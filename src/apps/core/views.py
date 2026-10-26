from decimal import Decimal
from django.db.models import Sum
from django.shortcuts import render
from apps.financeiro.models import Coordenacao
from apps.despesas.models import Despesa, StatusDespesa


def dashboard_view(request):
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
