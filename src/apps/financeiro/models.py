from decimal import Decimal
from django.db import models
from django.utils import timezone


class Coordenacao(models.Model):
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
        return f"{self.sigla} - {self.nome}"

    @property
    def total_comprometido(self) -> Decimal:
        """
        Soma das despesas nos estados ENVIADO, APROVADO e PAGO.
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
        Saldo livre para novos gastos na coordenação.
        """
        return self.teto_orcamentario - self.total_comprometido

    @property
    def percentual_consumido(self) -> float:
        """
        Percentual de consumo orçamentário para exibição no termômetro visual.
        """
        if self.teto_orcamentario > 0:
            pct = (float(self.total_comprometido) / float(self.teto_orcamentario)) * 100
            return round(min(pct, 100.0), 1)
        return 0.0
