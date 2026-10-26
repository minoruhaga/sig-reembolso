from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone

from apps.despesas.models import Despesa, HistoricoTransicaoStatus, StatusDespesa
from apps.financeiro.models import Coordenacao
from apps.usuarios.models import PapelUsuario, Usuario


class DespesaRegrasNegocioTestCase(TestCase):
    """
    Suíte de testes unitários automatizados para validação das regras de negócio contábeis (RN01 a RN06).

    - O que faz: Verifica o comportamento estrito da máquina de estados e das invariantes financeiras da entidade `Despesa`.
    - Como faz: Isola cenários de teste com `django.test.TestCase`, simulando coordenações, solicitantes, tesoureiros e anexos.
    - Qual finalidade atende: Previne regressões nas regras críticas de domínio exigidas pelo edital de LES (Item 3.i).
    """

    def setUp(self):
        """
        Prepara a massa de dados base em memória antes de cada teste unitário.

        - O que faz: Instancia uma coordenação com teto de R$ 500,00, um usuário coordenador, um tesoureiro e um comprovante simulado.
        - Como faz: Utiliza `objects.create` e `SimpleUploadedFile` dentro do banco transacional de testes do Django.
        - Qual finalidade atende: Garante independência e reprodutibilidade determinística entre os testes de RN01 a RN06.
        """
        self.coordenacao = Coordenacao.objects.create(
            nome='Alimentação e Cozinha Central',
            sigla='ALIM',
            teto_orcamentario=Decimal('500.00')
        )

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

        self.comprovante_fake = SimpleUploadedFile(
            "cupom.jpg",
            b"fake_image_content",
            content_type="image/jpeg"
        )

    def test_rn01_submissao_sem_comprovante_lanca_excecao(self):
        """
        Verifica a aplicação da RN01 (Obrigatoriedade de Comprovante Fiscal).

        - O que faz: Tenta submeter uma despesa em rascunho sem arquivo de comprovante anexado.
        - Como faz: Chama `despesa.submeter()` sem `comprovante` e valida o disparo de `ValidationError`.
        - Qual finalidade atende: Impede pedidos de reembolso sem lastro documental fiscal no AG VII.
        """
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
        """
        Verifica a aplicação da RN02 (Soft-block de Estouro de Teto Orçamentário).

        - O que faz: Submete uma despesa de R$ 600,00 em uma coordenação com saldo livre de R$ 500,00.
        - Como faz: Executa `despesa.submeter()` e confere se `excede_teto` passa a `True` e `valor_excedente` é `Decimal('100.00')`.
        - Qual finalidade atende: Garante que compras emergenciais de campo não sejam bloqueadas, mas cheguem marcadas com alerta à Tesouraria.
        """
        despesa = Despesa.objects.create(
            coordenacao=self.coordenacao,
            solicitante=self.solicitante,
            titulo='Compra Urgente Acima do Teto',
            valor=Decimal('600.00'),
            data_despesa=timezone.now().date(),
            comprovante=self.comprovante_fake,
            status=StatusDespesa.RASCUNHO
        )
        despesa.submeter(self.solicitante)
        self.assertEqual(despesa.status, StatusDespesa.ENVIADO)
        self.assertTrue(despesa.excede_teto)
        self.assertEqual(despesa.valor_excedente, Decimal('100.00'))

    def test_rn03_segregacao_de_funcoes_bloqueia_auto_aprovacao(self):
        """
        Verifica a aplicação da RN03 (Segregação de Funções na Triagem).

        - O que faz: Tenta aprovar uma despesa cujo solicitante é o próprio tesoureiro avaliador.
        - Como faz: Chama `despesa_propria.aprovar(self.tesoureiro)` e verifica a ocorrência de `ValidationError`.
        - Qual finalidade atende: Evita conflito de interesses e fraude interna na liberação de reembolsos.
        """
        despesa_propria = Despesa.objects.create(
            coordenacao=self.coordenacao,
            solicitante=self.tesoureiro,
            titulo='Gasolina comprada pelo tesoureiro',
            valor=Decimal('80.00'),
            data_despesa=timezone.now().date(),
            comprovante=self.comprovante_fake,
            status=StatusDespesa.ENVIADO
        )
        with self.assertRaises(ValidationError):
            despesa_propria.aprovar(self.tesoureiro)

    def test_rn04_rejeicao_sem_motivo_lanca_excecao(self):
        """
        Verifica a aplicação da RN04 (Justificativa Obrigatória em Rejeição).

        - O que faz: Tenta rejeitar uma despesa enviando motivo vazio.
        - Como faz: Invoca `despesa.rejeitar(self.tesoureiro, motivo="")` esperando `ValidationError`.
        - Qual finalidade atende: Garante feedback claro ao voluntário de campo para correção de notas recusadas.
        """
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

    def test_rn05_imutabilidade_pos_decisao(self):
        """
        Verifica a aplicação da RN05 (Imutabilidade Pós-Decisão para despesas APROVADO ou PAGO).

        - O que faz: Aprova uma despesa e tenta alterar seu valor monetário; em seguida liquida como PAGO e tenta alterar título ou reverter status.
        - Como faz: Chama `aprovar()`, modifica `despesa.valor` e verifica `ValidationError` em `save()`; depois chama `liquidar()` e verifica bloqueio de edição.
        - Qual finalidade atende: Protege a integridade contábil impedindo adulteração de valores ou datas após a aprovação da Tesouraria.
        """
        despesa = Despesa.objects.create(
            coordenacao=self.coordenacao,
            solicitante=self.solicitante,
            titulo='Compra de Lonas',
            valor=Decimal('200.00'),
            data_despesa=timezone.now().date(),
            comprovante=self.comprovante_fake,
            status=StatusDespesa.RASCUNHO
        )
        despesa.submeter(self.solicitante)
        despesa.aprovar(self.tesoureiro)

        # Tentativa de adulterar o valor após APROVADO deve falhar
        despesa.valor = Decimal('450.00')
        with self.assertRaises(ValidationError):
            despesa.save()

        # Recarrega o estado íntegro do banco e liquida para PAGO (transição legítima permitida)
        despesa.refresh_from_db()
        despesa.liquidar(self.tesoureiro)
        self.assertEqual(despesa.status, StatusDespesa.PAGO)

        # Tentativa de alterar título ou reverter status após PAGO deve falhar
        despesa.titulo = 'Título Adulterado'
        with self.assertRaises(ValidationError):
            despesa.save()

    def test_rn06_auditoria_imutavel_registra_transicoes(self):
        """
        Verifica a aplicação da RN06 (Auditoria Imutável de Transições).

        - O que faz: Executa o ciclo completo (`RASCUNHO` -> `ENVIADO` -> `APROVADO` -> `PAGO`) e inspeciona a tabela de histórico.
        - Como faz: Filtra `HistoricoTransicaoStatus` pela despesa e comprova a criação exata dos 3 registros cronológicos.
        - Qual finalidade atende: Assegura rastreabilidade contábil ponta a ponta para prestação de contas do AG VII.
        """
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
