from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone

from apps.financeiro.models import Coordenacao


class StatusDespesa(models.TextChoices):
    RASCUNHO = 'RASCUNHO', 'Rascunho'
    ENVIADO = 'ENVIADO', 'Enviado para Triagem'
    APROVADO = 'APROVADO', 'Aprovado'
    REJEITADO = 'REJEITADO', 'Rejeitado'
    PAGO = 'PAGO', 'Pago / Liquidado'
    CANCELADO = 'CANCELADO', 'Cancelado'


class CategoriaDespesa(models.TextChoices):
    ALIMENTACAO = 'ALIMENTACAO', 'Alimentação e Cozinha'
    COMBUSTIVEL = 'COMBUSTIVEL', 'Combustível e Transporte'
    SAUDE = 'SAUDE', 'Saúde e Farmácia'
    PROGRAMA = 'PROGRAMA', 'Programa e Atividades Escoteiras'
    INFRAESTRUTURA = 'INFRAESTRUTURA', 'Infraestrutura e Campo'
    LOCACAO = 'LOCACAO', 'Locação e Serviços'
    OUTROS = 'OUTROS', 'Outros Suprimentos'


class TipoDespesa(models.TextChoices):
    REEMBOLSO = 'REEMBOLSO', 'Reembolso (Desembolso do Voluntário)'
    FUNDO_CAIXA = 'FUNDO_CAIXA', 'Prestação de Contas de Fundo de Caixa'
    PAGAMENTO_DIRETO = 'PAGAMENTO_DIRETO', 'Pagamento Direto a Fornecedor'


class FormaPagamentoOriginal(models.TextChoices):
    PIX = 'PIX', 'PIX'
    CARTAO_DEBITO = 'CARTAO_DEBITO', 'Cartão de Débito'
    CARTAO_CREDITO = 'CARTAO_CREDITO', 'Cartão de Crédito'
    ESPECIE = 'ESPECIE', 'Dinheiro em Espécie'
    BOLETO = 'BOLETO', 'Boleto Bancário'


class Despesa(models.Model):
    coordenacao = models.ForeignKey(
        Coordenacao,
        on_delete=models.PROTECT,
        related_name='despesas',
        verbose_name='Coordenação Onerada'
    )
    solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='despesas_solicitadas',
        verbose_name='Solicitante'
    )
    titulo = models.CharField(
        max_length=150,
        verbose_name='Título da Despesa'
    )
    descricao = models.TextField(
        blank=True,
        verbose_name='Detalhamento Operacional'
    )
    categoria = models.CharField(
        max_length=20,
        choices=CategoriaDespesa.choices,
        default=CategoriaDespesa.OUTROS,
        verbose_name='Categoria Contábil'
    )
    tipo = models.CharField(
        max_length=20,
        choices=TipoDespesa.choices,
        default=TipoDespesa.REEMBOLSO,
        verbose_name='Modalidade'
    )
    forma_pagamento_original = models.CharField(
        max_length=20,
        choices=FormaPagamentoOriginal.choices,
        default=FormaPagamentoOriginal.PIX,
        verbose_name='Forma de Pagamento na Ponta'
    )
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Valor (R$)'
    )
    data_despesa = models.DateField(
        verbose_name='Data do Documento Fiscal'
    )
    comprovante = models.FileField(
        upload_to='comprovantes/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='Comprovante / Nota Fiscal'
    )
    status = models.CharField(
        max_length=20,
        choices=StatusDespesa.choices,
        default=StatusDespesa.RASCUNHO,
        db_index=True,
        verbose_name='Status Atual'
    )
    excede_teto = models.BooleanField(
        default=False,
        verbose_name='Excede Teto Orçamentário (Soft-block)'
    )
    valor_excedente = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Valor Excedente (R$)'
    )
    analisado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='despesas_analisadas',
        verbose_name='Analisado por'
    )
    analisado_em = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Analisado em'
    )
    motivo_rejeicao = models.TextField(
        blank=True,
        verbose_name='Justificativa de Reprovação'
    )
    pago_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='despesas_pagas',
        verbose_name='Pago por'
    )
    pago_em = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Pago em'
    )
    comprovante_pagamento = models.FileField(
        upload_to='pagamentos/%Y/%m/',
        null=True,
        blank=True,
        verbose_name='Comprovante de Transferência Cora PJ'
    )
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )
    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em'
    )

    class Meta:
        verbose_name = 'Despesa'
        verbose_name_plural = 'Despesas'
        ordering = ['-criado_em']

    def __str__(self):
        return f"[{self.coordenacao.sigla}] {self.titulo} - R$ {self.valor} ({self.get_status_display()})"

    def clean(self):
        super().clean()
        # RN01: Obrigatoriedade do comprovante para envio
        if self.status != StatusDespesa.RASCUNHO and not self.comprovante:
            raise ValidationError({'comprovante': 'O comprovante fiscal é obrigatório para envio.'})

        # RN04: Justificativa obrigatória em rejeição
        if self.status == StatusDespesa.REJEITADO and not self.motivo_rejeicao:
            raise ValidationError({'motivo_rejeicao': 'É obrigatório informar o motivo da reprovação.'})

    def _registrar_transicao(self, status_anterior, novo_status, usuario, observacao=''):
        HistoricoTransicaoStatus.objects.create(
            despesa=self,
            status_anterior=status_anterior,
            novo_status=novo_status,
            alterado_por=usuario,
            observacao=observacao
        )

    @transaction.atomic
    def submeter(self, usuario):
        """
        Transiciona de RASCUNHO (ou REJEITADO corrigido) para ENVIADO.
        Aplica RN01 (Comprovante obrigatório) e RN02 (Soft-block com cálculo de excedente).
        """
        if not self.comprovante:
            raise ValidationError("Não é possível submeter a despesa sem anexar o comprovante fiscal.")

        status_anterior = self.status
        if status_anterior not in (StatusDespesa.RASCUNHO, StatusDespesa.REJEITADO):
            raise ValidationError(f"Despesa em estado '{self.get_status_display()}' não pode ser submetida.")

        # RN02: Cálculo de soft-block de estouro
        saldo_livre = self.coordenacao.saldo_disponivel
        # Se a despesa já estava computada em total_comprometido (não é o caso de rascunho/rejeitado),
        # saldo_livre reflete o saldo sem ela.
        if self.valor > saldo_livre:
            self.excede_teto = True
            self.valor_excedente = self.valor - saldo_livre
        else:
            self.excede_teto = False
            self.valor_excedente = Decimal('0.00')

        self.status = StatusDespesa.ENVIADO
        self.save()
        self._registrar_transicao(status_anterior, StatusDespesa.ENVIADO, usuario, "Submissão para triagem da Tesouraria")

    @transaction.atomic
    def aprovar(self, tesoureiro, observacao=''):
        """
        Aprova a despesa na triagem.
        Aplica RN03 (Segregação de funções: tesoureiro não aprova próprio reembolso).
        """
        if self.status != StatusDespesa.ENVIADO:
            raise ValidationError("Apenas despesas no estado 'Enviado' podem ser aprovadas.")

        # RN03: Segregação de Funções
        if self.solicitante_id == tesoureiro.id and not tesoureiro.is_superuser:
            raise ValidationError("Segregação de Funções: O tesoureiro não pode aprovar sua própria solicitação.")

        status_anterior = self.status
        self.status = StatusDespesa.APROVADO
        self.analisado_por = tesoureiro
        self.analisado_em = timezone.now()
        self.save()
        self._registrar_transicao(status_anterior, StatusDespesa.APROVADO, tesoureiro, observacao or "Despesa aprovada na triagem")

    @transaction.atomic
    def rejeitar(self, tesoureiro, motivo):
        """
        Rejeita a despesa com motivo obrigatório (RN04).
        Aplica RN03 (Segregação de funções).
        """
        if self.status != StatusDespesa.ENVIADO:
            raise ValidationError("Apenas despesas no estado 'Enviado' podem ser rejeitadas.")

        if self.solicitante_id == tesoureiro.id and not tesoureiro.is_superuser:
            raise ValidationError("Segregação de Funções: O tesoureiro não pode reprovar sua própria solicitação.")

        if not motivo or not motivo.strip():
            raise ValidationError("A justificativa de reprovação é estritamente obrigatória.")

        status_anterior = self.status
        self.status = StatusDespesa.REJEITADO
        self.analisado_por = tesoureiro
        self.analisado_em = timezone.now()
        self.motivo_rejeicao = motivo.strip()
        self.save()
        self._registrar_transicao(status_anterior, StatusDespesa.REJEITADO, tesoureiro, f"Motivo: {self.motivo_rejeicao}")

    @transaction.atomic
    def liquidar(self, tesoureiro, comprovante_pagamento=None):
        """
        Marca como PAGO após transferência pelo Internet Banking Banco Cora PJ.
        """
        if self.status != StatusDespesa.APROVADO:
            raise ValidationError("Apenas despesas 'Aprovadas' podem ser liquidadas como Pagas.")

        status_anterior = self.status
        self.status = StatusDespesa.PAGO
        self.pago_por = tesoureiro
        self.pago_em = timezone.now()
        if comprovante_pagamento:
            self.comprovante_pagamento = comprovante_pagamento
        self.save()
        self._registrar_transicao(status_anterior, StatusDespesa.PAGO, tesoureiro, "Liquidação efetuada via Banco Cora PJ")


class HistoricoTransicaoStatus(models.Model):
    """
    Tabela imutável dedicada à auditoria e conformidade contábil (RN06).
    """
    despesa = models.ForeignKey(
        Despesa,
        on_delete=models.CASCADE,
        related_name='historico',
        verbose_name='Despesa Auditada'
    )
    status_anterior = models.CharField(
        max_length=20,
        verbose_name='Status Anterior'
    )
    novo_status = models.CharField(
        max_length=20,
        verbose_name='Novo Status'
    )
    alterado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        verbose_name='Autor da Alteração'
    )
    data_hora = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data e Hora (UTC)'
    )
    observacao = models.TextField(
        blank=True,
        verbose_name='Observação / Parecer'
    )

    class Meta:
        verbose_name = 'Histórico de Transição'
        verbose_name_plural = 'Histórico de Transições'
        ordering = ['data_hora']

    def __str__(self):
        return f"{self.despesa.id}: {self.status_anterior} -> {self.novo_status} por {self.alterado_por.username}"
