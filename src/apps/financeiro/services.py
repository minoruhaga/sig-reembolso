from decimal import ROUND_HALF_UP, Decimal

from django.db import transaction
from django.db.models import DecimalField, Q, Sum
from django.db.models.functions import Coalesce

from apps.core.exceptions import PermissaoNegadaDominioError, SigReembolsoDomainError
from apps.despesas.models import StatusDespesa
from apps.financeiro.models import Coordenacao
from apps.usuarios.services import coordenacoes_visiveis

ZERO = Decimal('0.00')
CEM = Decimal('100.0')


def _quantizar_moeda(valor: Decimal) -> Decimal:
    """
    Normaliza um valor `Decimal` para exatamente duas casas decimais.

    - O que faz: Padroniza montantes financeiros em Reais com precisão de centavos.
    - Como faz: Executa `valor.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)`.
    - Qual finalidade atende: Garante consistência contábil em somatórios e respostas JSON (RF03).
    """
    return (valor or ZERO).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def _montar_indicador_coordenacao(
    coordenacao: Coordenacao,
    *,
    total_pago: Decimal,
    total_aprovado: Decimal,
    total_enviado: Decimal,
) -> dict:
    """
    Constrói o dicionário consolidado do termômetro orçamentário para uma coordenação.

    - O que faz: Combina o teto aprovado com os montantes pagos, aprovados e em triagem, apurando saldo
      disponível, percentual real, percentual visual (0–100%), estado de estouro e nível de alerta Bootstrap.
    - Como faz: Opera exclusivamente com aritmética `Decimal`; calcula `total_comprometido` e
      `saldo_disponivel = teto_orcamentario - total_comprometido` e classifica o nível visual (> 90% ou estouro -> `danger`).
    - Qual finalidade atende: Centraliza a regra de cálculo do termômetro financeiro (RF03) sem duplicação de código.
    """
    teto = _quantizar_moeda(coordenacao.teto_orcamentario)
    pago = _quantizar_moeda(total_pago)
    aprovado = _quantizar_moeda(total_aprovado)
    enviado = _quantizar_moeda(total_enviado)
    comprometido = _quantizar_moeda(pago + aprovado + enviado)
    saldo = _quantizar_moeda(teto - comprometido)

    if teto > ZERO:
        pct_real_dec = ((comprometido / teto) * CEM).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)
        pct_barra_dec = min(pct_real_dec, CEM)
    else:
        pct_real_dec = Decimal('100.0') if comprometido > ZERO else Decimal('0.0')
        pct_barra_dec = pct_real_dec

    em_estouro = saldo < ZERO
    if em_estouro or pct_real_dec > Decimal('90.0'):
        nivel_alerta = 'danger'
    elif pct_real_dec > Decimal('60.0'):
        nivel_alerta = 'warning'
    else:
        nivel_alerta = 'success'

    return {
        'id': coordenacao.id,
        'sigla': coordenacao.sigla,
        'nome': coordenacao.nome,
        'descricao': coordenacao.descricao,
        'teto_orcamentario': teto,
        'total_pago': pago,
        'total_aprovado': aprovado,
        'total_enviado': enviado,
        'total_comprometido': comprometido,
        'saldo_disponivel': saldo,
        'percentual_real': float(pct_real_dec),
        'percentual_consumido': float(pct_barra_dec),
        'em_estouro': em_estouro,
        'nivel_alerta': nivel_alerta,
    }


def calcular_termometro_coordenacao(coordenacao: Coordenacao) -> dict:
    """
    Apura em tempo real os indicadores orçamentários individuais de uma coordenação.

    - O que faz: Agrega no banco os totais em `PAGO`, `APROVADO` e `ENVIADO` da pasta e gera seu termômetro.
    - Como faz: Executa `aggregate` com filtros condicionais `Q` e `Coalesce(..., ZERO)` em `DecimalField`
      e delega a montagem do payload a `_montar_indicador_coordenacao`.
    - Qual finalidade atende: Fornece leitura isolada de saldo e consumo para formulários ou APIs pontuais (RF03).
    """
    campo_decimal = DecimalField(max_digits=12, decimal_places=2)
    agregados = coordenacao.despesas.aggregate(
        pago=Coalesce(Sum('valor', filter=Q(status=StatusDespesa.PAGO)), ZERO, output_field=campo_decimal),
        aprovado=Coalesce(Sum('valor', filter=Q(status=StatusDespesa.APROVADO)), ZERO, output_field=campo_decimal),
        enviado=Coalesce(Sum('valor', filter=Q(status=StatusDespesa.ENVIADO)), ZERO, output_field=campo_decimal),
    )
    return _montar_indicador_coordenacao(
        coordenacao,
        total_pago=agregados['pago'],
        total_aprovado=agregados['aprovado'],
        total_enviado=agregados['enviado'],
    )


def obter_resumo_orcamentario(usuario, sigla: str | None = None) -> dict:
    """
    Calcula o painel consolidado de tetos, comprometimentos e saldos livres no recorte RBAC do usuário.

    - O que faz: Retorna a lista de termômetros das coordenações visíveis ao usuário (com filtro opcional
      por sigla) e os totalizadores globais em `Decimal`.
    - Como faz: Parte do queryset autorizado por `coordenacoes_visiveis(usuario)`, anota os somatórios por
      status em uma única consulta SQL (`annotate`) para evitar queries N+1 e soma os resultados em `Decimal`.
    - Qual finalidade atende: Atende aos requisitos RF01 e RF03, mantendo precisão de centavos e resposta < 1,5 s (RNF05).
    """
    campo_decimal = DecimalField(max_digits=12, decimal_places=2)
    queryset = coordenacoes_visiveis(usuario)
    if sigla:
        queryset = queryset.filter(sigla__iexact=sigla.strip())

    coordenacoes_anotadas = queryset.annotate(
        agg_pago=Coalesce(Sum('despesas__valor', filter=Q(despesas__status=StatusDespesa.PAGO)), ZERO, output_field=campo_decimal),
        agg_aprovado=Coalesce(Sum('despesas__valor', filter=Q(despesas__status=StatusDespesa.APROVADO)), ZERO, output_field=campo_decimal),
        agg_enviado=Coalesce(Sum('despesas__valor', filter=Q(despesas__status=StatusDespesa.ENVIADO)), ZERO, output_field=campo_decimal),
    )

    itens = [
        _montar_indicador_coordenacao(
            coord,
            total_pago=coord.agg_pago,
            total_aprovado=coord.agg_aprovado,
            total_enviado=coord.agg_enviado,
        )
        for coord in coordenacoes_anotadas
    ]

    total_orcado = _quantizar_moeda(sum((item['teto_orcamentario'] for item in itens), start=ZERO))
    total_pago = _quantizar_moeda(sum((item['total_pago'] for item in itens), start=ZERO))
    total_aprovado = _quantizar_moeda(sum((item['total_aprovado'] for item in itens), start=ZERO))
    total_enviado = _quantizar_moeda(sum((item['total_enviado'] for item in itens), start=ZERO))
    total_comprometido = _quantizar_moeda(sum((item['total_comprometido'] for item in itens), start=ZERO))
    total_saldo_livre = _quantizar_moeda(total_orcado - total_comprometido)

    if total_orcado > ZERO:
        pct_global = float(((total_comprometido / total_orcado) * CEM).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
    else:
        pct_global = 0.0

    return {
        'coordenacoes': itens,
        'totais': {
            'total_orcado': total_orcado,
            'total_pago': total_pago,
            'total_aprovado': total_aprovado,
            'total_enviado': total_enviado,
            'total_comprometido': total_comprometido,
            'total_saldo_livre': total_saldo_livre,
            'percentual_consumido': min(pct_global, 100.0),
            'percentual_real': pct_global,
        },
    }


@transaction.atomic
def atualizar_teto_orcamentario(*, usuario, coordenacao: Coordenacao, novo_teto: Decimal) -> Coordenacao:
    """
    Atualiza de forma atômica e autorizada o teto orçamentário de uma coordenação operacional (RF02).

    - O que faz: Altera o campo `teto_orcamentario` da coordenação mediante validação de papel e valor válido.
    - Como faz: Protegido por `@transaction.atomic`; valida se `usuario` é Tesoureiro ou Admin Geral
      (lançando `PermissaoNegadaDominioError` caso contrário); garante `novo_teto >= 0.00` em `Decimal`
      (lançando `SigReembolsoDomainError` caso negativo) e persiste com `update_fields=['teto_orcamentario']`.
    - Qual finalidade atende: Cumpre o requisito RF02 (parametrização de tetos das 15 coordenações pela Tesouraria).
    """
    if not (getattr(usuario, 'is_tesoureiro', False) or getattr(usuario, 'is_admin_geral', False)):
        raise PermissaoNegadaDominioError(
            "Apenas membros da Tesouraria ou Administração Geral podem alterar tetos orçamentários."
        )

    if not isinstance(novo_teto, Decimal):
        raise SigReembolsoDomainError("O teto orçamentário deve ser informado como Decimal exato.")

    teto_quantizado = _quantizar_moeda(novo_teto)
    if teto_quantizado < ZERO:
        raise SigReembolsoDomainError("O teto orçamentário não pode ser negativo.")

    coordenacao.teto_orcamentario = teto_quantizado
    coordenacao.save(update_fields=['teto_orcamentario'])
    return coordenacao
