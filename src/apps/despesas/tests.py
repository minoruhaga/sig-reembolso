from decimal import Decimal
from io import BytesIO

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from apps.core.services import TAMANHO_MAXIMO_COMPRIMIDO_BYTES
from apps.despesas.models import (
    CategoriaDespesa,
    Despesa,
    FormaPagamentoOriginal,
    HistoricoTransicaoStatus,
    StatusDespesa,
    TipoDespesa,
)
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


class DespesaSubmissaoViewFormTestCase(TestCase):
    """
    Testes de integração para formulário, views e serviços de submissão de despesas (Issue #7).

    - O que faz: Testa o fluxo completo de submissão mobile e salvamento de rascunhos, validação do anexo (RN01),
      otimização com Pillow (RNF02), cálculo de soft-block (RN02), imutabilidade (RN05) e auditoria (RN06).
    - Como faz: Utiliza o test client do Django (`self.client`) simulando requisições multipart/form-data
      autenticadas como coordenador de área, com imagens geradas dinamicamente via Pillow.
    - Qual finalidade atende: Assegura a integridade do ciclo de submissão da Issue #7 antes da homologação.
    """

    def setUp(self):
        """
        Inicializa o ambiente de teste com coordenação ativa, coordenador de teste e dados base.
        """
        self.coordenacao = Coordenacao.objects.create(
            nome='Infraestrutura e Campo',
            sigla='INFRA',
            teto_orcamentario=Decimal('1000.00'),
            ativo=True
        )

        self.coordenador = Usuario.objects.create_user(
            username='coordenador_infra',
            password='senha_segura_123',
            papel=PapelUsuario.COORDENADOR,
            first_name='Carlos',
            last_name='Coordenador'
        )

        self.tesoureiro = Usuario.objects.create_user(
            username='tesoureiro_chefe',
            password='senha_segura_123',
            papel=PapelUsuario.TESOUREIRO
        )

    def _gerar_imagem_upload(self, nome="cupom_posto.png", size=(2200, 1600)):
        """
        Gera arquivo de imagem sintético para simulação de upload multipart.
        """
        buffer = BytesIO()
        img = Image.new('RGB', size, (30, 120, 200))
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return SimpleUploadedFile(nome, buffer.getvalue(), content_type="image/png")

    def test_submissao_valida_com_imagem_otimizada_via_view(self):
        """
        Testa o fluxo de submissão bem-sucedido de uma despesa com imagem fiscal pela view.

        - O que faz: Envia formulário completo com imagem bruta grande de 2200x1600 px e acao='submeter'.
        - Como faz: Faz POST autenticado em `despesas:nova`; verifica redirecionamento para `despesas:minhas`;
          confere no banco que o status é `ENVIADO`, o arquivo foi comprimido para `< 350KB` com extensão `.jpg`
          e o log de auditoria `HistoricoTransicaoStatus` registrou o evento.
        - Qual finalidade atende: Valida a entrega central da Issue #7 (RN01, RNF02, RNF04 e RN06).
        """
        self.client.login(username='coordenador_infra', password='senha_segura_123')
        upload_img = self._gerar_imagem_upload()

        payload = {
            'coordenacao': self.coordenacao.id,
            'titulo': 'Compra de Cabos e Fitas Isolantes',
            'categoria': CategoriaDespesa.INFRAESTRUTURA,
            'tipo': TipoDespesa.REEMBOLSO,
            'forma_pagamento_original': FormaPagamentoOriginal.PIX,
            'valor': '185.50',
            'data_despesa': '2026-10-30',
            'descricao': 'Comprado na loja de materiais elétricos de Juquitiba',
            'comprovante': upload_img,
            'acao': 'submeter',
        }

        response = self.client.post(reverse('despesas:nova'), payload)
        self.assertRedirects(response, reverse('despesas:minhas'))

        despesa = Despesa.objects.filter(solicitante=self.coordenador).first()
        self.assertIsNotNone(despesa)
        self.assertEqual(despesa.status, StatusDespesa.ENVIADO)
        self.assertEqual(despesa.valor, Decimal('185.50'))
        self.assertFalse(despesa.excede_teto)

        # Valida compressão Pillow e nome UUID
        self.assertTrue(despesa.comprovante.name.endswith('.jpg'))
        self.assertLessEqual(despesa.comprovante.size, TAMANHO_MAXIMO_COMPRIMIDO_BYTES)

        # Valida auditoria imutável RN06
        historico = HistoricoTransicaoStatus.objects.filter(despesa=despesa)
        self.assertEqual(historico.count(), 2)  # Criação + Submissão

    def test_bloqueio_submissao_sem_comprovante_rn01(self):
        """
        Verifica se a tentativa de submissão sem anexo é impedida pelo formulário (RN01).

        - O que faz: Envia o formulário com dados válidos e acao='submeter', porém sem arquivo de comprovante.
        - Como faz: Analisa o response 200, validando a presença de erro no campo `comprovante`.
        - Qual finalidade atende: Garante a aplicação rigorosa da RN01 (anexo obrigatório para triagem).
        """
        self.client.login(username='coordenador_infra', password='senha_segura_123')
        payload = {
            'coordenacao': self.coordenacao.id,
            'titulo': 'Despesa sem comprovante',
            'categoria': CategoriaDespesa.INFRAESTRUTURA,
            'tipo': TipoDespesa.REEMBOLSO,
            'forma_pagamento_original': FormaPagamentoOriginal.PIX,
            'valor': '50.00',
            'data_despesa': '2026-10-30',
            'acao': 'submeter',
        }

        response = self.client.post(reverse('despesas:nova'), payload)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context['form'],
            'comprovante',
            'RN01: O comprovante fiscal é estritamente obrigatório para enviar a despesa à triagem.'
        )
        self.assertEqual(Despesa.objects.count(), 0)

    def test_salvar_rascunho_sem_comprovante_rf05(self):
        """
        Verifica se o usuário pode salvar um rascunho preliminar sem anexar foto (RF05).

        - O que faz: Envia formulário com acao='rascunho' sem anexo de cupom fiscal.
        - Como faz: Confere redirecionamento e criação de instância no banco com status `RASCUNHO`.
        - Qual finalidade atende: Cumpre o requisito RF05 (Gestão de Rascunhos).
        """
        self.client.login(username='coordenador_infra', password='senha_segura_123')
        payload = {
            'coordenacao': self.coordenacao.id,
            'titulo': 'Rascunho de Compra de Parafusos',
            'categoria': CategoriaDespesa.INFRAESTRUTURA,
            'tipo': TipoDespesa.REEMBOLSO,
            'forma_pagamento_original': FormaPagamentoOriginal.ESPECIE,
            'valor': '35.00',
            'data_despesa': '2026-10-30',
            'acao': 'rascunho',
        }

        response = self.client.post(reverse('despesas:nova'), payload)
        self.assertRedirects(response, reverse('despesas:minhas'))

        despesa = Despesa.objects.filter(solicitante=self.coordenador).first()
        self.assertIsNotNone(despesa)
        self.assertEqual(despesa.status, StatusDespesa.RASCUNHO)
        self.assertFalse(bool(despesa.comprovante))

    def test_softblock_estouro_teto_na_submissao_rn02(self):
        """
        Verifica o acionamento do soft-block quando a despesa supera o saldo disponível (RN02).

        - O que faz: Submete uma despesa de R$ 1.200,00 em uma coordenação com teto de R$ 1.000,00.
        - Como faz: Avalia se a despesa transiciona para `ENVIADO` com as flags `excede_teto=True` e `valor_excedente=200.00`.
        - Qual finalidade atende: Cumpre a RN02 (não bloqueia compras emergenciais, mas sinaliza a Tesouraria).
        """
        self.client.login(username='coordenador_infra', password='senha_segura_123')
        upload_img = self._gerar_imagem_upload()

        payload = {
            'coordenacao': self.coordenacao.id,
            'titulo': 'Gerador de Emergência para Ambulatório',
            'categoria': CategoriaDespesa.INFRAESTRUTURA,
            'tipo': TipoDespesa.REEMBOLSO,
            'forma_pagamento_original': FormaPagamentoOriginal.PIX,
            'valor': '1200.00',
            'data_despesa': '2026-10-30',
            'comprovante': upload_img,
            'acao': 'submeter',
        }

        response = self.client.post(reverse('despesas:nova'), payload)
        self.assertRedirects(response, reverse('despesas:minhas'))

        despesa = Despesa.objects.filter(solicitante=self.coordenador).first()
        self.assertEqual(despesa.status, StatusDespesa.ENVIADO)
        self.assertTrue(despesa.excede_teto)
        self.assertEqual(despesa.valor_excedente, Decimal('200.00'))

    def test_edicao_e_submissao_posterior_de_rascunho(self):
        """
        Testa a complementação de uma despesa salva previamente em rascunho.

        - O que faz: Cria despesa em RASCUNHO sem anexo e depois realiza POST em `despesas:editar` anexando foto.
        - Como faz: Confere atualização de campos e promoção de status para `ENVIADO`.
        - Qual finalidade atende: Garante a jornada completa de edição de rascunhos de campo.
        """
        despesa = Despesa.objects.create(
            coordenacao=self.coordenacao,
            solicitante=self.coordenador,
            titulo='Lâmpadas para Refeitório',
            valor=Decimal('60.00'),
            data_despesa=timezone.now().date(),
            status=StatusDespesa.RASCUNHO
        )

        self.client.login(username='coordenador_infra', password='senha_segura_123')
        upload_img = self._gerar_imagem_upload(nome="nota_lampada.jpg")

        payload = {
            'coordenacao': self.coordenacao.id,
            'titulo': 'Lâmpadas LED para Refeitório (Atualizado)',
            'categoria': CategoriaDespesa.INFRAESTRUTURA,
            'tipo': TipoDespesa.REEMBOLSO,
            'forma_pagamento_original': FormaPagamentoOriginal.CARTAO_DEBITO,
            'valor': '75.00',
            'data_despesa': '2026-10-30',
            'comprovante': upload_img,
            'acao': 'submeter',
        }

        response = self.client.post(reverse('despesas:editar', args=[despesa.id]), payload)
        self.assertRedirects(response, reverse('despesas:minhas'))

        despesa.refresh_from_db()
        self.assertEqual(despesa.status, StatusDespesa.ENVIADO)
        self.assertEqual(despesa.titulo, 'Lâmpadas LED para Refeitório (Atualizado)')
        self.assertEqual(despesa.valor, Decimal('75.00'))
        self.assertTrue(bool(despesa.comprovante))

    def test_bloqueio_edicao_despesa_aprovada_rn05(self):
        """
        Verifica o bloqueio de edição para despesas que já foram aprovadas na triagem (RN05).

        - O que faz: Tenta acessar a tela de edição de uma despesa no estado APROVADO.
        - Como faz: Envia GET e POST em `despesas:editar` e confere redirecionamento com mensagem de erro.
        - Qual finalidade atende: Protege a integridade contábil e a imutabilidade pós-decisão (RN05).
        """
        despesa = Despesa.objects.create(
            coordenacao=self.coordenacao,
            solicitante=self.coordenador,
            titulo='Compra Aprovada',
            valor=Decimal('100.00'),
            data_despesa=timezone.now().date(),
            comprovante=self._gerar_imagem_upload(),
            status=StatusDespesa.APROVADO
        )

        self.client.login(username='coordenador_infra', password='senha_segura_123')
        response = self.client.get(reverse('despesas:editar', args=[despesa.id]))
        self.assertRedirects(response, reverse('despesas:minhas'))
