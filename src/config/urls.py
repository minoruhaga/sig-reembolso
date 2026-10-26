"""
Configuração central de URLs do projeto SIG-Reembolso.

Delega as rotas específicas para cada app de domínio (`usuarios`, `financeiro`, `despesas`)
a fim de evitar conflitos de merge durante o desenvolvimento paralelo da equipe.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from apps.core.views import dashboard_view

admin.site.site_header = "SIG-Reembolso | AG VII Caramuru"
admin.site.site_title = "Administração SIG-Reembolso"
admin.site.index_title = "Painel de Governança e Finanças"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard_view, name='dashboard'),
    path('usuarios/', include('apps.usuarios.urls', namespace='usuarios')),
    path('financeiro/', include('apps.financeiro.urls', namespace='financeiro')),
    path('despesas/', include('apps.despesas.urls', namespace='despesas')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
