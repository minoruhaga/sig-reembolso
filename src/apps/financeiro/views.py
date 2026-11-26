from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.core.exceptions import PermissaoNegadaDominioError, SigReembolsoDomainError
from apps.financeiro.models import Coordenacao
from apps.financeiro.services import atualizar_teto_orcamentario, obter_resumo_orcamentario
from apps.usuarios.services import usuario_pode_acessar_admin


def _serializar_item_json(item: dict) -> dict:
    """
    Converte os campos `Decimal` de um indicador de coordenação para strings decimais exatas em JSON.

    - O que faz: Formata valores monetários com duas casas decimais para resposta segura de API.
    - Como faz: Converte os campos em Reais para `f"{valor:.2f}"`, preservando strings, booleanos e percentual.
    - Qual finalidade atende: Evita erros de arredondamento de ponto flutuante na comunicação JSON (RF03).
    """
    return {
        'id': item['id'],
        'sigla': item['sigla'],
        'nome': item['nome'],
        'descricao': item['descricao'],
        'teto_orcamentario': f"{item['teto_orcamentario']:.2f}",
        'total_pago': f"{item['total_pago']:.2f}",
        'total_aprovado': f"{item['total_aprovado']:.2f}",
        'total_enviado': f"{item['total_enviado']:.2f}",
        'total_comprometido': f"{item['total_comprometido']:.2f}",
        'saldo_disponivel': f"{item['saldo_disponivel']:.2f}",
        'percentual_consumido': item['percentual_consumido'],
        'percentual_real': item['percentual_real'],
        'em_estouro': item['em_estouro'],
        'nivel_alerta': item['nivel_alerta'],
    }


@login_required
def painel_saldos_view(request):
    """
    Exibe a página dedicada de saldos, comprometimentos e termômetros de verba por coordenação.

    - O que faz: Apresenta a situação orçamentária em tempo real das pastas visíveis ao usuário autenticado,
      habilitando ajustes de teto para a Tesouraria e Administração Geral.
    - Como faz: Delega o cálculo ao serviço `obter_resumo_orcamentario(request.user, sigla=...)`, aplica a
      flag `pode_editar_tetos` baseada em `usuario_pode_acessar_admin` e renderiza `painel_saldos.html`.
    - Qual finalidade atende: Cumpre os requisitos RF02 e RF03 entregando transparência orçamentária dedicada.
    """
    sigla = request.GET.get('sigla')
    resumo = obter_resumo_orcamentario(request.user, sigla=sigla)

    return render(request, 'financeiro/painel_saldos.html', {
        'coordenacoes': resumo['coordenacoes'],
        'totais': resumo['totais'],
        'sigla_filtro': sigla or '',
        'pode_editar_tetos': usuario_pode_acessar_admin(request.user),
    })


@login_required
def api_saldos_coordenacoes_view(request):
    """
    Endpoint JSON que expõe saldos, comprometimentos por status e termômetros das coordenações visíveis.

    - O que faz: Retorna em tempo real o resumo consolidado e a lista de coordenações autorizadas pelo RBAC.
    - Como faz: Chama `obter_resumo_orcamentario(request.user, sigla=...)` e serializa todos os valores
      monetários `Decimal` via `_serializar_item_json` em um `JsonResponse`.
    - Qual finalidade atende: Permite consultas assíncronas e atualização dinâmica de barras de progresso em
      telas Mobile-First e no painel da Tesouraria (Issue #10 / RF03).
    """
    sigla = request.GET.get('sigla')
    resumo = obter_resumo_orcamentario(request.user, sigla=sigla)
    totais = resumo['totais']

    return JsonResponse({
        'totais': {
            'total_orcado': f"{totais['total_orcado']:.2f}",
            'total_pago': f"{totais['total_pago']:.2f}",
            'total_aprovado': f"{totais['total_aprovado']:.2f}",
            'total_enviado': f"{totais['total_enviado']:.2f}",
            'total_comprometido': f"{totais['total_comprometido']:.2f}",
            'total_saldo_livre': f"{totais['total_saldo_livre']:.2f}",
            'percentual_consumido': totais['percentual_consumido'],
            'percentual_real': totais['percentual_real'],
        },
        'coordenacoes': [_serializar_item_json(item) for item in resumo['coordenacoes']],
    })


@login_required
@require_POST
def atualizar_teto_coordenacao_view(request, pk):
    """
    Processa a atualização de teto orçamentário de uma coordenação pela Tesouraria (RF02).

    - O que faz: Recebe o novo limite em Reais via POST e delega a persistência atômica ao serviço financeiro.
    - Como faz: Localiza `Coordenacao` por PK; normaliza string numérica para `Decimal`; chama
      `atualizar_teto_orcamentario`; converte falhas de autorização em HTTP 403 (`PermissionDenied`) e falhas
      de validação em mensagens amigáveis antes de redirecionar para `financeiro:saldos`.
    - Qual finalidade atende: Permite ajustes orçamentários rápidos pela Tesouraria durante o AG VII (RF02).
    """
    coordenacao = get_object_or_404(Coordenacao, pk=pk, ativo=True)
    valor_bruto = (request.POST.get('novo_teto') or '').strip().replace(',', '.')

    try:
        novo_teto = Decimal(valor_bruto)
    except InvalidOperation:
        messages.error(request, "Informe um valor monetário válido para o teto orçamentário.")
        return redirect('financeiro:saldos')

    try:
        atualizar_teto_orcamentario(
            usuario=request.user,
            coordenacao=coordenacao,
            novo_teto=novo_teto,
        )
        messages.success(
            request,
            f"Teto da coordenação {coordenacao.sigla} atualizado com sucesso para R$ {coordenacao.teto_orcamentario:.2f}."
        )
    except PermissaoNegadaDominioError as exc:
        raise PermissionDenied(str(exc)) from exc
    except SigReembolsoDomainError as exc:
        messages.error(request, exc.message if hasattr(exc, 'message') else str(exc))

    return redirect('financeiro:saldos')
