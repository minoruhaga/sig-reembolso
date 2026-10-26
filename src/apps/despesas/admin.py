from django.contrib import admin

from .models import Despesa, HistoricoTransicaoStatus


class HistoricoTransicaoInline(admin.TabularInline):
    """
    Exibição inline somente-leitura do histórico de transições dentro da tela da Despesa.

    - O que faz: Lista cronologicamente todas as transições de estado sofridas pela despesa no Django Admin.
    - Como faz: Configura `TabularInline` com `can_delete = False` e todos os campos em `readonly_fields`.
    - Qual finalidade atende: Preserva a imutabilidade da trilha de auditoria (RN06) enquanto facilita a consulta pela Tesouraria.
    """

    model = HistoricoTransicaoStatus
    extra = 0
    can_delete = False
    readonly_fields = ('status_anterior', 'novo_status', 'alterado_por', 'data_hora', 'observacao')


@admin.register(Despesa)
class DespesaAdmin(admin.ModelAdmin):
    """
    Configuração do painel administrativo para inspeção e auditoria de Despesas.

    - O que faz: Disponibiliza listagem filtrável por status, coordenação, categoria e flag de estouro (`excede_teto`).
    - Como faz: Registra `ModelAdmin` com campos calculados protegidos em `readonly_fields` e anexa `HistoricoTransicaoInline`.
    - Qual finalidade atende: Permite auditoria administrativa rápida dos lançamentos financeiros do AG VII.
    """

    list_display = ('id', 'titulo', 'coordenacao', 'solicitante', 'valor', 'status', 'excede_teto', 'data_despesa')
    list_filter = ('status', 'coordenacao', 'categoria', 'tipo', 'excede_teto')
    search_fields = ('titulo', 'descricao', 'solicitante__username', 'solicitante__first_name', 'solicitante__last_name')
    readonly_fields = ('criado_em', 'atualizado_em', 'excede_teto', 'valor_excedente', 'analisado_em', 'pago_em')
    inlines = [HistoricoTransicaoInline]


@admin.register(HistoricoTransicaoStatus)
class HistoricoTransicaoStatusAdmin(admin.ModelAdmin):
    """
    Visualização dedicada e estritamente imutável dos logs de auditoria no Django Admin.

    - O que faz: Exibe todos os eventos de mudança de status registrados no sistema sem permitir edição ou exclusão.
    - Como faz: Define todos os atributos como `readonly_fields` e desabilita a deleção (`can_delete = False`).
    - Qual finalidade atende: Garante conformidade com a RN06 perante a Diretoria e o Conselho Fiscal.
    """

    list_display = ('despesa', 'status_anterior', 'novo_status', 'alterado_por', 'data_hora')
    list_filter = ('novo_status', 'status_anterior')
    readonly_fields = ('despesa', 'status_anterior', 'novo_status', 'alterado_por', 'data_hora', 'observacao')
    can_delete = False
