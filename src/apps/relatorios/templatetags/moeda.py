"""
Filtros de template para exibir valores em Reais na prestação de contas.

- O que faz: Expõe a formatação brasileira de `Decimal` aos templates de relatório.
- Como faz: Delega a `formatar_reais_exibicao`, que não usa `float`.
- Qual finalidade atende: Mostra totais com separador de milhar para o voluntário do AG VII (RF08).
"""

from django import template

from apps.relatorios.services import formatar_reais_exibicao

register = template.Library()


@register.filter(name='reais')
def reais(valor):
    """
    Formata um montante para a tela da prestação de contas.

    - O que faz: Converte o total do balancete em texto no padrão `40.788,40`.
    - Como faz: Chama `formatar_reais_exibicao` com o `Decimal` já calculado no serviço.
    - Qual finalidade atende: Evita que o template recalcule dinheiro e mantém a leitura em Reais (RF08).
    """
    return formatar_reais_exibicao(valor)
