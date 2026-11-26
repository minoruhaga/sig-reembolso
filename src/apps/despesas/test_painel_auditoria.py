import shutil
import tempfile
from decimal import Decimal
from io import BytesIO

from django.contrib.auth.models import AnonymousUser
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from apps.despesas.models import Despesa, StatusDespesa
from apps.financeiro.models import Coordenacao
from apps.usuarios.models import PapelUsuario, Usuario
from apps.usuarios.services import usuario_pode_acessar_painel_auditoria


class BaseAuditoriaTestCase(TestCase):
    """
    Base comum dos testes do painel de auditoria (Issue #13), sem casos de teste próprios.

    - O que faz: Prepara coordenação, usuários de cada papel, mídia temporária e geradores de anexos.
    - Como faz: Centraliza `setUp`, `tearDown` e os auxiliares `_imagem`, `_pdf` e `_enviada`.
    - Qual finalidade atende: Evita repetir a preparação nas suítes do painel e da rota de comprovantes.
    """

    def setUp(self):
        """
        Prepara coordenação, usuários de cada papel e diretório temporário de mídia.
        """
        self.temp_media = tempfile.mkdtemp()
        self.coordenacao = Coordenacao.objects.create(
            nome='Alimentação', sigla='ALIM', teto_orcamentario=Decimal('1000.00'), ativo=True,
        )
        self.coordenador = Usuario.objects.create_user(
            username='coord_aud', password='senha_teste_123',
            papel=PapelUsuario.COORDENADOR, coordenacao=self.coordenacao, chave_pix='coord@pix.com',
        )
        self.tesoureiro = Usuario.objects.create_user(
            username='tes_aud', password='senha_teste_123', papel=PapelUsuario.TESOUREIRO, is_staff=True,
        )
        self.outro_tesoureiro = Usuario.objects.create_user(
            username='tes_aud_2', password='senha_teste_123', papel=PapelUsuario.TESOUREIRO, is_staff=True,
        )
        self.admin_geral = Usuario.objects.create_user(
            username='admin_aud', password='senha_teste_123', papel=PapelUsuario.ADMIN, is_staff=True,
        )
        self.superusuario = Usuario.objects.create_superuser(
            username='root_aud', password='senha_teste_123', email='root@exemplo.test',
        )

    def tearDown(self):
        """
        Remove o diretório temporário de mídia.
        """
        shutil.rmtree(self.temp_media, ignore_errors=True)

    def _imagem(self, nome='nota.png') -> SimpleUploadedFile:
        """
        Gera uma imagem PNG válida em memória para servir de NF ou recibo.
        """
        buf = BytesIO()
        Image.new('RGB', (600, 400), color=(40, 90, 150)).save(buf, format='PNG')
        return SimpleUploadedFile(nome, buf.getvalue(), content_type='image/png')

    def _pdf(self, nome='danfe.pdf') -> SimpleUploadedFile:
        """
        Gera um PDF simulado para servir de NF eletrônica.
        """
        return SimpleUploadedFile(nome, b'%PDF-1.4 nota fiscal simulada', content_type='application/pdf')

    def _enviada(self, *, solicitante=None, comprovante=None, valor=Decimal('250.00')) -> Despesa:
        """
        Cria e submete uma despesa, deixando-a no estado ENVIADO.
        """
        autor = solicitante or self.coordenador
        despesa = Despesa.objects.create(
            coordenacao=self.coordenacao, solicitante=autor, titulo='Compra de hortifrúti',
            valor=valor, data_despesa=timezone.now().date(),
            comprovante=comprovante or self._imagem(), status=StatusDespesa.RASCUNHO,
        )
        despesa.submeter(autor)
        return despesa



class PainelAuditoriaTestCase(BaseAuditoriaTestCase):
    """
    Testes do painel de auditoria de notas da Tesouraria (Issue #13).

    - O que faz: Verifica que só a Tesouraria (e o superusuário) abre o painel, que menu e dashboard
      escondem o atalho de quem não audita, que as despesas aparecem em cards com o modal de zoom, que o
      tipo de arquivo (foto ou PDF) é informado ao visualizador e que a segregação de funções (RN03)
      esconde as ações rápidas da própria solicitação.
    - Como faz: Usa os usuários e anexos de `BaseAuditoriaTestCase` e o test client do Django.
    - Qual finalidade atende: Garante que a conferência de NF ou recibo fique restrita a quem audita as
      contas do AG VII e que o painel ofereça os recursos pedidos na issue.
    """

    # --- Acesso -----------------------------------------------------------------

    def test_tesoureiro_abre_o_painel(self):
        """
        Tesoureiro recebe 200 e o template do painel de auditoria.
        """
        self.client.force_login(self.tesoureiro)
        resposta = self.client.get(reverse('despesas:triagem'))
        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, 'despesas/painel_triagem.html')

    def test_superusuario_abre_o_painel(self):
        """
        Superusuário é tratado como Tesoureiro e também acessa.
        """
        self.client.force_login(self.superusuario)
        self.assertEqual(self.client.get(reverse('despesas:triagem')).status_code, 200)

    def test_administrador_geral_recebe_403(self):
        """
        Administrador Geral sem papel de Tesoureiro não abre o painel de auditoria.
        """
        self.client.force_login(self.admin_geral)
        self.assertEqual(self.client.get(reverse('despesas:triagem')).status_code, 403)

    def test_coordenador_recebe_403(self):
        """
        Coordenador de campo não abre o painel de auditoria.
        """
        self.client.force_login(self.coordenador)
        self.assertEqual(self.client.get(reverse('despesas:triagem')).status_code, 403)

    def test_anonimo_vai_para_o_login(self):
        """
        Visitante sem sessão é redirecionado para a tela de login.
        """
        resposta = self.client.get(reverse('despesas:triagem'))
        self.assertEqual(resposta.status_code, 302)
        self.assertIn(reverse('usuarios:login'), resposta['Location'])

    def test_administrador_geral_nao_aprova_pela_rota_de_acao(self):
        """
        Mesmo chamando a rota de aprovação direto, o Administrador Geral recebe 403 e nada muda.
        """
        with override_settings(MEDIA_ROOT=self.temp_media):
            despesa = self._enviada()
            self.client.force_login(self.admin_geral)
            resposta = self.client.post(reverse('despesas:aprovar', args=[despesa.id]))
        self.assertEqual(resposta.status_code, 403)
        despesa.refresh_from_db()
        self.assertEqual(despesa.status, StatusDespesa.ENVIADO)

    def test_regra_de_acesso_por_papel(self):
        """
        O serviço de acesso libera só Tesoureiro e superusuário.
        """
        self.assertTrue(usuario_pode_acessar_painel_auditoria(self.tesoureiro))
        self.assertTrue(usuario_pode_acessar_painel_auditoria(self.superusuario))
        self.assertFalse(usuario_pode_acessar_painel_auditoria(self.admin_geral))
        self.assertFalse(usuario_pode_acessar_painel_auditoria(self.coordenador))
        self.assertFalse(usuario_pode_acessar_painel_auditoria(AnonymousUser()))

    # --- Menu e dashboard ---------------------------------------------------------

    def test_menu_mostra_auditoria_so_para_tesouraria(self):
        """
        O item "Auditoria de Notas" aparece para o Tesoureiro e some para o Administrador Geral,
        que continua vendo "Administração".
        """
        self.client.force_login(self.tesoureiro)
        self.assertContains(self.client.get(reverse('dashboard')), 'Auditoria de Notas')

        self.client.force_login(self.admin_geral)
        resposta = self.client.get(reverse('dashboard'))
        self.assertNotContains(resposta, 'Auditoria de Notas')
        self.assertContains(resposta, 'Administração')

    def test_dashboard_mostra_atalho_do_painel_so_para_tesouraria(self):
        """
        O botão "Ver Todas no Painel da Tesouraria" do dashboard segue a mesma regra do painel.
        """
        self.client.force_login(self.tesoureiro)
        self.assertContains(self.client.get(reverse('dashboard')), 'Ver Todas no Painel da Tesouraria')

        self.client.force_login(self.admin_geral)
        self.assertNotContains(self.client.get(reverse('dashboard')), 'Ver Todas no Painel da Tesouraria')

    # --- Cards e modal de zoom ----------------------------------------------------

    def test_despesas_aparecem_em_cards_com_badges(self):
        """
        Cada despesa vira um card com badge de status, de estouro (RN02) e botão de conferência.
        """
        with override_settings(MEDIA_ROOT=self.temp_media):
            despesa = self._enviada(valor=Decimal('1200.00'))
            self.client.force_login(self.tesoureiro)
            resposta = self.client.get(reverse('despesas:triagem'))

        self.assertContains(resposta, f'id="despesa-{despesa.id}"')
        self.assertContains(resposta, 'aud-card aud-card--estouro')
        self.assertContains(resposta, 'Aguardando decisão')
        self.assertContains(resposta, 'ESTOURO DE TETO (+R$ 200,00)')
        self.assertContains(resposta, 'Conferir nota')
        self.assertContains(resposta, 'coord@pix.com')

    def test_modal_de_conferencia_tem_tela_cheia_zoom_e_acoes_rapidas(self):
        """
        O modal abre em tela cheia, com controles de zoom, giro, abas de documento e os botões de
        aprovar e rejeitar com atalhos de teclado.
        """
        with override_settings(MEDIA_ROOT=self.temp_media):
            self._enviada()
            self.client.force_login(self.tesoureiro)
            resposta = self.client.get(reverse('despesas:triagem'))

        self.assertContains(resposta, 'modal-fullscreen')
        for controle in ('data-zoom="mais"', 'data-zoom="menos"', 'data-zoom="ajustar"',
                         'data-zoom="real"', 'data-zoom="girar"'):
            self.assertContains(resposta, controle)
        self.assertContains(resposta, 'data-doc="nota"')
        self.assertContains(resposta, 'data-doc="pagamento"')
        self.assertContains(resposta, 'id="audFormAprovar"')
        self.assertContains(resposta, 'id="audFormRejeitar"')
        self.assertContains(resposta, 'name="motivo_rejeicao"')

    def test_card_informa_urls_das_acoes_rapidas(self):
        """
        O card leva as rotas de aprovar, rejeitar e liquidar que o modal usa nos formulários.
        """
        with override_settings(MEDIA_ROOT=self.temp_media):
            despesa = self._enviada()
            self.client.force_login(self.tesoureiro)
            resposta = self.client.get(reverse('despesas:triagem'))

        self.assertContains(resposta, f'data-url-aprovar="{reverse("despesas:aprovar", args=[despesa.id])}"')
        self.assertContains(resposta, f'data-url-rejeitar="{reverse("despesas:rejeitar", args=[despesa.id])}"')
        self.assertContains(resposta, f'data-url-liquidar="{reverse("despesas:liquidar", args=[despesa.id])}"')

    def test_foto_usa_visualizador_de_imagem(self):
        """
        NF em foto aparece como miniatura e é marcada como não-PDF para o visualizador com zoom.
        """
        with override_settings(MEDIA_ROOT=self.temp_media):
            despesa = self._enviada()
            self.client.force_login(self.tesoureiro)
            resposta = self.client.get(reverse('despesas:triagem'))

        url_protegida = reverse('despesas:comprovante', args=[despesa.id, 'nota'])
        self.assertFalse(despesa.comprovante_eh_pdf)
        self.assertContains(resposta, 'data-nota-pdf="0"')
        self.assertContains(resposta, f'<img src="{url_protegida}"')
        self.assertContains(resposta, f'data-nota-url="{url_protegida}"')
        self.assertNotContains(resposta, despesa.comprovante.url)

    def test_pdf_usa_leitor_de_pdf(self):
        """
        NF em PDF é marcada como PDF, para o modal abrir no leitor embutido em vez do zoom de imagem.
        """
        with override_settings(MEDIA_ROOT=self.temp_media):
            despesa = self._enviada(comprovante=self._pdf())
            self.client.force_login(self.tesoureiro)
            resposta = self.client.get(reverse('despesas:triagem'))

        self.assertTrue(despesa.comprovante_eh_pdf)
        self.assertContains(resposta, 'data-nota-pdf="1"')
        self.assertContains(resposta, 'aud-miniatura-pdf')

    def test_comprovante_de_pagamento_fica_disponivel_no_modal(self):
        """
        Depois da liquidação, o card leva o comprovante Cora PJ para a aba "Comprovante de pagamento".
        """
        with override_settings(MEDIA_ROOT=self.temp_media):
            despesa = self._enviada()
            despesa.aprovar(self.tesoureiro)
            despesa.liquidar(self.tesoureiro, comprovante_pagamento=self._imagem('cora.png'))
            despesa.refresh_from_db()
            self.client.force_login(self.tesoureiro)
            resposta = self.client.get(reverse('despesas:triagem'), {'status': 'PAGO'})

        url_protegida = reverse('despesas:comprovante', args=[despesa.id, 'pagamento'])
        self.assertContains(resposta, f'data-pagamento-url="{url_protegida}"')
        self.assertContains(resposta, 'data-pagamento-pdf="0"')

    def test_tipo_de_arquivo_sem_anexo(self):
        """
        Sem arquivo anexado, as propriedades de PDF devolvem False (sem erro).
        """
        despesa = Despesa(coordenacao=self.coordenacao, solicitante=self.coordenador, titulo='X', valor=Decimal('1.00'))
        self.assertFalse(despesa.comprovante_eh_pdf)
        self.assertFalse(despesa.comprovante_pagamento_eh_pdf)

    # --- Segregação de funções (RN03) -------------------------------------------

    def test_solicitacao_propria_esconde_acoes_rapidas(self):
        """
        Na despesa do próprio tesoureiro, o card mostra "Solicitação própria" e marca impedimento;
        na despesa de outra pessoa, as ações ficam liberadas.
        """
        with override_settings(MEDIA_ROOT=self.temp_media):
            propria = self._enviada(solicitante=self.tesoureiro)
            alheia = self._enviada()
            self.client.force_login(self.tesoureiro)
            resposta = self.client.get(reverse('despesas:triagem'))

        html = resposta.content.decode()
        self.assertContains(resposta, 'Solicitação própria')
        card_proprio = html[html.index(f'id="despesa-{propria.id}"'):]
        card_alheio = html[html.index(f'id="despesa-{alheia.id}"'):]
        self.assertIn('data-impedido="1"', card_proprio[:card_proprio.index('</article>')])
        self.assertIn('data-impedido="0"', card_alheio[:card_alheio.index('</article>')])

    def test_outro_tesoureiro_ve_a_despesa_liberada(self):
        """
        A despesa de um tesoureiro aparece liberada para o segundo tesoureiro decidir.
        """
        with override_settings(MEDIA_ROOT=self.temp_media):
            despesa = self._enviada(solicitante=self.tesoureiro)
            self.client.force_login(self.outro_tesoureiro)
            resposta = self.client.get(reverse('despesas:triagem'))

        html = resposta.content.decode()
        card = html[html.index(f'id="despesa-{despesa.id}"'):]
        self.assertIn('data-impedido="0"', card[:card.index('</article>')])


class ComprovanteAuditoriaRotaTestCase(BaseAuditoriaTestCase):
    """
    Testes da rota protegida que entrega a NF/recibo e o comprovante de pagamento ao painel (Issue #13).

    - O que faz: Verifica quem pode baixar o arquivo, o tipo MIME, a liberação de exibição no `<iframe>`
      do próprio site (`SAMEORIGIN`) e as respostas 404 para tipo, despesa ou arquivo inexistente.
    - Como faz: Reaproveita usuários e geradores de arquivo de `BaseAuditoriaTestCase` e chama a rota
      `despesas:comprovante` com o test client.
    - Qual finalidade atende: Garante que o PDF apareça no modal sem afrouxar o clickjacking do resto do
      site e que o documento fiscal só chegue à Tesouraria.
    """

    def _get(self, despesa, tipo='nota'):
        """
        Faz GET na rota protegida do comprovante e lê o corpo inteiro (fechando o arquivo).
        """
        resposta = self.client.get(reverse('despesas:comprovante', args=[despesa.id, tipo]))
        if hasattr(resposta, 'streaming_content'):
            resposta.corpo = b''.join(resposta.streaming_content)
            resposta.close()
        return resposta

    def test_tesoureiro_recebe_a_foto_inline(self):
        """
        Tesoureiro recebe a foto com o tipo da imagem, exibição inline, nosniff e cache privado.
        """
        with override_settings(MEDIA_ROOT=self.temp_media):
            despesa = self._enviada()
            self.client.force_login(self.tesoureiro)
            resposta = self._get(despesa)

        self.assertEqual(resposta.status_code, 200)
        self.assertTrue(resposta['Content-Type'].startswith('image/'))
        self.assertEqual(resposta['Content-Disposition'], 'inline')
        self.assertEqual(resposta['X-Content-Type-Options'], 'nosniff')
        self.assertIn('private', resposta['Cache-Control'])
        self.assertGreater(len(resposta.corpo), 0)

    def test_pdf_pode_ser_exibido_no_iframe_do_proprio_site(self):
        """
        O PDF sai como application/pdf com X-Frame-Options SAMEORIGIN, para o modal conseguir exibi-lo.
        """
        with override_settings(MEDIA_ROOT=self.temp_media):
            despesa = self._enviada(comprovante=self._pdf())
            self.client.force_login(self.tesoureiro)
            resposta = self._get(despesa)

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta['Content-Type'], 'application/pdf')
        self.assertEqual(resposta['X-Frame-Options'], 'SAMEORIGIN')
        self.assertEqual(resposta.corpo, b'%PDF-1.4 nota fiscal simulada')

    def test_resto_do_site_continua_com_deny(self):
        """
        A liberação vale só para a rota do comprovante: o painel continua com X-Frame-Options DENY.
        """
        self.client.force_login(self.tesoureiro)
        self.assertEqual(self.client.get(reverse('despesas:triagem'))['X-Frame-Options'], 'DENY')

    def test_comprovante_de_pagamento(self):
        """
        Com tipo "pagamento", a rota devolve o comprovante Cora PJ da despesa liquidada.
        """
        with override_settings(MEDIA_ROOT=self.temp_media):
            despesa = self._enviada()
            despesa.aprovar(self.tesoureiro)
            despesa.liquidar(self.tesoureiro, comprovante_pagamento=self._imagem('cora.png'))
            self.client.force_login(self.outro_tesoureiro)
            resposta = self._get(despesa, 'pagamento')

        self.assertEqual(resposta.status_code, 200)
        self.assertTrue(resposta['Content-Type'].startswith('image/'))

    def test_superusuario_recebe_o_arquivo(self):
        """
        Superusuário, tratado como Tesoureiro, também abre o comprovante.
        """
        with override_settings(MEDIA_ROOT=self.temp_media):
            despesa = self._enviada()
            self.client.force_login(self.superusuario)
            self.assertEqual(self._get(despesa).status_code, 200)

    def test_administrador_geral_recebe_403(self):
        """
        Administrador Geral não abre o comprovante pela rota do painel.
        """
        with override_settings(MEDIA_ROOT=self.temp_media):
            despesa = self._enviada()
            self.client.force_login(self.admin_geral)
            self.assertEqual(self._get(despesa).status_code, 403)

    def test_coordenador_recebe_403_mesmo_na_propria_despesa(self):
        """
        Coordenador não usa a rota do painel, nem para a própria despesa.
        """
        with override_settings(MEDIA_ROOT=self.temp_media):
            despesa = self._enviada()
            self.client.force_login(self.coordenador)
            self.assertEqual(self._get(despesa).status_code, 403)

    def test_anonimo_vai_para_o_login(self):
        """
        Sem sessão, a rota redireciona para o login.
        """
        with override_settings(MEDIA_ROOT=self.temp_media):
            despesa = self._enviada()
            resposta = self._get(despesa)
        self.assertEqual(resposta.status_code, 302)
        self.assertIn(reverse('usuarios:login'), resposta['Location'])

    def test_tipo_desconhecido_responde_404(self):
        """
        Um tipo diferente de "nota" ou "pagamento" responde 404.
        """
        with override_settings(MEDIA_ROOT=self.temp_media):
            despesa = self._enviada()
            self.client.force_login(self.tesoureiro)
            self.assertEqual(self._get(despesa, 'outro').status_code, 404)

    def test_despesa_inexistente_responde_404(self):
        """
        Um id de despesa que não existe responde 404.
        """
        self.client.force_login(self.tesoureiro)
        resposta = self.client.get(reverse('despesas:comprovante', args=[999999, 'nota']))
        self.assertEqual(resposta.status_code, 404)

    def test_despesa_sem_comprovante_de_pagamento_responde_404(self):
        """
        Pedir o comprovante de pagamento de uma despesa ainda não paga responde 404.
        """
        with override_settings(MEDIA_ROOT=self.temp_media):
            despesa = self._enviada()
            self.client.force_login(self.tesoureiro)
            self.assertEqual(self._get(despesa, 'pagamento').status_code, 404)

    def test_arquivo_apagado_do_disco_responde_404(self):
        """
        Se o arquivo registrado não existe mais no storage, a rota responde 404 em vez de erro 500.
        """
        with override_settings(MEDIA_ROOT=self.temp_media):
            despesa = self._enviada()
            despesa.comprovante.close()  # no Windows, o arquivo aberto não pode ser apagado
            despesa.comprovante.storage.delete(despesa.comprovante.name)
            self.client.force_login(self.tesoureiro)
            self.assertEqual(self._get(despesa).status_code, 404)
