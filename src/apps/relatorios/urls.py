"""
Configuração de rotas do aplicativo de Relatórios e Prestação de Contas (RF08).
"""

from django.urls import path

from apps.relatorios import views

app_name = 'relatorios'

urlpatterns = [
    path('balancete/', views.balancete_view, name='balancete'),
    path('exportar.csv', views.exportar_csv_view, name='exportar_csv'),
]
