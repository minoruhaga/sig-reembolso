from decimal import ROUND_HALF_UP, Decimal

from apps.core.exceptions import PermissaoNegadaDominioError, SegregacaoFuncoesError

ZERO = Decimal('0.00')


def calcular_soft_block_rn02(valor: Decimal, saldo_disponivel: Decimal) -> tuple[bool, Decimal]:
    """
    Calcula o acionamento e o valor excedente do soft-block orçamentário (RN02).

    - O que faz: Determina se uma compra operacional ultrapassa o saldo disponível da coordenação e
      calcula com exatidão de centavos qual parcela corresponde ao estouro orçamentário.
    - Como faz: Compara `valor` com `saldo_disponivel` em `Decimal`; caso `valor > saldo_disponivel`,
      retorna `(True, valor)` quando `saldo_disponivel <= 0.00` (toda a nova despesa é excedente) ou
      `(True, valor - saldo_disponivel)` caso contrário; se couber no saldo, retorna `(False, 0.00)`.
    - Qual finalidade atende: Garante que compras urgentes em campo não sejam travadas pelo sistema,
      sinalizando exatamente o excesso financeiro à Tesouraria (RN02 / Issue #12).
    """
    valor_dec = (valor or ZERO).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    saldo_dec = (saldo_disponivel or ZERO).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    if valor_dec > saldo_dec:
        excedente = valor_dec if saldo_dec <= ZERO else (valor_dec - saldo_dec)
        return True, excedente.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    return False, ZERO


def avaliar_alerta_estouro_rn02(despesa) -> dict:
    """
    Produz o diagnóstico visual e contábil de estouro orçamentário para exibição na triagem (RN02).

    - O que faz: Consolida flag booleana `excede_teto`, `valor_excedente`, saldo atual da coordenação,
      classe CSS Bootstrap de destaque (`bg-danger` / `bg-success`) e texto informativo do alerta.
    - Como faz: Lê os atributos `excede_teto`, `valor_excedente` e `coordenacao.saldo_disponivel` da
      instância de `Despesa`, evitando cálculos ou condicionais duplicadas nos templates HTML.
    - Qual finalidade atende: Cumpre o critério da Issue #12 e `src/AGENTS.md` (destaque visual em
      vermelho gerado a partir da camada de domínio).
    """
    excede = bool(getattr(despesa, 'excede_teto', False))
    excedente = (getattr(despesa, 'valor_excedente', ZERO) or ZERO).quantize(
        Decimal('0.01'),
        rounding=ROUND_HALF_UP,
    )
    saldo_atual = despesa.coordenacao.saldo_disponivel if despesa.coordenacao_id else ZERO

    return {
        'excede_teto': excede,
        'valor_excedente': excedente,
        'saldo_disponivel': saldo_atual.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
        'classe_badge': 'bg-danger' if excede else 'bg-success',
        'texto_alerta': f"ESTOURO DE TETO (+R$ {excedente:.2f})" if excede else 'Dentro do Teto',
    }


def verificar_impedimento_rn03(despesa, usuario) -> bool:
    """
    Indica se o usuário avaliador está impedido pela Segregação de Funções de decidir sobre a despesa.

    - O que faz: Retorna `True` quando o operador é o próprio solicitante da despesa e não é superusuário.
    - Como faz: Compara `despesa.solicitante_id == getattr(usuario, 'id', None)` combinado com `not is_superuser`.
    - Qual finalidade atende: Permite que serviços, views e painéis da Tesouraria bloqueiem botões de
      auto-aprovação ou auto-liquidação com transparência (RN03).
    """
    if not usuario or not getattr(usuario, 'is_authenticated', True):
        return True
    return (
        despesa.solicitante_id == getattr(usuario, 'id', None)
        and not getattr(usuario, 'is_superuser', False)
    )


def validar_segregacao_funcoes_rn03(*, despesa, operador, acao: str) -> None:
    """
    Valida autorização de Tesouraria e Segregação de Funções antes de aprovar, rejeitar ou liquidar (RN03).

    - O que faz: Bloqueia operações financeiras executadas por não-tesoureiros ou pelo próprio solicitante.
    - Como faz: Verifica `getattr(operador, 'is_tesoureiro', False)` (lançando `PermissaoNegadaDominioError`)
      e invoca `verificar_impedimento_rn03(despesa, operador)` (lançando `SegregacaoFuncoesError` com
      mensagem contextualizada para a `acao` informada).
    - Qual finalidade atende: Centraliza a regra crítica RN03 em ponto único auditável, impedindo conflito
      de interesses em toda a máquina de estados da Tesouraria.
    """
    if not getattr(operador, 'is_tesoureiro', False):
        raise PermissaoNegadaDominioError(
            f"Apenas usuários com perfil de Tesouraria podem {acao} despesas."
        )

    if verificar_impedimento_rn03(despesa, operador):
        raise SegregacaoFuncoesError(
            f"O tesoureiro não pode {acao} a própria solicitação. Outro tesoureiro precisa fazer isso."
        )
