from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
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
