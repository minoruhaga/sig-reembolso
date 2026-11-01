from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.despesas.models import Despesa, StatusDespesa
from apps.financeiro.models import Coordenacao
from apps.usuarios.models import PapelUsuario, Usuario
from apps.usuarios.services import coordenacoes_visiveis, url_pos_login


class LoginLogoutRbacTestCase(TestCase):
    """
    Suíte de testes do login customizado, redirect por papel e recorte de coordenações (Issue #6 / RF01).

    - O que faz: Exercita autenticação, destinos pós-login, bloqueio de `/admin/` e o queryset visível por papel.
    - Como faz: Usa `django.test.Client` e `TestCase` com duas coordenações e três usuários representativos.
    - Qual finalidade atende: Garante que coordenador de campo não vê as 15 pastas nem opera o Admin,
      enquanto Tesouraria e Diretoria mantêm visão consolidada.
    """

    def setUp(self):
        """
        Cria a massa mínima de usuários e pastas para os cenários de RBAC.

        - O que faz: Persiste ALIM, INFRA, um coordenador vinculado a ALIM, tesoureiro staff e admin.
        - Como faz: `create_user` e `Coordenacao.objects.create` no banco transacional de testes.
        - Qual finalidade atende: Isola cada teste sem depender da fixture das 15 coordenações.
        """
        self.alim = Coordenacao.objects.create(
            nome='Alimentação e Cozinha Central',
            sigla='ALIM',
            teto_orcamentario=Decimal('1000.00'),
        )
        self.infra = Coordenacao.objects.create(
            nome='Infraestrutura e Energia',
            sigla='INFRA',
            teto_orcamentario=Decimal('2000.00'),
        )
        self.coordenador = Usuario.objects.create_user(
            username='coord_cozinha',
            password='cozinha123',
            papel=PapelUsuario.COORDENADOR,
            coordenacao=self.alim,
        )
        self.tesoureiro = Usuario.objects.create_user(
            username='tesoureiro',
            password='tesouraria123',
            papel=PapelUsuario.TESOUREIRO,
            is_staff=True,
        )
        self.admin = Usuario.objects.create_user(
            username='admin',
            password='admin123',
            papel=PapelUsuario.ADMIN,
            is_staff=True,
            is_superuser=True,
        )

    def test_anonimo_e_redirecionado_do_dashboard_para_login(self):
        """
        Visitante sem sessão não acessa o painel operacional.

        - O que faz: GET em `/` sem autenticar.
        - Como faz: Confere 302 para a rota nomeada `usuarios:login`.
        - Qual finalidade atende: Impede vazamento público dos tetos orçamentários do AG VII.
        """
        resposta = self.client.get(reverse('dashboard'))
        self.assertEqual(resposta.status_code, 302)
        self.assertIn(reverse('usuarios:login'), resposta.url)

    def test_login_coordenador_redireciona_ao_dashboard(self):
        """
        Coordenador autenticado cai no dashboard da própria pasta.

        - O que faz: POST no login customizado com credenciais de coordenador.
        - Como faz: Segue o 302 e verifica 200 no dashboard contendo só a sigla ALIM.
        - Qual finalidade atende: Critério 1 da Issue #6 (redirect por papel) e recorte de área.
        """
        resposta = self.client.post(
            reverse('usuarios:login'),
            {'username': 'coord_cozinha', 'password': 'cozinha123'},
        )
        self.assertEqual(resposta.status_code, 302)
        self.assertEqual(resposta.url, reverse('dashboard'))

        painel = self.client.get(reverse('dashboard'))
        self.assertEqual(painel.status_code, 200)
        self.assertContains(painel, 'ALIM')
        self.assertNotContains(painel, 'INFRA')

    def test_login_tesoureiro_redireciona_ao_dashboard_com_todas_as_pastas(self):
        """
        Tesoureiro autenticado vê o painel consolidado.

        - O que faz: Login do tesoureiro e GET do dashboard.
        - Como faz: Confere redirect para `dashboard` e presença de ALIM e INFRA.
        - Qual finalidade atende: Tesouraria visualiza todas as coordenações ativas (RF01).
        """
        resposta = self.client.post(
            reverse('usuarios:login'),
            {'username': 'tesoureiro', 'password': 'tesouraria123'},
        )
        self.assertEqual(resposta.status_code, 302)
        self.assertEqual(resposta.url, reverse('dashboard'))

        painel = self.client.get(reverse('dashboard'))
        self.assertContains(painel, 'ALIM')
        self.assertContains(painel, 'INFRA')

    def test_login_admin_redireciona_ao_django_admin(self):
        """
        Administrador Geral é enviado ao Django Admin após o login.

        - O que faz: POST de login com usuário ADMIN.
        - Como faz: Compara a URL de destino com `admin:index`.
        - Qual finalidade atende: Redirect diferenciado por papel (critério 1).
        """
        resposta = self.client.post(
            reverse('usuarios:login'),
            {'username': 'admin', 'password': 'admin123'},
        )
        self.assertEqual(resposta.status_code, 302)
        self.assertEqual(resposta.url, reverse('admin:index'))

    def test_coordenador_autenticado_nao_acessa_admin(self):
        """
        Coordenador de campo é barrado em qualquer rota `/admin/`.

        - O que faz: Autentica o coordenador e solicita o índice do Admin.
        - Como faz: Espera 302 para o dashboard mesmo se `is_staff` for forçado.
        - Qual finalidade atende: Critério 2 da Issue #6 (bloqueio de rotas administrativas).
        """
        self.coordenador.is_staff = True
        self.coordenador.save(update_fields=['is_staff'])
        self.client.force_login(self.coordenador)
        resposta = self.client.get(reverse('admin:index'))
        self.assertEqual(resposta.status_code, 302)
        self.assertEqual(resposta.url, reverse('dashboard'))

    def test_tesoureiro_acessa_admin(self):
        """
        Tesoureiro staff permanece autorizado no Django Admin.

        - O que faz: GET em `admin:index` autenticado como tesoureiro.
        - Como faz: Espera HTTP 200.
        - Qual finalidade atende: O bloqueio não pode cegar a Tesouraria.
        """
        self.client.force_login(self.tesoureiro)
        resposta = self.client.get(reverse('admin:index'))
        self.assertEqual(resposta.status_code, 200)

    def test_anonimo_em_admin_vai_ao_login_customizado(self):
        """
        Acesso anônimo a `/admin/` usa a tela de login do SIG, não a do Admin.

        - O que faz: GET em `admin:index` sem sessão.
        - Como faz: Confere redirect contendo `usuarios:login`.
        - Qual finalidade atende: Um único ponto de autenticação com o modelo `Usuario`.
        """
        resposta = self.client.get(reverse('admin:index'))
        self.assertEqual(resposta.status_code, 302)
        self.assertIn(reverse('usuarios:login'), resposta.url)

    def test_logout_encerra_sessao(self):
        """
        Logout por POST invalida a sessão e devolve ao login.

        - O que faz: Autentica, envia POST para `usuarios:logout` e tenta o dashboard.
        - Como faz: Segue o redirect do logout e confere novo 302 para login no painel.
        - Qual finalidade atende: Dispositivo compartilhado no campo não reaproveita sessão.
        """
        self.client.force_login(self.coordenador)
        resposta = self.client.post(reverse('usuarios:logout'))
        self.assertEqual(resposta.status_code, 302)
        self.assertEqual(resposta.url, reverse('usuarios:login'))
        painel = self.client.get(reverse('dashboard'))
        self.assertEqual(painel.status_code, 302)

    def test_servico_coordenacoes_visiveis_respeita_papel(self):
        """
        O serviço de escopo filtra pastas no domínio, não na view.

        - O que faz: Compara `coordenacoes_visiveis` para coordenador, tesoureiro e admin.
        - Como faz: Avalia `sigla` no queryset retornado.
        - Qual finalidade atende: Views permanecem orquestradoras; a regra RBAC vive no serviço.
        """
        siglas_coord = set(coordenacoes_visiveis(self.coordenador).values_list('sigla', flat=True))
        siglas_tesouraria = set(coordenacoes_visiveis(self.tesoureiro).values_list('sigla', flat=True))
        siglas_admin = set(coordenacoes_visiveis(self.admin).values_list('sigla', flat=True))
        self.assertEqual(siglas_coord, {'ALIM'})
        self.assertEqual(siglas_tesouraria, {'ALIM', 'INFRA'})
        self.assertEqual(siglas_admin, {'ALIM', 'INFRA'})

    def test_url_pos_login_por_papel(self):
        """
        Mapeia papel para URL padrão de aterrissagem.

        - O que faz: Chama `url_pos_login` para os três perfis.
        - Como faz: Compara com `admin:index` e `dashboard`.
        - Qual finalidade atende: Documenta o contrato de redirect usado pela `LoginView`.
        """
        self.assertEqual(url_pos_login(self.admin), reverse('admin:index'))
        self.assertEqual(url_pos_login(self.tesoureiro), reverse('dashboard'))
        self.assertEqual(url_pos_login(self.coordenador), reverse('dashboard'))

    def test_dashboard_coordenador_omite_despesa_de_outra_pasta(self):
        """
        Histórico recente do coordenador não lista despesa de outra coordenação.

        - O que faz: Cria uma despesa em INFRA e autentica o coordenador de ALIM.
        - Como faz: GET no dashboard e `assertNotContains` do título da despesa alheia.
        - Qual finalidade atende: Recorte de visualização também nas despesas, não só nos termômetros.
        """
        Despesa.objects.create(
            coordenacao=self.infra,
            solicitante=self.coordenador,
            titulo='Diesel exclusivo da Infra',
            valor=Decimal('50.00'),
            data_despesa=timezone.now().date(),
            status=StatusDespesa.ENVIADO,
        )
        self.client.force_login(self.coordenador)
        painel = self.client.get(reverse('dashboard'))
        self.assertNotContains(painel, 'Diesel exclusivo da Infra')
