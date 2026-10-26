from decimal import Decimal
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone

from apps.usuarios.models import Usuario, PapelUsuario
from apps.financeiro.models import Coordenacao
from apps.despesas.models import Despesa, StatusDespesa, CategoriaDespesa, HistoricoTransicaoStatus


class DespesaRegrasNegocioTestCase(TestCase):
    def setUp(self):
        # 1. Cria coordenação com teto de R$ 500,00
        self.coordenacao = Coordenacao.objects.create(
            nome='Alimentação e Cozinha Central',
            sigla='ALIM',
            teto_orcamentario=Decimal('500.00')
        )

        # 2. Usuários
        self.solicitante = Usuario.objects.create_user(
            username='coordenador1',
            password='pass',
            papel=PapelUsuario.COORDENADOR
        )
        self.tesoureiro = Usuario.objects.create_user(
            username='tesoureiro1',
            password='pass',
            papel=PapelUsuario.TESOUREIRO
        )

        # 3. Arquivo fake para comprovante
        self.comprovante_fake = SimpleUploadedFile(
            "cupom.jpg",
            b"fake_image_content",
            content_type="image/jpeg"
        )

    def test_rn01_submissao_sem_comprovante_lanca_excecao(self):
        """RN01: Submissão sem comprovante deve ser bloqueada."""
        despesa = Despesa.objects.create(
            coordenacao=self.coordenacao,
            solicitante=self.solicitante,
            titulo='Compra de Verduras',
            valor=Decimal('100.00'),
            data_despesa=timezone.now().date(),
            status=StatusDespesa.RASCUNHO
        )
        with self.assertRaises(ValidationError):
            despesa.submeter(self.solicitante)

    def test_rn02_softblock_estouro_orcamentario(self):
        """RN02: Despesa que supera saldo disponível marca excede_teto = True."""
        despesa = Despesa.objects.create(
            coordenacao=self.coordenacao,
            solicitante=self.solicitante,
            titulo='Compra Urgente Acima do Teto',
            valor=Decimal('600.00'),  # Teto é 500.00
            data_despesa=timezone.now().date(),
            comprovante=self.comprovante_fake,
            status=StatusDespesa.RASCUNHO
        )
        despesa.submeter(self.solicitante)
        self.assertEqual(despesa.status, StatusDespesa.ENVIADO)
        self.assertTrue(despesa.excede_teto)
        self.assertEqual(despesa.valor_excedente, Decimal('100.00'))

    def test_rn03_segregacao_de_funcoes_bloqueia_auto_aprovacao(self):
        """RN03: Tesoureiro não pode aprovar ou rejeitar suas próprias despesas."""
        despesa_propria = Despesa.objects.create(
            coordenacao=self.coordenacao,
            solicitante=self.tesoureiro,  # Próprio tesoureiro é o solicitante
            titulo='Gasolina comprada pelo tesoureiro',
            valor=Decimal('80.00'),
            data_despesa=timezone.now().date(),
            comprovante=self.comprovante_fake,
            status=StatusDespesa.ENVIADO
        )
        with self.assertRaises(ValidationError):
            despesa_propria.aprovar(self.tesoureiro)

    def test_rn04_rejeicao_sem_motivo_lanca_excecao(self):
        """RN04: Reprovação sem justificativa deve ser rejeitada."""
        despesa = Despesa.objects.create(
            coordenacao=self.coordenacao,
            solicitante=self.solicitante,
            titulo='Despesa Questionável',
            valor=Decimal('50.00'),
            data_despesa=timezone.now().date(),
            comprovante=self.comprovante_fake,
            status=StatusDespesa.ENVIADO
        )
        with self.assertRaises(ValidationError):
            despesa.rejeitar(self.tesoureiro, motivo="")

    def test_rn06_auditoria_imutavel_registra_transicoes(self):
        """RN06: Todas as transições geram registros em HistoricoTransicaoStatus."""
        despesa = Despesa.objects.create(
            coordenacao=self.coordenacao,
            solicitante=self.solicitante,
            titulo='Compra de Gás',
            valor=Decimal('120.00'),
            data_despesa=timezone.now().date(),
            comprovante=self.comprovante_fake,
            status=StatusDespesa.RASCUNHO
        )
        despesa.submeter(self.solicitante)
        despesa.aprovar(self.tesoureiro)
        despesa.liquidar(self.tesoureiro)

        historico = HistoricoTransicaoStatus.objects.filter(despesa=despesa).order_by('data_hora')
        self.assertEqual(historico.count(), 3)
        self.assertEqual(historico[0].novo_status, StatusDespesa.ENVIADO)
        self.assertEqual(historico[1].novo_status, StatusDespesa.APROVADO)
        self.assertEqual(historico[2].novo_status, StatusDespesa.PAGO)
