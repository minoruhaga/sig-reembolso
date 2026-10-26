from django.contrib import admin
from .models import Coordenacao


@admin.register(Coordenacao)
class CoordenacaoAdmin(admin.ModelAdmin):
    list_display = ('sigla', 'nome', 'teto_orcamentario', 'total_comprometido_display', 'saldo_disponivel_display', 'percentual_display', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('sigla', 'nome', 'descricao')
    readonly_fields = ('criado_em',)

    @admin.display(description='Comprometido (R$)')
    def total_comprometido_display(self, obj):
        return f"R$ {obj.total_comprometido:,.2f}"

    @admin.display(description='Saldo Livre (R$)')
    def saldo_disponivel_display(self, obj):
        return f"R$ {obj.saldo_disponivel:,.2f}"

    @admin.display(description='Consumo (%)')
    def percentual_display(self, obj):
        return f"{obj.percentual_consumido}%"
