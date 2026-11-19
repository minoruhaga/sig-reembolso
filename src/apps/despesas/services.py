from django.core.exceptions import ValidationError
from django.db import transaction

from apps.core.services import otimizar_comprovante_fiscal
from apps.despesas.models import Despesa, StatusDespesa


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
      vazamento de regras contábeis para views ou templates.
    """
    if despesa_existente:
        if despesa_existente.status not in (StatusDespesa.RASCUNHO, StatusDespesa.REJEITADO):
            raise ValidationError(
                f"RN05 (Imutabilidade Pós-Decisão): A despesa #{despesa_existente.id} está no estado "
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
