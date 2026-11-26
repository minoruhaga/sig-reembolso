"""
Configuração de rotas do aplicativo de Usuários e Autenticação (RBAC).
"""

from django.urls import path

from apps.usuarios import views

app_name = 'usuarios'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
]
