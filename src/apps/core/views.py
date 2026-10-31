from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.usuarios.services import coordenacoes_visiveis, despesas_visiveis, usuario_pode_acessar_admin


@login_required
def dashboard_view(request):
    """
    Exibe o painel consolidado do evento e termômetros orçamentários no recorte do papel.

    - O que faz: Renderiza tetos, saldos e despesas recentes visíveis ao usuário autenticado.
    - Como faz: Delega o recorte a `coordenacoes_visiveis` e `despesas_visiveis`; soma tetos e
      comprometidos apenas sobre esse queryset com aritmética `Decimal`.
    - Qual finalidade atende: Atende RF03 com isolamento RF01 — coordenador vê a própria pasta;
      Tesouraria e Diretoria veem as 15 coordenações.
    """
    coordenacoes = list(coordenacoes_visiveis(request.user))
    total_orcado = sum((c.teto_orcamentario for c in coordenacoes), start=Decimal('0.00'))
    total_comprometido = sum((c.total_comprometido for c in coordenacoes), start=Decimal('0.00'))
    total_saldo_livre = total_orcado - total_comprometido
    despesas_recentes = despesas_visiveis(request.user)[:10]

    context = {
        'coordenacoes': coordenacoes,
        'total_orcado': total_orcado,
        'total_comprometido': total_comprometido,
        'total_saldo_livre': total_saldo_livre,
        'despesas_recentes': despesas_recentes,
        'visao_gestor': usuario_pode_acessar_admin(request.user),
    }
    return render(request, 'dashboard.html', context)
