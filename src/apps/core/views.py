from django.shortcuts import render

from apps.despesas.models import Despesa
from apps.financeiro.models import Coordenacao


def dashboard_view(request):
    """
    Exibe o painel consolidado do evento e termômetros orçamentários.

    - O que faz: Renderiza a visão geral do orçamento do AG VII, saldos livres, total comprometido
      e a listagem das despesas recentemente tramitadas.
    - Como faz: Consulta as coordenações ativas, soma dinamicamente os tetos e saldos livres calculados
      nas propriedades do model e busca as últimas 10 despesas com joins otimizados (`select_related`).
    - Qual finalidade atende: Atende ao requisito RF03 (consulta dinâmica de saldo e termômetro de verba)
      oferecendo transparência imediata para a Tesouraria e coordenadores de campo.
    """
    coordenacoes = list(Coordenacao.objects.filter(ativo=True).order_by('nome'))
    
    total_orcado = sum(c.teto_orcamentario for c in coordenacoes)
    total_comprometido = sum(c.total_comprometido for c in coordenacoes)
    total_saldo_livre = total_orcado - total_comprometido
    
    despesas_recentes = Despesa.objects.select_related('coordenacao', 'solicitante').order_by('-criado_em')[:10]
    
    context = {
        'coordenacoes': coordenacoes,
        'total_orcado': total_orcado,
        'total_comprometido': total_comprometido,
        'total_saldo_livre': total_saldo_livre,
        'despesas_recentes': despesas_recentes,
    }
    return render(request, 'dashboard.html', context)
