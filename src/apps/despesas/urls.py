"""
Configuração de rotas do aplicativo de Despesas, Submissão Mobile e Triagem.
"""
from django.urls import path

from apps.despesas import views

app_name = 'despesas'

urlpatterns = [
    path('nova/', views.nova_despesa_view, name='nova'),
    path('previa-orcamento/', views.previa_orcamento_view, name='previa_orcamento'),
    path('minhas/', views.minhas_despesas_view, name='minhas'),
    path('<int:pk>/editar/', views.editar_despesa_view, name='editar'),
    path('<int:pk>/submeter/', views.submeter_despesa_view, name='submeter'),
    path('triagem/', views.painel_triagem_view, name='triagem'),
    path('<int:pk>/aprovar/', views.aprovar_despesa_view, name='aprovar'),
    path('<int:pk>/rejeitar/', views.rejeitar_despesa_view, name='rejeitar'),
    path('<int:pk>/liquidar/', views.liquidar_despesa_view, name='liquidar'),
]
