from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone

from apps.financeiro.models import Coordenacao


class StatusDespesa(models.TextChoices):
    """
    Estados possíveis do ciclo de vida finito de uma Despesa no SIG-Reembolso.

    - O que faz: Enumera os 6 estados formais pelos quais um lançamento financeiro pode transitar.
    - Como faz: Utiliza `models.TextChoices` para garantir consistência de valores no banco e na camada de domínio.
    - Qual finalidade atende: Sustenta a máquina de estados auditável definida na arquitetura do sistema e na RN06.
    """

    RASCUNHO = 'RASCUNHO', 'Rascunho'
    ENVIADO = 'ENVIADO', 'Enviado para Triagem'
    APROVADO = 'APROVADO', 'Aprovado'
    REJEITADO = 'REJEITADO', 'Rejeitado'
    PAGO = 'PAGO', 'Pago / Liquidado'
    CANCELADO = 'CANCELADO', 'Cancelado'


class CategoriaDespesa(models.TextChoices):
    """
    Classificação contábil da natureza do gasto efetuado pela coordenação.

    - O que faz: Agrupa as despesas nas categorias operacionais recorrentes do Acampamento Geral VII.
    - Como faz: Define escolhas padronizadas via `models.TextChoices`.
    - Qual finalidade atende: Facilita a prestação de contas final ao Grupo Escoteiro Caramuru e a análise histórica por natureza de gasto.
    """

    ALIMENTACAO = 'ALIMENTACAO', 'Alimentação e Cozinha'
    COMBUSTIVEL = 'COMBUSTIVEL', 'Combustível e Transporte'
    SAUDE = 'SAUDE', 'Saúde e Farmácia'
    PROGRAMA = 'PROGRAMA', 'Programa e Atividades Escoteiras'
    INFRAESTRUTURA = 'INFRAESTRUTURA', 'Infraestrutura e Campo'
    LOCACAO = 'LOCACAO', 'Locação e Serviços'
    OUTROS = 'OUTROS', 'Outros Suprimentos'


class TipoDespesa(models.TextChoices):
    """
    Modalidade financeira de realização da despesa.

    - O que faz: Diferencia reembolsos a voluntários, prestações de contas de adiantamento (fundo de caixa) e pagamentos diretos.
    - Como faz: Mapeia constantes em `models.TextChoices`.
    - Qual finalidade atende: Orienta a Tesouraria sobre quem deve receber a transferência PIX no Banco Cora PJ.
    """

    REEMBOLSO = 'REEMBOLSO', 'Reembolso (Desembolso do Voluntário)'
    FUNDO_CAIXA = 'FUNDO_CAIXA', 'Prestação de Contas de Fundo de Caixa'
    PAGAMENTO_DIRETO = 'PAGAMENTO_DIRETO', 'Pagamento Direto a Fornecedor'


class FormaPagamentoOriginal(models.TextChoices):
    """
    Meio de pagamento utilizado pelo voluntário no estabelecimento comercial na ponta.

    - O que faz: Registra como a compra foi paga originalmente na loja, mercado ou posto de combustível.
    - Como faz: Utiliza `models.TextChoices` com os meios de pagamento usuais (PIX, cartões, espécie, boleto).
    - Qual finalidade atende: Auxilia a conciliação entre o cupom fiscal anexado e o comprovante de desembolso do voluntário.
    """

    PIX = 'PIX', 'PIX'
    CARTAO_DEBITO = 'CARTAO_DEBITO', 'Cartão de Débito'
    CARTAO_CREDITO = 'CARTAO_CREDITO', 'Cartão de Crédito'
    ESPECIE = 'ESPECIE', 'Dinheiro em Espécie'
    BOLETO = 'BOLETO', 'Boleto Bancário'


class Despesa(models.Model):
    """
    Entidade central de domínio que representa uma despesa, prestação de contas ou pedido de reembolso.

    - O que faz: Gerencia os dados financeiros, anexos comprobatórios e transições de estado de cada gasto das 15 coordenações.
    - Como faz: Concentra as regras de negócio RN01 a RN06 em métodos transacionais (`@transaction.atomic`) e bloqueia
      mutações indevidas em `clean()` e `save()`.
    - Qual finalidade atende: Substitui o fluxo informal de notas em papel e mensagens de WhatsApp por um processo
      auditável, com controle de teto em tempo real e conciliação bancária Cora PJ.
    """

    CAMPOS_IMUTAVEIS_POS_DECISAO = (
        'valor',
        'coordenacao_id',
        'data_despesa',
        'solicitante_id',
        'titulo',
        'categoria',
        'tipo',
        'forma_pagamento_original',
    )

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
        """
        Retorna o resumo textual da despesa.

        - O que faz: Exibe a sigla da coordenação, o título, o valor monetário e o status legível.
        - Como faz: Formata uma string com os atributos principais da instância.
        - Qual finalidade atende: Facilita a identificação imediata do lançamento no Admin e em logs.
        """
        return f"[{self.coordenacao.sigla}] {self.titulo} - R$ {self.valor} ({self.get_status_display()})"

    def _validar_imutabilidade_rn05(self):
        """
        Verifica e bloqueia alterações em campos contábeis após aprovação ou pagamento (RN05).

        - O que faz: Impede que despesas já `APROVADO` ou `PAGO` no banco tenham seu valor, coordenação,
          data, solicitante ou classificação adulterados, ou que uma despesa `PAGO` mude de status.
        - Como faz: Consulta o estado persistido no banco (`Despesa.objects.get(pk=self.pk)`) e compara os
          atributos protegidos em `CAMPOS_IMUTAVEIS_POS_DECISAO`, lançando `ValidationError` se houver divergência.
        - Qual finalidade atende: Garante a imutabilidade pós-decisão (RN05) e protege a integridade contábil
          da prestação de contas auditada pela Diretoria do Grupo Escoteiro Caramuru.
        """
        if not self.pk:
            return

        original = Despesa.objects.filter(pk=self.pk).first()
        if not original:
            return

        if original.status in (StatusDespesa.APROVADO, StatusDespesa.PAGO):
            for campo in self.CAMPOS_IMUTAVEIS_POS_DECISAO:
                if getattr(self, campo) != getattr(original, campo):
                    raise ValidationError(
                        f"RN05 (Imutabilidade Pós-Decisão): Não é permitido alterar o campo '{campo}' "
                        f"de uma despesa no estado '{original.get_status_display()}'."
                    )

            if original.status == StatusDespesa.PAGO and self.status != StatusDespesa.PAGO:
                raise ValidationError(
                    "RN05 (Imutabilidade Pós-Decisão): Uma despesa já liquidada (PAGO) não pode ter seu status revertido."
                )

    def clean(self):
        """
        Executa as validações de integridade de domínio da Despesa antes da persistência.

        - O que faz: Valida a presença obrigatória de comprovante fiscal fora de rascunho (RN01),
          a justificativa obrigatória em reprovações (RN04) e a imutabilidade pós-decisão (RN05).
        - Como faz: Sobrescreve `Model.clean()`, invoca `_validar_imutabilidade_rn05()` e levanta `ValidationError`
          estruturado por campo quando alguma invariante é violada.
        - Qual finalidade atende: Impede que formulários ou chamadas de modelo persistam estados contábeis inválidos.
        """
        super().clean()
        self._validar_imutabilidade_rn05()

        # RN01: Obrigatoriedade do comprovante para envio
        if self.status != StatusDespesa.RASCUNHO and not self.comprovante:
            raise ValidationError({'comprovante': 'O comprovante fiscal é obrigatório para envio.'})

        # RN04: Justificativa obrigatória em rejeição
        if self.status == StatusDespesa.REJEITADO and not self.motivo_rejeicao:
            raise ValidationError({'motivo_rejeicao': 'É obrigatório informar o motivo da reprovação.'})

    def save(self, *args, **kwargs):
        """
        Persiste a instância da Despesa garantindo a verificação prévia de imutabilidade (RN05).

        - O que faz: Executa a validação de imutabilidade pós-decisão antes de delegar ao `super().save()`.
        - Como faz: Chama `self._validar_imutabilidade_rn05()` em toda operação de gravação no banco.
        - Qual finalidade atende: Garante que mesmo chamadas diretas a `.save()` via código Python respeitem a RN05.
        """
        self._validar_imutabilidade_rn05()
        return super().save(*args, **kwargs)

    def _registrar_transicao(self, status_anterior, novo_status, usuario, observacao=''):
        """
        Grava um registro imutável na trilha de auditoria da despesa (RN06).

        - O que faz: Insere uma nova linha em `HistoricoTransicaoStatus` documentando quem mudou o status e quando.
        - Como faz: Instancia `HistoricoTransicaoStatus.objects.create(...)` dentro do escopo transacional da transição.
        - Qual finalidade atende: Atende à RN06 (Auditoria Imutável de Transições) para rastreabilidade completa da Tesouraria.
        """
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
        Submete uma despesa de RASCUNHO (ou REJEITADO corrigido) para a fila de triagem (ENVIADO).

        - O que faz: Valida a presença de anexo fiscal (RN01), calcula se o gasto ultrapassa o saldo livre
          da coordenação (Soft-block RN02), atualiza o status para `ENVIADO` e registra auditoria (RN06).
        - Como faz: Opera sob `@transaction.atomic`, compara `self.valor` com `self.coordenacao.saldo_disponivel`
          usando `Decimal` e persiste o alerta `excede_teto` e `valor_excedente`.
        - Qual finalidade atende: Permite que voluntários enviem compras urgentes de campo sem travar a operação,
          mas alertando visualmente a Tesouraria sobre qualquer estouro de teto orçamentário.
        """
        if not self.comprovante:
            raise ValidationError("Não é possível submeter a despesa sem anexar o comprovante fiscal.")

        status_anterior = self.status
        if status_anterior not in (StatusDespesa.RASCUNHO, StatusDespesa.REJEITADO):
            raise ValidationError(f"Despesa em estado '{self.get_status_display()}' não pode ser submetida.")

        # RN02: Cálculo de soft-block de estouro
        saldo_livre = self.coordenacao.saldo_disponivel
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
        Aprova a despesa na triagem financeira e a habilita para liquidação bancária.

        - O que faz: Transiciona a despesa de `ENVIADO` para `APROVADO`, aplicando a Segregação de Funções (RN03).
        - Como faz: Verifica dentro de `@transaction.atomic` se `self.solicitante_id != tesoureiro.id` (exceto superuser),
          registra o autor e timestamp da análise e grava o log de auditoria (RN06).
        - Qual finalidade atende: Garante conformidade e governança financeira (RN03), impedindo auto-aprovação de reembolsos.
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
        Reprova uma despesa enviada na triagem mediante justificativa obrigatória (RN04).

        - O que faz: Transiciona a despesa de `ENVIADO` para `REJEITADO`, liberando o saldo comprometido da coordenação.
        - Como faz: Exige `motivo` não vazio (RN04), valida segregação de funções (RN03), persiste a justificativa
          e grava o histórico de transição (RN06) sob `@transaction.atomic`.
        - Qual finalidade atende: Permite que o coordenador de campo saiba exatamente por que sua nota foi recusada
          (ex: foto ilegível ou item não autorizado) e possa corrigi-la.
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
        Liquida a despesa como PAGO após transferência PIX na conta do Banco Cora PJ.

        - O que faz: Transiciona a despesa de `APROVADO` para `PAGO`, registrando o pagador, a data/hora e o comprovante bancário.
        - Como faz: Valida que o status atual é `APROVADO`, atualiza os metadados de pagamento e grava auditoria (RN06).
        - Qual finalidade atende: Encerra o ciclo financeiro da despesa com lastro documental para a prestação de contas final do evento.
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
    Tabela imutável de log de auditoria de todas as mudanças de estado das despesas (RN06).

    - O que faz: Armazena cada transição de status (`status_anterior` -> `novo_status`), autor, timestamp UTC e observação.
    - Como faz: Vincula-se à `Despesa` e ao `Usuario` autor da ação com campos somente-leitura na administração.
    - Qual finalidade atende: Cumpre a RN06 (Auditoria Imutável de Transições), assegurando transparência total
      para o Conselho Fiscal do Grupo Escoteiro Caramuru.
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
        """
        Retorna a descrição textual da linha de auditoria.

        - O que faz: Mostra o ID da despesa, a transição realizada e o username do responsável.
        - Como faz: Formata os atributos `despesa.id`, `status_anterior`, `novo_status` e `alterado_por.username`.
        - Qual finalidade atende: Facilita a leitura rápida da trilha de auditoria no painel administrativo.
        """
        return f"{self.despesa.id}: {self.status_anterior} -> {self.novo_status} por {self.alterado_por.username}"
