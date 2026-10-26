from decimal import Decimal

from django.db import models
from django.utils import timezone


class Coordenacao(models.Model):
    """
    Entidade de domínio que representa cada uma das 15 coordenações operacionais do AG VII.

    - O que faz: Armazena os dados cadastrais da coordenação e seu teto orçamentário aprovado (R$),
      calculando em tempo real o valor comprometido, o saldo livre e o percentual de consumo.
    - Como faz: Utiliza `DecimalField` para o teto orçamentário e agrega via ORM (`models.Sum`) as despesas
      vinculadas nos estados `ENVIADO`, `APROVADO` e `PAGO`.
    - Qual finalidade atende: Atende aos requisitos RF02 e RF03, impedindo o descontrole financeiro do
      orçamento global de R$ 180.000,00 do Acampamento Geral VII.
    """

    nome = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nome da Coordenação'
    )
    sigla = models.CharField(
        max_length=10,
        unique=True,
        verbose_name='Sigla'
    )
    descricao = models.TextField(
        blank=True,
        verbose_name='Atribuição Operacional'
    )
    teto_orcamentario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Teto Orçamentário (R$)'
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name='Ativo'
    )
    criado_em = models.DateTimeField(
        default=timezone.now,
        verbose_name='Data de Criação'
    )

    class Meta:
        verbose_name = 'Coordenação'
        verbose_name_plural = 'Coordenações'
        ordering = ['nome']

    def __str__(self):
        """
        Retorna a identificação textual da coordenação.

        - O que faz: Combina a sigla e o nome completo da coordenação.
        - Como faz: Interpola os campos `sigla` e `nome` em uma string formatada.
        - Qual finalidade atende: Padroniza a exibição das 15 áreas em seletores de formulário e relatórios.
        """
        return f"{self.sigla} - {self.nome}"

    @property
    def total_comprometido(self) -> Decimal:
        """
        Calcula o montante financeiro já comprometido pela coordenação.

        - O que faz: Soma todas as despesas da coordenação nos estados `ENVIADO`, `APROVADO` e `PAGO`.
        - Como faz: Executa agregação SQL `Sum('valor')` sobre o relacionamento reverso `self.despesas`,
          retornando `Decimal('0.00')` caso não existam lançamentos ativos.
        - Qual finalidade atende: Garante que tanto gastos já pagos quanto notas aguardando triagem na fila
          sensibilizem preventivamente o limite da área (RF03 e RN02).
        """
        from apps.despesas.models import StatusDespesa
        estados_comprometidos = [
            StatusDespesa.ENVIADO,
            StatusDespesa.APROVADO,
            StatusDespesa.PAGO,
        ]
        total = self.despesas.filter(
            status__in=estados_comprometidos
        ).aggregate(total=models.Sum('valor'))['total']
        return total or Decimal('0.00')

    @property
    def saldo_disponivel(self) -> Decimal:
        """
        Calcula o saldo orçamentário livre da coordenação em Reais (R$).

        - O que faz: Subtrai o `total_comprometido` do `teto_orcamentario` da área.
        - Como faz: Realiza aritmética exata com objetos `Decimal` sem uso de ponto flutuante.
        - Qual finalidade atende: Fornece o parâmetro exato para o cálculo de estouro orçamentário (soft-block RN02)
          e para tomada de decisão imediata da Tesouraria.
        """
        return self.teto_orcamentario - self.total_comprometido

    @property
    def percentual_consumido(self) -> float:
        """
        Calcula o percentual de consumo do teto orçamentário para exibição visual.

        - O que faz: Retorna a razão percentual (limitada a 100.0% na barra visual) entre o valor comprometido e o teto.
        - Como faz: Divide `total_comprometido` por `teto_orcamentario` usando aritmética `Decimal` e arredonda para 1 casa decimal.
        - Qual finalidade atende: Alimenta as barras de progresso (termômetros de verba) no Dashboard (RF03).
        """
        if self.teto_orcamentario > Decimal('0.00'):
            pct = (self.total_comprometido / self.teto_orcamentario) * Decimal('100.0')
            return float(min(round(pct, 1), Decimal('100.0')))
        return 0.0
