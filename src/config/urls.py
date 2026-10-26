"""
URL configuration for config project.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from apps.core.views import dashboard_view

admin.site.site_header = "SIG-Reembolso | AG VII Caramuru"
admin.site.site_title = "Administração SIG-Reembolso"
admin.site.index_title = "Painel de Governança e Finanças"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard_view, name='dashboard'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
