from django.contrib import admin

from .models import Despesa, HistoricoTransicaoStatus


class HistoricoTransicaoInline(admin.TabularInline):
    model = HistoricoTransicaoStatus
    extra = 0
    can_delete = False
    readonly_fields = ('status_anterior', 'novo_status', 'alterado_por', 'data_hora', 'observacao')


@admin.register(Despesa)
class DespesaAdmin(admin.ModelAdmin):
    list_display = ('id', 'titulo', 'coordenacao', 'solicitante', 'valor', 'status', 'excede_teto', 'data_despesa')
    list_filter = ('status', 'coordenacao', 'categoria', 'tipo', 'excede_teto')
    search_fields = ('titulo', 'descricao', 'solicitante__username', 'solicitante__first_name', 'solicitante__last_name')
    readonly_fields = ('criado_em', 'atualizado_em', 'excede_teto', 'valor_excedente', 'analisado_em', 'pago_em')
    inlines = [HistoricoTransicaoInline]


@admin.register(HistoricoTransicaoStatus)
class HistoricoTransicaoStatusAdmin(admin.ModelAdmin):
    list_display = ('despesa', 'status_anterior', 'novo_status', 'alterado_por', 'data_hora')
    list_filter = ('novo_status', 'status_anterior')
    readonly_fields = ('despesa', 'status_anterior', 'novo_status', 'alterado_por', 'data_hora', 'observacao')
    can_delete = False
