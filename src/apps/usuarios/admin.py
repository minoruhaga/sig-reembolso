from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """
    Configuração da interface administrativa para gestão de usuários e papéis (RBAC).

    - O que faz: Expõe os campos customizados (`papel`, `chave_pix`, `telefone`) na listagem e nos formulários do Django Admin.
    - Como faz: Especializa `UserAdmin` anexando fieldsets específicos do SIG-Reembolso e filtros laterais por papel.
    - Qual finalidade atende: Permite que a Diretoria e a Coordenação Financeira cadastrem voluntários e chaves PIX com segurança.
    """

    list_display = ('username', 'email', 'first_name', 'last_name', 'papel', 'chave_pix', 'is_active')
    list_filter = ('papel', 'is_active', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Atribuições no SIG-Reembolso', {
            'fields': ('papel', 'chave_pix', 'telefone'),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Atribuições no SIG-Reembolso', {
            'fields': ('papel', 'chave_pix', 'telefone'),
        }),
    )
