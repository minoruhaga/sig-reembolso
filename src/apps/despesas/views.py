import mimetypes

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.decorators.http import require_GET, require_POST

from apps.core.exceptions import PermissaoNegadaDominioError
from apps.despesas.forms import (
    DespesaForm,
    LiquidacaoDespesaForm,
    RejeicaoDespesaForm,
    converter_valor_reais,
)
from apps.despesas.models import Despesa, StatusDespesa
from apps.despesas.regras import verificar_impedimento_rn03
from apps.despesas.services import (
    aprovar_despesa_triagem,
    criar_ou_atualizar_despesa,
    liquidar_despesa_triagem,
    listar_despesas_triagem,
    rejeitar_despesa_triagem,
    simular_impacto_orcamentario,
)
from apps.financeiro.models import Coordenacao
from apps.usuarios.services import usuario_pode_acessar_painel_auditoria


def _previa_inicial(request, form):
    """
    Calcula a prévia do termômetro exibida no primeiro carregamento do formulário de despesa.

    - O que faz: Descobre a coordenação e o valor já presentes no formulário (dados enviados, instância
      ou valores iniciais) e pede ao serviço de domínio a projeção do saldo.
    - Como faz: Lê `form['coordenacao'].value()` e `form['valor'].value()`, converte o valor em reais com
      `converter_valor_reais` (formato "1.250,40"), ignorando entradas inválidas, e delega todo o cálculo a `simular_impacto_orcamentario`.
    - Qual finalidade atende: Faz o termômetro funcionar mesmo sem JavaScript ou em conexão lenta (RNF01),
      mantendo a view apenas como orquestradora.
    """
    coordenacao_id = form['coordenacao'].value()
    if not coordenacao_id:
        return None
    valor = converter_valor_reais(form['valor'].value())
    return simular_impacto_orcamentario(
        usuario=request.user, coordenacao_id=coordenacao_id, valor=valor
    )


@login_required
@require_GET
def previa_orcamento_view(request):
    """
    Devolve em JSON a projeção do saldo da coordenação para uma compra ainda não enviada.

    - O que faz: Responde ao termômetro da tela mobile com saldo atual, saldo após a compra e sinal de
      estouro (RN02), sem gravar nada.
    - Como faz: Lê `coordenacao` e `valor` (formato "1.250,40" da máscara) da query string, converte com
      `converter_valor_reais`, chama
      `simular_impacto_orcamentario` (que aplica o recorte RBAC) e serializa os montantes como strings
      com duas casas; responde 404 para coordenação inexistente ou fora do escopo do usuário.
    - Qual finalidade atende: Permite ao voluntário ver, enquanto digita o valor em campo, se a compra cabe
      na verba da pasta (RF03 / RNF01), com payload pequeno para a rede Starlink.
    """
    texto_valor = request.GET.get('valor') or '0'
    valor = converter_valor_reais(texto_valor)
    if valor is None:
        return JsonResponse({'erro': 'Valor inválido.'}, status=400)

    previa = simular_impacto_orcamentario(
        usuario=request.user,
        coordenacao_id=request.GET.get('coordenacao'),
        valor=valor,
    )
    if previa is None:
        return JsonResponse({'erro': 'Coordenação não encontrada.'}, status=404)

    dados = dict(previa)
    for campo in ('teto', 'comprometido', 'saldo_atual', 'valor', 'saldo_apos', 'valor_excedente'):
        dados[campo] = f"{previa[campo]:.2f}"
    return JsonResponse(dados)



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
        form = DespesaForm(request.POST, request.FILES, usuario=request.user)
        acao = request.POST.get('acao', 'submeter')
        submeter_agora = (acao == 'submeter')
        comprovante_upload = request.FILES.get('comprovante')

        if submeter_agora and not comprovante_upload:
            form.add_error(
                'comprovante',
                'Anexe a foto ou o PDF da NF ou recibo para enviar a despesa à tesouraria.'
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
                            f"Despesa #{despesa.id} enviada. Ela passa do teto da coordenação "
                            f"{despesa.coordenacao.sigla} em R$ {despesa.valor_excedente}; a tesouraria vai "
                            "decidir se libera a verba extra."
                        )
                    else:
                        messages.success(
                            request,
                            f"Despesa #{despesa.id} enviada para a tesouraria."
                        )
                else:
                    messages.info(
                        request,
                        f"Rascunho #{despesa.id} salvo. Você pode voltar depois para anexar a foto da NF ou "
                        "recibo e enviar."
                    )
                return redirect('despesas:minhas')

            except PermissaoNegadaDominioError as exc:
                raise PermissionDenied(str(exc)) from exc
            except ValidationError as e:
                msg_erro = e.message if hasattr(e, 'message') else str(e)
                form.add_error(None, msg_erro)
    else:
        form = DespesaForm(
            initial={
                'data_despesa': timezone.now().date(),
                'coordenacao': request.user.coordenacao_id,
            },
            usuario=request.user,
        )

    return render(request, 'despesas/despesa_form.html', {
        'form': form,
        'titulo_pagina': 'Nova despesa',
        'modo_edicao': False,
        'previa': _previa_inicial(request, form),
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
            f"Despesas no estado '{despesa.get_status_display()}' não podem mais ser alteradas."
        )
        return redirect('despesas:minhas')

    if request.method == 'POST':
        form = DespesaForm(request.POST, request.FILES, instance=despesa, usuario=request.user)
        acao = request.POST.get('acao', 'submeter')
        submeter_agora = (acao == 'submeter')
        comprovante_upload = request.FILES.get('comprovante')

        if submeter_agora and not comprovante_upload and not despesa.comprovante:
            form.add_error(
                'comprovante',
                'Anexe a foto ou o PDF da NF ou recibo para enviar a despesa à tesouraria.'
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
                            f"Despesa #{despesa.id} reenviada. Ela passa do teto da coordenação "
                            f"{despesa.coordenacao.sigla} em R$ {despesa.valor_excedente}; a tesouraria vai "
                            "decidir se libera a verba extra."
                        )
                    else:
                        messages.success(
                            request,
                            f"Despesa #{despesa.id} reenviada para a tesouraria."
                        )
                else:
                    messages.info(
                        request,
                        f"Alterações salvas no rascunho #{despesa.id}."
                    )
                return redirect('despesas:minhas')

            except PermissaoNegadaDominioError as exc:
                raise PermissionDenied(str(exc)) from exc
            except ValidationError as e:
                msg_erro = e.message if hasattr(e, 'message') else str(e)
                form.add_error(None, msg_erro)
    else:
        form = DespesaForm(instance=despesa, usuario=request.user)

    return render(request, 'despesas/despesa_form.html', {
        'form': form,
        'despesa': despesa,
        'titulo_pagina': f'Despesa #{despesa.id}',
        'modo_edicao': True,
        'previa': _previa_inicial(request, form),
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
                f"Despesa #{despesa.id} enviada. Ela passa do teto da coordenação "
                f"{despesa.coordenacao.sigla} em R$ {despesa.valor_excedente}; a tesouraria vai "
                "decidir se libera a verba extra."
            )
        else:
            messages.success(request, f"Despesa #{despesa.id} enviada para a tesouraria.")
    except ValidationError as e:
        messages.error(request, f"Não foi possível enviar: {e.message if hasattr(e, 'message') else str(e)}")

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


def _extrair_mensagem_erro(exc: ValidationError) -> str:
    """
    Extrai mensagem legível de uma exceção `ValidationError` do Django.

    - O que faz: Converte mensagens simples ou listas de erros em texto único para feedback na UI.
    - Como faz: Verifica `exc.messages` ou `exc.message`, concatenando quando necessário.
    - Qual finalidade atende: Padroniza a exibição de alertas de regras RN01–RN06 nas views da Tesouraria.
    """
    if hasattr(exc, 'messages') and exc.messages:
        return ' '.join(str(m) for m in exc.messages)
    if hasattr(exc, 'message'):
        return str(exc.message)
    return str(exc)


@login_required
def painel_triagem_view(request):
    """
    Exibe o painel de auditoria da Tesouraria em cards, com modal de zoom da NF ou recibo (RF06, RF07, Issue #13).

    - O que faz: Lista despesas pendentes de aprovação (`ENVIADO`) e pagamento (`APROVADO`) em cards com
      badges de status e de estouro, filtragem por status e coordenação e ações rápidas de aprovar, rejeitar
      e liquidar dentro do modal de conferência.
    - Como faz: Libera o acesso somente quando `usuario_pode_acessar_painel_auditoria` aprova (Tesoureiro ou
      superusuário; Administrador Geral e Coordenador recebem 403); delega a consulta a
      `listar_despesas_triagem`; marca em cada despesa o impedimento de segregação de funções calculado por
      `verificar_impedimento_rn03`, para o template só esconder os botões; prepara os formulários dos modais.
    - Qual finalidade atende: Dá à auditoria da Tesouraria uma conferência rápida e nítida dos cupons sem
      expor o painel a quem não audita as contas do AG VII.
    """
    if not usuario_pode_acessar_painel_auditoria(request.user):
        raise PermissionDenied("Apenas a Tesouraria pode acessar o painel de auditoria.")

    status_filtro = request.GET.get('status', 'PENDENTES')
    coordenacao_id = request.GET.get('coordenacao')
    despesas = list(listar_despesas_triagem(status_filtro=status_filtro, coordenacao_id=coordenacao_id))
    for despesa in despesas:
        despesa.impedido_rn03 = verificar_impedimento_rn03(despesa, request.user)

    return render(request, 'despesas/painel_triagem.html', {
        'despesas': despesas,
        'coordenacoes': Coordenacao.objects.filter(ativo=True).order_by('nome'),
        'status_filtro': status_filtro,
        'coordenacao_filtro': str(coordenacao_id or ''),
        'rejeicao_form': RejeicaoDespesaForm(),
        'liquidacao_form': LiquidacaoDespesaForm(),
        'qtd_enviadas': sum(1 for d in despesas if d.status == StatusDespesa.ENVIADO),
        'qtd_aprovadas': sum(1 for d in despesas if d.status == StatusDespesa.APROVADO),
        'qtd_estouro': sum(1 for d in despesas if d.excede_teto),
    })


CAMPOS_COMPROVANTE = {'nota': 'comprovante', 'pagamento': 'comprovante_pagamento'}


@login_required
@require_GET
@xframe_options_sameorigin
def comprovante_auditoria_view(request, pk, tipo):
    """
    Entrega a NF/recibo ou o comprovante de pagamento de uma despesa para o painel de auditoria.

    - O que faz: Devolve o arquivo (`tipo='nota'` para a NF ou recibo, `tipo='pagamento'` para o comprovante
      Cora PJ) para exibição dentro do modal de conferência ou numa aba nova.
    - Como faz: Exige `usuario_pode_acessar_painel_auditoria` (403 para os demais); responde 404 para tipo
      desconhecido, despesa inexistente ou sem arquivo; abre o arquivo pelo storage e responde com
      `FileResponse` inline, tipo MIME pela extensão, `nosniff` e cache privado. O decorador
      `xframe_options_sameorigin` troca o `X-Frame-Options: DENY` global por `SAMEORIGIN` só nesta rota.
    - Qual finalidade atende: Permite exibir PDFs no modal da Issue #13 (o `DENY` global bloqueava o
      `<iframe>`) sem afrouxar a proteção contra clickjacking do resto do site, e só entrega o documento
      fiscal a quem audita as contas do AG VII.
    """
    if not usuario_pode_acessar_painel_auditoria(request.user):
        raise PermissionDenied("Apenas a Tesouraria pode abrir os comprovantes no painel de auditoria.")

    campo = CAMPOS_COMPROVANTE.get(tipo)
    if campo is None:
        raise Http404("Tipo de comprovante desconhecido.")

    despesa = get_object_or_404(Despesa, pk=pk)
    arquivo = getattr(despesa, campo)
    if not arquivo:
        raise Http404("Esta despesa não tem esse comprovante.")

    try:
        conteudo = arquivo.open('rb')
    except FileNotFoundError as exc:
        raise Http404("Arquivo do comprovante não encontrado.") from exc

    tipo_mime = mimetypes.guess_type(arquivo.name)[0] or 'application/octet-stream'
    resposta = FileResponse(conteudo, content_type=tipo_mime)
    resposta['Content-Disposition'] = 'inline'
    resposta['X-Content-Type-Options'] = 'nosniff'
    resposta['Cache-Control'] = 'private, max-age=300'
    return resposta


@login_required
@require_POST
def aprovar_despesa_view(request, pk):
    """
    Processa a aprovação de uma despesa submetida na fila de triagem da Tesouraria (RF06).

    - O que faz: Promove uma despesa de `ENVIADO` para `APROVADO` sob transação atômica.
    - Como faz: Valida perfil `is_tesoureiro`; invoca `aprovar_despesa_triagem`; trata violações de RN03
      ou máquina de estados exibindo mensagens de feedback e redirecionando para `despesas:triagem`.
    - Qual finalidade atende: Habilita a aprovação em um clique na triagem com segurança e auditoria (RN06).
    """
    if not getattr(request.user, 'is_tesoureiro', False):
        raise PermissionDenied("Apenas membros da Tesouraria podem aprovar despesas.")

    despesa = get_object_or_404(Despesa, pk=pk)
    observacao = (request.POST.get('observacao') or '').strip()

    try:
        aprovar_despesa_triagem(despesa=despesa, tesoureiro=request.user, observacao=observacao)
        messages.success(
            request,
            f"Despesa #{despesa.id} ({despesa.coordenacao.sigla}) aprovada e liberada para liquidação!"
        )
    except PermissaoNegadaDominioError as exc:
        raise PermissionDenied(str(exc)) from exc
    except ValidationError as exc:
        messages.error(request, _extrair_mensagem_erro(exc))

    return redirect('despesas:triagem')


@login_required
@require_POST
def rejeitar_despesa_view(request, pk):
    """
    Processa a reprovação de uma despesa na triagem exigindo parecer textual obrigatório (RN04).

    - O que faz: Valida o `RejeicaoDespesaForm` e transiciona a despesa para `REJEITADO`.
    - Como faz: Verifica perfil `is_tesoureiro`; valida formulário; invoca `rejeitar_despesa_triagem`
      registrando motivo e auditoria (RN06); redireciona com mensagem de erro ou confirmação.
    - Qual finalidade atende: Garante que nenhuma despesa seja recusada sem justificativa clara ao campo.
    """
    if not getattr(request.user, 'is_tesoureiro', False):
        raise PermissionDenied("Apenas membros da Tesouraria podem rejeitar despesas.")

    despesa = get_object_or_404(Despesa, pk=pk)
    form = RejeicaoDespesaForm(request.POST)

    if not form.is_valid():
        erro = form.errors.get('motivo_rejeicao', ['Informe a justificativa da reprovação.'])[0]
        messages.error(request, f"Erro ao rejeitar despesa #{despesa.id}: {erro}")
        return redirect('despesas:triagem')

    try:
        rejeitar_despesa_triagem(
            despesa=despesa,
            tesoureiro=request.user,
            motivo=form.cleaned_data['motivo_rejeicao'],
        )
        messages.warning(
            request,
            f"Despesa #{despesa.id} rejeitada e devolvida ao solicitante com justificativa."
        )
    except PermissaoNegadaDominioError as exc:
        raise PermissionDenied(str(exc)) from exc
    except ValidationError as exc:
        messages.error(request, _extrair_mensagem_erro(exc))

    return redirect('despesas:triagem')


@login_required
@require_POST
def liquidar_despesa_view(request, pk):
    """
    Processa a liquidação bancária (Banco Cora PJ) de uma despesa aprovada (RF07).

    - O que faz: Valida o anexo obrigatório de transferência bancária e transiciona para `PAGO`.
    - Como faz: Verifica perfil `is_tesoureiro`; valida `LiquidacaoDespesaForm`; delega compressão Pillow
      e liquidação transacional a `liquidar_despesa_triagem`; redireciona para `despesas:triagem`.
    - Qual finalidade atende: Encerra o ciclo financeiro do reembolso com comprovante bancário auditável.
    """
    if not getattr(request.user, 'is_tesoureiro', False):
        raise PermissionDenied("Apenas membros da Tesouraria podem liquidar despesas.")

    despesa = get_object_or_404(Despesa, pk=pk)
    form = LiquidacaoDespesaForm(request.POST, request.FILES)

    if not form.is_valid():
        erro = form.errors.get('comprovante_pagamento', ['Comprovante bancário Cora PJ obrigatório.'])[0]
        messages.error(request, f"Erro ao liquidar despesa #{despesa.id}: {erro}")
        return redirect('despesas:triagem')

    try:
        liquidar_despesa_triagem(
            despesa=despesa,
            tesoureiro=request.user,
            comprovante_pagamento=form.cleaned_data['comprovante_pagamento'],
        )
        messages.success(
            request,
            f"Despesa #{despesa.id} liquidada como PAGO com comprovante do Banco Cora PJ anexado!"
        )
    except PermissaoNegadaDominioError as exc:
        raise PermissionDenied(str(exc)) from exc
    except ValidationError as exc:
        messages.error(request, _extrair_mensagem_erro(exc))

    return redirect('despesas:triagem')
