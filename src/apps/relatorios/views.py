"""
Views orquestradoras para visualização de balancetes e download de exportações contábeis (RF08).

- O que faz: Recebe requisições HTTP autenticadas de exportação CSV e balancetes sintéticos,
  delegando cálculos e filtragens para `apps.relatorios.services`.
- Como faz: Aplica proteção de sessão/RBAC e retorna respostas de download (`HttpResponse` CSV) ou
  renderiza templates de prestação de contas sem conter lógica de negócio direta.
- Qual finalidade atende: Viabiliza o cumprimento da entrega do módulo de relatórios (Issue #34)
  seguindo estritamente a separação de camadas definida em `src/AGENTS.md`.
"""

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from apps.despesas.models import CategoriaDespesa, StatusDespesa
from apps.relatorios.services import gerar_balancete_sintetico, gerar_csv_despesas
from apps.usuarios.services import coordenacoes_visiveis


def _filtros_da_requisicao(request) -> dict:
    """
    Lê os filtros de prestação de contas enviados na query string.

    - O que faz: Extrai coordenação, categoria e status sem interpretar regra contábil.
    - Como faz: Copia `request.GET` para um dicionário de argumentos do serviço de relatórios.
    - Qual finalidade atende: Mantém a view como orquestradora da Issue #34 (RF08).
    """
    return {
        'coordenacao': request.GET.get('coordenacao'),
        'categoria': request.GET.get('categoria'),
        'status': request.GET.get('status'),
    }


@login_required
def balancete_view(request):
    """
    Exibe o balancete sintético da prestação de contas no recorte do usuário.

    - O que faz: Mostra totais por coordenação e categoria e oferece os mesmos filtros da exportação CSV.
    - Como faz: Encaminha os parâmetros a `gerar_balancete_sintetico` e lista só coordenações visíveis no formulário.
    - Qual finalidade atende: Dá à Tesouraria e ao coordenador a leitura consolidada do AG VII (RF08).
    """
    filtros = _filtros_da_requisicao(request)
    balancete = gerar_balancete_sintetico(request.user, **filtros)
    return render(request, 'relatorios/balancete.html', {
        'balancete': balancete,
        'filtros': {
            'coordenacao': (filtros['coordenacao'] or '').strip(),
            'categoria': (filtros['categoria'] or '').strip(),
            'status': (filtros['status'] or '').strip(),
        },
        'coordenacoes': coordenacoes_visiveis(request.user),
        'categorias': CategoriaDespesa.choices,
        'status_opcoes': StatusDespesa.choices,
    })


@login_required
def exportar_csv_view(request):
    """
    Entrega o download da planilha analítica de despesas.

    - O que faz: Responde com o CSV das despesas autorizadas, respeitando os filtros da query string.
    - Como faz: Chama `gerar_csv_despesas` e devolve `HttpResponse` com BOM UTF-8 e `Content-Disposition`.
    - Qual finalidade atende: Disponibiliza a planilha estruturada da prestação de contas (RF08 / Issue #34).
    """
    filtros = _filtros_da_requisicao(request)
    conteudo = gerar_csv_despesas(request.user, **filtros)
    resposta = HttpResponse(
        '\ufeff' + conteudo,
        content_type='text/csv; charset=utf-8',
    )
    resposta['Content-Disposition'] = 'attachment; filename="prestacao_contas_ag7.csv"'
    return resposta
