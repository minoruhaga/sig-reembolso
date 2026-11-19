from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.despesas.forms import DespesaForm
from apps.despesas.models import Despesa, StatusDespesa
from apps.despesas.services import criar_ou_atualizar_despesa


@login_required
def nova_despesa_view(request):
    """
    Controla o fluxo de submissão e gravação de rascunhos de despesas em campo.

    - O que faz: Exibe o formulário de cadastro de despesa, processa envios de novos gastos,
      valida a presença de comprovante para submissão imediata (RN01) e aciona a camada de serviço
      para otimização Pillow e registro transacional.
    - Como faz: Instancia `DespesaForm`; lê a intenção do usuário (`acao == 'submeter'` vs `'rascunho'`);
      se for submissão, exige comprovante no payload; invoca `criar_ou_atualizar_despesa` sob transação atômica;
      redireciona com mensagens de alerta/sucesso para a listagem do voluntário.
    - Qual finalidade atende: Atende aos requisitos RF04 (Lançamento de Despesa), RF05 (Gestão de Rascunhos)
      e RNF01/RNF02 (submissão mobile ágil com fotos compactadas).
    """
    if request.method == 'POST':
        form = DespesaForm(request.POST, request.FILES)
        acao = request.POST.get('acao', 'submeter')
        submeter_agora = (acao == 'submeter')
        comprovante_upload = request.FILES.get('comprovante')

        if submeter_agora and not comprovante_upload:
            form.add_error(
                'comprovante',
                'RN01: O comprovante fiscal é estritamente obrigatório para enviar a despesa à triagem.'
            )

        if form.is_valid():
            try:
                despesa = criar_ou_atualizar_despesa(
                    usuario=request.user,
                    dados_validados=form.cleaned_data,
                    comprovante_upload=comprovante_upload,
                    submeter_agora=submeter_agora,
                )

                if submeter_agora:
                    if despesa.excede_teto:
                        messages.warning(
                            request,
                            f"Despesa #{despesa.id} enviada com sucesso! ATENÇÃO: Esta compra excedeu o teto "
                            f"da coordenação {despesa.coordenacao.sigla} em R$ {despesa.valor_excedente} "
                            "(Soft-block RN02) e demandará deliberação especial da Tesouraria."
                        )
                    else:
                        messages.success(
                            request,
                            f"Despesa #{despesa.id} enviada com sucesso para a fila de triagem da Tesouraria!"
                        )
                else:
                    messages.info(
                        request,
                        f"Rascunho da despesa #{despesa.id} salvo com sucesso. Você pode editá-la e anexar o "
                        "comprovante antes do envio formal."
                    )
                return redirect('despesas:minhas')

            except ValidationError as e:
                msg_erro = e.message if hasattr(e, 'message') else str(e)
                form.add_error(None, msg_erro)
    else:
        form = DespesaForm(initial={'data_despesa': timezone.now().date()})

    return render(request, 'despesas/despesa_form.html', {
        'form': form,
        'titulo_pagina': 'Nova Despesa (Campo)',
        'modo_edicao': False,
    })


@login_required
def editar_despesa_view(request, pk):
    """
    Permite alterar dados e anexar comprovantes em despesas no estado RASCUNHO ou REJEITADO.

    - O que faz: Carrega uma despesa existente para complementação ou correção de pendências apontadas
      pela Tesouraria, impedindo a edição de despesas já aprovadas ou pagas (RN05).
    - Como faz: Consulta a despesa por PK; verifica se o usuário logado é o solicitante ou membro da gestão;
      avalia `despesa.status in (RASCUNHO, REJEITADO)`; processa o formulário atualizando os campos e o
      arquivo através de `criar_ou_atualizar_despesa`; redireciona para a listagem com feedback.
    - Qual finalidade atende: Cumpre a RN04 e RN05, possibilitando o ciclo de correção de notas reprovadas
      e protegendo contra fraude ou adulteração após a tomada de decisão contábil.
    """
    despesa = get_object_or_404(Despesa, pk=pk)

    # Apenas o solicitante original ou membros da tesouraria/administração podem editar
    if despesa.solicitante_id != request.user.id and not request.user.is_tesoureiro:
        raise PermissionDenied("Você não tem autorização para editar uma despesa solicitada por outro usuário.")

    # RN05: Bloqueio estrito de edição pós-decisão
    if despesa.status not in (StatusDespesa.RASCUNHO, StatusDespesa.REJEITADO):
        messages.error(
            request,
            f"RN05 (Imutabilidade Pós-Decisão): Despesas no estado '{despesa.get_status_display()}' "
            "não podem ser modificadas."
        )
        return redirect('despesas:minhas')

    if request.method == 'POST':
        form = DespesaForm(request.POST, request.FILES, instance=despesa)
        acao = request.POST.get('acao', 'submeter')
        submeter_agora = (acao == 'submeter')
        comprovante_upload = request.FILES.get('comprovante')

        if submeter_agora and not comprovante_upload and not despesa.comprovante:
            form.add_error(
                'comprovante',
                'RN01: O comprovante fiscal é obrigatório para submeter a despesa à triagem.'
            )

        if form.is_valid():
            try:
                despesa = criar_ou_atualizar_despesa(
                    usuario=request.user,
                    dados_validados=form.cleaned_data,
                    comprovante_upload=comprovante_upload,
                    despesa_existente=despesa,
                    submeter_agora=submeter_agora,
                )

                if submeter_agora:
                    if despesa.excede_teto:
                        messages.warning(
                            request,
                            f"Despesa #{despesa.id} reenviada com alerta de estouro de teto (+R$ {despesa.valor_excedente})."
                        )
                    else:
                        messages.success(
                            request,
                            f"Despesa #{despesa.id} reenviada com sucesso para a triagem da Tesouraria!"
                        )
                else:
                    messages.info(
                        request,
                        f"Alterações na despesa #{despesa.id} salvas em rascunho com sucesso."
                    )
                return redirect('despesas:minhas')

            except ValidationError as e:
                msg_erro = e.message if hasattr(e, 'message') else str(e)
                form.add_error(None, msg_erro)
    else:
        form = DespesaForm(instance=despesa)

    return render(request, 'despesas/despesa_form.html', {
        'form': form,
        'despesa': despesa,
        'titulo_pagina': f'Editar Despesa #{despesa.id}',
        'modo_edicao': True,
    })


@login_required
@require_POST
def submeter_despesa_view(request, pk):
    """
    Submete diretamente um rascunho existente que já possua comprovante fiscal anexado.

    - O que faz: Promove a despesa de RASCUNHO para ENVIADO com um único clique a partir da listagem.
    - Como faz: Localiza a despesa por PK; valida a permissão do solicitante; invoca `despesa.submeter(request.user)`
      sob transação atômica; captura eventuais exceções de RN01 ou RN02 e redireciona com mensagem informativa.
    - Qual finalidade atende: Oferece atalho rápido de campo para voluntários que salvaram o rascunho
      previamente e desejam transmitir o lote quando entram na área de cobertura Wi-Fi Starlink.
    """
    despesa = get_object_or_404(Despesa, pk=pk)

    if despesa.solicitante_id != request.user.id and not request.user.is_tesoureiro:
        raise PermissionDenied("Você não tem autorização para submeter despesas de outro usuário.")

    try:
        despesa.submeter(request.user)
        if despesa.excede_teto:
            messages.warning(
                request,
                f"Despesa #{despesa.id} enviada com alerta de estouro (+R$ {despesa.valor_excedente})!"
            )
        else:
            messages.success(request, f"Despesa #{despesa.id} submetida para triagem com sucesso!")
    except ValidationError as e:
        messages.error(request, f"Erro ao submeter: {e.message if hasattr(e, 'message') else str(e)}")

    return redirect('despesas:minhas')


@login_required
def minhas_despesas_view(request):
    """
    Exibe a listagem consolidada de todas as despesas lançadas pelo voluntário logado.

    - O que faz: Apresenta o histórico pessoal de solicitações de reembolso com status, valores,
      alertas de estouro de teto, motivos de eventuais reprovações e botões de ação rápida.
    - Como faz: Executa query otimizada com `select_related('coordenacao')` filtrada pelo `request.user`;
      ordena cronologicamente de forma decrescente para priorizar os lançamentos mais recentes.
    - Qual finalidade atende: Atende ao requisito RF01 e RF04, proporcionando transparência e controle
      operacional direto ao voluntário em campo sobre seus reembolsos no AG VII.
    """
    despesas = Despesa.objects.filter(
        solicitante=request.user
    ).select_related('coordenacao').order_by('-criado_em')

    return render(request, 'despesas/minhas_despesas.html', {
        'despesas': despesas,
    })
