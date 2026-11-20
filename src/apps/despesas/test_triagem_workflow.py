import shutil
import tempfile
from decimal import Decimal
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from apps.core.services import TAMANHO_MAXIMO_COMPRIMIDO_BYTES
from apps.despesas.models import Despesa, HistoricoTransicaoStatus, StatusDespesa
from apps.financeiro.models import Coordenacao
from apps.usuarios.models import PapelUsuario, Usuario


class TriagemWorkflowTestCase(TestCase):
    """
    Suíte de testes integrados para o workflow de triagem e liquidação da Tesouraria (Issue #11).

    - O que faz: Valida acesso RBAC ao painel de triagem e o ciclo completo dos endpoints de ação
      (`aprovar`, `rejeitar` com parecer RN04, e `liquidar` com anexo Cora PJ), além da segregação RN03.
    - Como faz: Utiliza `self.client` com requisições GET/POST multipart em diretório de mídia temporário.
    - Qual finalidade atende: Garante que a fila financeira da Tesouraria opere com segurança, atomicidade
      e auditoria imutável antes da entrega à banca.
    """

    def setUp(self):
        """
        Prepara ambiente isolado com pasta, coordenador, dois tesoureiros e diretório temporário de mídia.

        - O que faz: Cria `ALIM` (teto R$ 1.000,00), coordenador solicitante e dois tesoureiros para testar RN03.
        - Como faz: Usa `Coordenacao.objects.create`, `Usuario.objects.create_user` e `tempfile.mkdtemp()`.
        - Qual finalidade atende: Assegura testes determinísticos sem poluir `src/media/`.
        """
        self.temp_media = tempfile.mkdtemp()
        self.coordenacao = Coordenacao.objects.create(
            nome='Alimentação e Cozinha Central',
            sigla='ALIM',
            teto_orcamentario=Decimal('1000.00'),
        )
        self.coordenador = Usuario.objects.create_user(
            username='coord_triagem',
            password='pass123',  # nosec B106
            papel=PapelUsuario.COORDENADOR,
            coordenacao=self.coordenacao,
            chave_pix='coord@pix.com',
        )
        self.tesoureiro = Usuario.objects.create_user(
            username='tesoureiro_principal',
            password='pass123',  # nosec B106
            papel=PapelUsuario.TESOUREIRO,
            is_staff=True,
        )
        self.outro_tesoureiro = Usuario.objects.create_user(
            username='tesoureiro_segundo',
            password='pass123',  # nosec B106
            papel=PapelUsuario.TESOUREIRO,
            is_staff=True,
        )

    def tearDown(self):
        """
        Remove o diretório temporário de mídia após cada teste.

        - O que faz: Exclui arquivos gerados durante a suíte.
        - Como faz: Chama `shutil.rmtree(self.temp_media, ignore_errors=True)`.
        - Qual finalidade atende: Mantém o ambiente limpo entre execuções.
        """
        shutil.rmtree(self.temp_media, ignore_errors=True)

    def _gerar_imagem(self, nome='comprovante.png', size=(600, 400)) -> SimpleUploadedFile:
        """
        Gera uma imagem PNG sintética para anexos de despesa e liquidação Cora PJ.

        - O que faz: Cria payload de imagem válido em memória.
        - Como faz: Usa Pillow para gerar imagem RGB em `BytesIO`.
        - Qual finalidade atende: Simula comprovantes fiscais e comprovantes bancários nos testes HTTP.
        """
        buf = BytesIO()
        Image.new('RGB', size, color=(40, 90, 150)).save(buf, format='PNG')
        return SimpleUploadedFile(nome, buf.getvalue(), content_type='image/png')

    def _criar_despesa_enviada(self, *, solicitante=None, valor=Decimal('250.00')) -> Despesa:
        """
        Cria e submete uma despesa para o estado `ENVIADO` pronta para triagem.

        - O que faz: Instancia e submete uma despesa com comprovante válido.
        - Como faz: Usa `Despesa.objects.create` e `despesa.submeter(...)`.
        - Qual finalidade atende: Reduz repetição de código nos testes de triagem.
        """
        autor = solicitante or self.coordenador
        despesa = Despesa.objects.create(
            coordenacao=self.coordenacao,
            solicitante=autor,
            titulo='Compra de Hortifrúti',
            valor=valor,
            data_despesa=timezone.now().date(),
            comprovante=self._gerar_imagem(),
            status=StatusDespesa.RASCUNHO,
        )
        despesa.submeter(autor)
        return despesa

    def test_coordenador_recebe_403_no_painel_e_acoes_triagem(self):
        """
        Garante que coordenadores de campo não acessam nem operam endpoints de triagem (RF01).

        - O que faz: Tenta GET em `triagem` e POST em `aprovar`, `rejeitar` e `liquidar` como coordenador.
        - Como faz: Autentica `self.coordenador` e confere HTTP 403 em todas as rotas de triagem.
        - Qual finalidade atende: Bloqueia qualquer elevação horizontal ou vertical de privilégio.
        """
        with override_settings(MEDIA_ROOT=self.temp_media):
            despesa = self._criar_despesa_enviada()
            self.client.force_login(self.coordenador)

            self.assertEqual(self.client.get(reverse('despesas:triagem')).status_code, 403)
            self.assertEqual(self.client.post(reverse('despesas:aprovar', args=[despesa.id])).status_code, 403)
            self.assertEqual(
                self.client.post(reverse('despesas:rejeitar', args=[despesa.id]), {'motivo_rejeicao': 'Teste'}).status_code,
                403,
            )
            self.assertEqual(
                self.client.post(
                    reverse('despesas:liquidar', args=[despesa.id]),
                    {'comprovante_pagamento': self._gerar_imagem('cora.png')},
                ).status_code,
                403,
            )

    def test_fluxo_aprovar_e_liquidar_com_comprovante_cora_pj(self):
        """
        Valida o ciclo completo da Tesouraria: visualizar fila, aprovar e liquidar com anexo Cora PJ.

        - O que faz: Executa GET na triagem (incluindo destaque de estouro RN02), POST para aprovar,
          falha esperada ao liquidar sem anexo, e liquidação válida com imagem comprimida por Pillow.
        - Como faz: Verifica transições `ENVIADO -> APROVADO -> PAGO`, timestamps, autores, tamanho < 350KB
          e entradas em `HistoricoTransicaoStatus`.
        - Qual finalidade atende: Comprova os critérios principais das Issues #11 (RF06 e RF07).
        """
        with override_settings(MEDIA_ROOT=self.temp_media):
            despesa = self._criar_despesa_enviada(valor=Decimal('1200.00'))  # Gera soft-block RN02 (+200.00)
            self.client.force_login(self.tesoureiro)

            # Painel exibe a despesa com badge de estouro e chave PIX
            painel = self.client.get(reverse('despesas:triagem'))
            self.assertEqual(painel.status_code, 200)
            self.assertContains(painel, 'ESTOURO DE TETO')
            self.assertContains(painel, 'coord@pix.com')

            # 1. Aprovar
            resp_aprovar = self.client.post(reverse('despesas:aprovar', args=[despesa.id]))
            self.assertRedirects(resp_aprovar, reverse('despesas:triagem'))
            despesa.refresh_from_db()
            self.assertEqual(despesa.status, StatusDespesa.APROVADO)
            self.assertEqual(despesa.analisado_por, self.tesoureiro)
            self.assertIsNotNone(despesa.analisado_em)

            # 2. Tentativa de liquidar sem comprovante Cora PJ deve manter APROVADO
            resp_sem_anexo = self.client.post(reverse('despesas:liquidar', args=[despesa.id]), {})
            self.assertRedirects(resp_sem_anexo, reverse('despesas:triagem'))
            despesa.refresh_from_db()
            self.assertEqual(despesa.status, StatusDespesa.APROVADO)

            # 3. Liquidar com anexo bancário Cora PJ
            resp_liquidar = self.client.post(
                reverse('despesas:liquidar', args=[despesa.id]),
                {'comprovante_pagamento': self._gerar_imagem('pix_cora.png', size=(2000, 1400))},
            )
            self.assertRedirects(resp_liquidar, reverse('despesas:triagem'))
            despesa.refresh_from_db()
            self.assertEqual(despesa.status, StatusDespesa.PAGO)
            self.assertEqual(despesa.pago_por, self.tesoureiro)
            self.assertIsNotNone(despesa.pago_em)
            self.assertTrue(despesa.comprovante_pagamento.name.endswith('.jpg'))
            self.assertLessEqual(despesa.comprovante_pagamento.size, TAMANHO_MAXIMO_COMPRIMIDO_BYTES)

            # Verifica trilha completa RN06: submissão + aprovação + liquidação
            self.assertEqual(HistoricoTransicaoStatus.objects.filter(despesa=despesa).count(), 3)

    def test_rejeitar_exige_justificativa_obrigatoria_rn04_e_libera_saldo(self):
        """
        Valida a obrigatoriedade de motivo na rejeição via modal/endpoint e liberação de saldo (RN04).

        - O que faz: Tenta rejeitar com texto vazio/espaços (deve manter `ENVIADO`) e depois envia
          justificativa válida (deve mudar para `REJEITADO` e zerar comprometimento da coordenação).
        - Como faz: Envia POST para `despesas:rejeitar` e inspeciona estado, `motivo_rejeicao` e saldo.
        - Qual finalidade atende: Garante conformidade da interface de triagem com a RN04.
        """
        with override_settings(MEDIA_ROOT=self.temp_media):
            despesa = self._criar_despesa_enviada(valor=Decimal('300.00'))
            self.assertEqual(self.coordenacao.saldo_disponivel, Decimal('700.00'))

            self.client.force_login(self.tesoureiro)

            # Motivo em branco não muda status
            self.client.post(reverse('despesas:rejeitar', args=[despesa.id]), {'motivo_rejeicao': '   '})
            despesa.refresh_from_db()
            self.assertEqual(despesa.status, StatusDespesa.ENVIADO)

            # Motivo válido rejeita e libera o saldo
            self.client.post(
                reverse('despesas:rejeitar', args=[despesa.id]),
                {'motivo_rejeicao': 'Foto do CNPJ está cortada.'},
            )
            despesa.refresh_from_db()
            self.assertEqual(despesa.status, StatusDespesa.REJEITADO)
            self.assertEqual(despesa.motivo_rejeicao, 'Foto do CNPJ está cortada.')
            self.assertEqual(self.coordenacao.saldo_disponivel, Decimal('1000.00'))

    def test_rn03_segregacao_de_funcoes_bloqueia_auto_triagem_nos_endpoints(self):
        """
        Verifica que a segregação de funções (RN03) impede auto-aprovação, auto-rejeição e auto-liquidação.

        - O que faz: Cria despesa solicitada por `tesoureiro`, tenta aprovar/rejeitar com o próprio e depois
          permite aprovação e liquidação por `outro_tesoureiro`, bloqueando apenas auto-liquidação final.
        - Como faz: Faz POST nos endpoints com ambos os usuários e valida o estado após cada tentativa.
        - Qual finalidade atende: Blindagem completa contra conflito de interesse nos endpoints web.
        """
        with override_settings(MEDIA_ROOT=self.temp_media):
            despesa = self._criar_despesa_enviada(solicitante=self.tesoureiro, valor=Decimal('90.00'))

            # O próprio solicitante (mesmo tesoureiro) não pode aprovar nem rejeitar
            self.client.force_login(self.tesoureiro)
            self.client.post(reverse('despesas:aprovar', args=[despesa.id]))
            despesa.refresh_from_db()
            self.assertEqual(despesa.status, StatusDespesa.ENVIADO)

            self.client.post(reverse('despesas:rejeitar', args=[despesa.id]), {'motivo_rejeicao': 'Auto rejeição'})
            despesa.refresh_from_db()
            self.assertEqual(despesa.status, StatusDespesa.ENVIADO)

            # Outro tesoureiro pode aprovar
            self.client.force_login(self.outro_tesoureiro)
            self.client.post(reverse('despesas:aprovar', args=[despesa.id]))
            despesa.refresh_from_db()
            self.assertEqual(despesa.status, StatusDespesa.APROVADO)

            # O próprio solicitante não pode liquidar a despesa aprovada
            self.client.force_login(self.tesoureiro)
            self.client.post(
                reverse('despesas:liquidar', args=[despesa.id]),
                {'comprovante_pagamento': self._gerar_imagem('cora.png')},
            )
            despesa.refresh_from_db()
            self.assertEqual(despesa.status, StatusDespesa.APROVADO)

            # Outro tesoureiro consegue liquidar
            self.client.force_login(self.outro_tesoureiro)
            self.client.post(
                reverse('despesas:liquidar', args=[despesa.id]),
                {'comprovante_pagamento': self._gerar_imagem('cora.png')},
            )
            despesa.refresh_from_db()
            self.assertEqual(despesa.status, StatusDespesa.PAGO)
