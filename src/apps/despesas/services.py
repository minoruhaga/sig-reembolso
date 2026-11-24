from decimal import ROUND_HALF_UP, Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.core.exceptions import ComprovanteObrigatorioError, PermissaoNegadaDominioError
from apps.core.services import otimizar_comprovante_fiscal
from apps.despesas.models import Despesa, StatusDespesa
from apps.despesas.regras import calcular_soft_block_rn02

ZERO = Decimal('0.00')
CEM = Decimal('100')


def _percentual_da_barra(parte: Decimal, total: Decimal) -> float:
    """
    Converte uma fração monetária do teto em largura percentual de barra visual.

    - O que faz: Retorna quanto `parte` representa de `total`, limitado ao intervalo 0–100.
    - Como faz: Divide em `Decimal`, quantiza com uma casa decimal e só converte para `float` no fim,
      pois o resultado serve apenas como largura CSS (nunca é usado em contas em R$).
    - Qual finalidade atende: Alimenta o termômetro da tela mobile (RF03) sem expor aritmética ao template.
    """
    if total <= ZERO or parte <= ZERO:
        return 0.0
    pct = ((parte / total) * CEM).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)
    return float(min(pct, CEM))


def simular_impacto_orcamentario(*, usuario, coordenacao_id, valor: Decimal | None) -> dict | None:
    """
    Projeta o efeito de uma compra ainda não enviada sobre o saldo da coordenação.

    - O que faz: Para uma coordenação visível ao usuário, devolve teto, comprometido, saldo atual, saldo após
      a compra, sinalização de estouro (RN02) e as larguras da barra do termômetro (comprometido e compra).
    - Como faz: Restringe a busca a `coordenacoes_visiveis(usuario)` (RBAC); lê o termômetro oficial via
      `calcular_termometro_coordenacao`; aplica a mesma regra de soft-block usada na submissão
      (`calcular_soft_block_rn02`), tudo em `Decimal`. Nada é gravado: é uma leitura.
    - Qual finalidade atende: Mostra ao voluntário em campo, antes de enviar, se a compra cabe na verba da
      pasta (RF03/RNF01) sem bloquear o envio (RN02 é soft-block), mantendo o cálculo fora de views e templates.
      Retorna `None` quando a coordenação não existe ou não é visível ao usuário.
    """
    from apps.financeiro.services import calcular_termometro_coordenacao
    from apps.usuarios.services import coordenacoes_visiveis

    try:
        coordenacao_pk = int(coordenacao_id)
    except (TypeError, ValueError):
        return None

    coordenacao = coordenacoes_visiveis(usuario).filter(pk=coordenacao_pk).first()
    if coordenacao is None:
        return None

    termometro = calcular_termometro_coordenacao(coordenacao)
    teto = termometro['teto_orcamentario']
    comprometido = termometro['total_comprometido']
    saldo_atual = termometro['saldo_disponivel']
    valor_dec = (valor if valor is not None and valor > ZERO else ZERO).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP
    )

    if valor_dec > ZERO:
        excede_teto, valor_excedente = calcular_soft_block_rn02(valor_dec, saldo_atual)
    else:
        excede_teto, valor_excedente = False, ZERO
    espaco_livre = max(teto - comprometido, ZERO)

    return {
        'coordenacao_id': coordenacao.id,
        'sigla': coordenacao.sigla,
        'nome': coordenacao.nome,
        'teto': teto,
        'comprometido': comprometido,
        'saldo_atual': saldo_atual,
        'valor': valor_dec,
        'saldo_apos': saldo_atual - valor_dec,
        'excede_teto': excede_teto,
        'valor_excedente': valor_excedente,
        'pct_comprometido': _percentual_da_barra(comprometido, teto),
        'pct_compra': _percentual_da_barra(min(valor_dec, espaco_livre), teto),
    }


@transaction.atomic
def criar_ou_atualizar_despesa(
    *,
    usuario,
    dados_validados,
    comprovante_upload=None,
    despesa_existente=None,
    submeter_agora=True
) -> Despesa:
    """
    Orquestra a criação, edição e submissão transacional de despesas com compressão de comprovante.

    - O que faz: Persiste lançamentos de despesas de voluntários de campo, processa uploads de cupom
      fiscal através da rotina de otimização Pillow (< 350KB e UUID v4), aplica as travas de imutabilidade
      pós-decisão (RN05) para despesas já aprovadas/pagas e aciona a máquina de estados para submissão
      à triagem (RN01, RN02 e RN06) ou arquivamento temporário em rascunho (RF05).
    - Como faz: Opera integralmente sob a proteção atômica `@transaction.atomic`; caso haja `despesa_existente`,
      valida se o status pertence a `(RASCUNHO, REJEITADO)` antes de mutar qualquer campo; caso um novo arquivo
      de cupom seja anexado, delega a validação de formato e compressão para `otimizar_comprovante_fiscal`;
      por fim, se `submeter_agora=True`, invoca o método de domínio `despesa.submeter(usuario)` para cômputo
      do soft-block e registro da trilha imutável de auditoria.
    - Qual finalidade atende: Cumpre as regras de integridade arquitetural do SIG-Reembolso (src/AGENTS.md),
      centralizando as operações de domínio e manipulação de mídia em camada de serviço testável, impedindo
      vazamento de regras contábeis para views ou templates e bloqueando lançamentos fora do escopo RBAC.
    """
    from apps.usuarios.services import coordenacoes_visiveis

    coordenacao_alvo = dados_validados.get('coordenacao')
    if coordenacao_alvo is None and despesa_existente is not None:
        coordenacao_alvo = despesa_existente.coordenacao
    if coordenacao_alvo is not None:
        coordenacao_id = getattr(coordenacao_alvo, 'pk', coordenacao_alvo)
        if not coordenacoes_visiveis(usuario).filter(pk=coordenacao_id).exists():
            raise PermissaoNegadaDominioError(
                "Você não tem permissão para lançar ou editar despesas nesta coordenação."
            )

    if despesa_existente:
        if despesa_existente.status not in (StatusDespesa.RASCUNHO, StatusDespesa.REJEITADO):
            raise ValidationError(
                f"A despesa #{despesa_existente.id} está no estado "
                f"'{despesa_existente.get_status_display()}' e não pode ser editada."
            )

        despesa = despesa_existente
        status_original = despesa.status

        for campo, valor in dados_validados.items():
            if campo != 'comprovante':
                setattr(despesa, campo, valor)

        if comprovante_upload:
            despesa.comprovante = otimizar_comprovante_fiscal(comprovante_upload)

        if status_original == StatusDespesa.REJEITADO and not submeter_agora:
            despesa.status = StatusDespesa.RASCUNHO
            despesa.save()
            despesa._registrar_transicao(
                StatusDespesa.REJEITADO,
                StatusDespesa.RASCUNHO,
                usuario,
                "Despesa reaberta como rascunho para correção"
            )
        else:
            despesa.save()

    else:
        dados = dict(dados_validados)
        if comprovante_upload:
            dados['comprovante'] = otimizar_comprovante_fiscal(comprovante_upload)

        dados['solicitante'] = usuario
        dados['status'] = StatusDespesa.RASCUNHO
        despesa = Despesa.objects.create(**dados)
        despesa._registrar_transicao(
            '',
            StatusDespesa.RASCUNHO,
            usuario,
            "Criação da despesa pelo formulário"
        )

    if submeter_agora:
        despesa.submeter(usuario)

    return despesa


def listar_despesas_triagem(status_filtro: str | None = None, coordenacao_id: int | str | None = None):
    """
    Consulta as despesas da fila operacional de triagem e liquidação da Tesouraria.

    - O que faz: Retorna o queryset otimizado das despesas ordenadas por prioridade (estouros e envio),
      com filtros opcionais por status e coordenação.
    - Como faz: Aplica `select_related('coordenacao', 'solicitante', 'analisado_por', 'pago_por')`; quando
      `status_filtro` é omitido ou `'PENDENTES'`, filtra por `[ENVIADO, APROVADO]`; caso contrário, filtra
      pelo status exato (exceto `'TODAS'`).
    - Qual finalidade atende: Sustenta o Painel de Triagem da Tesouraria (RF06/RF07) garantindo baixa latência (RNF05).
    """
    queryset = Despesa.objects.select_related(
        'coordenacao',
        'solicitante',
        'analisado_por',
        'pago_por',
    ).order_by('-excede_teto', '-criado_em')

    if not status_filtro or status_filtro == 'PENDENTES':
        queryset = queryset.filter(status__in=[StatusDespesa.ENVIADO, StatusDespesa.APROVADO])
    elif status_filtro != 'TODAS':
        queryset = queryset.filter(status=status_filtro)

    if coordenacao_id:
        queryset = queryset.filter(coordenacao_id=coordenacao_id)

    return queryset


@transaction.atomic
def aprovar_despesa_triagem(*, despesa: Despesa, tesoureiro, observacao: str = '') -> Despesa:
    """
    Executa a aprovação transacional de uma despesa na fila de triagem da Tesouraria.

    - O que faz: Valida perfil de Tesouraria e delega a transição `ENVIADO -> APROVADO` ao domínio.
    - Como faz: Opera sob `@transaction.atomic`, checa `is_tesoureiro` e invoca `despesa.aprovar(...)`.
    - Qual finalidade atende: Cumpre RF06, RN03 (segregação de funções) e RN06 (auditoria imutável).
    """
    if not getattr(tesoureiro, 'is_tesoureiro', False):
        raise PermissaoNegadaDominioError("Apenas usuários com perfil de Tesouraria podem aprovar despesas.")

    despesa.aprovar(tesoureiro, observacao=observacao)
    return despesa


@transaction.atomic
def rejeitar_despesa_triagem(*, despesa: Despesa, tesoureiro, motivo: str) -> Despesa:
    """
    Executa a reprovação transacional de uma despesa mediante justificativa obrigatória (RN04).

    - O que faz: Valida perfil de Tesouraria e transiciona a despesa para `REJEITADO` com parecer formal.
    - Como faz: Opera sob `@transaction.atomic`, checa `is_tesoureiro` e invoca `despesa.rejeitar(tesoureiro, motivo)`.
    - Qual finalidade atende: Cumpre RF06, RN03 e RN04, liberando o saldo comprometido e instruindo o solicitante.
    """
    if not getattr(tesoureiro, 'is_tesoureiro', False):
        raise PermissaoNegadaDominioError("Apenas usuários com perfil de Tesouraria podem reprovar despesas.")

    despesa.rejeitar(tesoureiro, motivo=motivo)
    return despesa


@transaction.atomic
def liquidar_despesa_triagem(*, despesa: Despesa, tesoureiro, comprovante_pagamento) -> Despesa:
    """
    Liquida uma despesa aprovada anexando e otimizando o comprovante de transferência do Banco Cora PJ.

    - O que faz: Exige anexo bancário válido, comprime/anonimiza com Pillow (`RNF02`/`RNF04`) e conclui
      a transição `APROVADO -> PAGO`.
    - Como faz: Opera sob `@transaction.atomic`; valida perfil `is_tesoureiro` e presença de
      `comprovante_pagamento`; processa via `otimizar_comprovante_fiscal`; chama `despesa.liquidar(...)`.
    - Qual finalidade atende: Atende ao requisito RF07 e critérios da Issue #11 com lastro bancário auditável.
    """
    if not getattr(tesoureiro, 'is_tesoureiro', False):
        raise PermissaoNegadaDominioError("Apenas usuários com perfil de Tesouraria podem liquidar despesas.")

    if not comprovante_pagamento:
        raise ComprovanteObrigatorioError(
            "É obrigatório anexar o comprovante de transferência do Banco Cora PJ para liquidar o reembolso."
        )

    comprovante_otimizado = otimizar_comprovante_fiscal(comprovante_pagamento)
    despesa.liquidar(tesoureiro, comprovante_pagamento=comprovante_otimizado)
    return despesa
