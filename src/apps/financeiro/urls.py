"""
Configuração de rotas do aplicativo Financeiro (Tetos Orçamentários e Saldos).
"""
from django.urls import path

from apps.financeiro import views

app_name = 'financeiro'

urlpatterns = [
    path('saldos/', views.painel_saldos_view, name='saldos'),
    path('api/saldos/', views.api_saldos_coordenacoes_view, name='api_saldos'),
    path('coordenacoes/<int:pk>/teto/', views.atualizar_teto_coordenacao_view, name='atualizar_teto'),
]
