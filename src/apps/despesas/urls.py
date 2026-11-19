"""
Configuração de rotas do aplicativo de Despesas, Submissão Mobile e Triagem.
"""
from django.urls import path

from apps.despesas import views

app_name = 'despesas'

urlpatterns = [
    path('nova/', views.nova_despesa_view, name='nova'),
    path('minhas/', views.minhas_despesas_view, name='minhas'),
    path('<int:pk>/editar/', views.editar_despesa_view, name='editar'),
    path('<int:pk>/submeter/', views.submeter_despesa_view, name='submeter'),
]
