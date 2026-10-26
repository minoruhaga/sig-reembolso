from django.contrib import admin

from .models import Coordenacao


@admin.register(Coordenacao)
class CoordenacaoAdmin(admin.ModelAdmin):
    """
    Painel administrativo para gestão das 15 coordenações e acompanhamento de tetos orçamentários.

    - O que faz: Exibe na listagem administrativa o teto aprovado, o valor comprometido, o saldo livre e o percentual consumido.
    - Como faz: Registra colunas calculadas com `@admin.display` consumindo as propriedades de domínio do modelo `Coordenacao`.
    - Qual finalidade atende: Oferece à Diretoria e à Tesouraria uma visão contábil consolidada das cotas do AG VII.
    """

    list_display = (
        'sigla',
        'nome',
        'teto_orcamentario',
        'total_comprometido_display',
        'saldo_disponivel_display',
        'percentual_display',
        'ativo',
    )
    list_filter = ('ativo',)
    search_fields = ('sigla', 'nome', 'descricao')
    readonly_fields = ('criado_em',)

    @admin.display(description='Comprometido (R$)')
    def total_comprometido_display(self, obj):
        """
        Formata o total comprometido da coordenação em moeda nacional (R$).

        - O que faz: Retorna string formatada com prefixo `R$` e duas casas decimais.
        - Como faz: Lê a propriedade `obj.total_comprometido` do modelo `Coordenacao`.
        - Qual finalidade atende: Melhora a legibilidade contábil na listagem do Django Admin.
        """
        return f"R$ {obj.total_comprometido:,.2f}"

    @admin.display(description='Saldo Livre (R$)')
    def saldo_disponivel_display(self, obj):
        """
        Formata o saldo disponível da coordenação em moeda nacional (R$).

        - O que faz: Retorna string formatada com prefixo `R$` e duas casas decimais.
        - Como faz: Lê a propriedade `obj.saldo_disponivel` do modelo `Coordenacao`.
        - Qual finalidade atende: Permite identificar rapidamente áreas próximas do limite orçamentário no Admin.
        """
        return f"R$ {obj.saldo_disponivel:,.2f}"

    @admin.display(description='Consumo (%)')
    def percentual_display(self, obj):
        """
        Formata o percentual consumido do orçamento da coordenação.

        - O que faz: Exibe o valor percentual seguido do símbolo `%`.
        - Como faz: Lê a propriedade `obj.percentual_consumido` do modelo `Coordenacao`.
        - Qual finalidade atende: Sintetiza o grau de utilização da cota orçamentária da área.
        """
        return f"{obj.percentual_consumido}%"
