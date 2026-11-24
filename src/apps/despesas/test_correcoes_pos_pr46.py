from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.core.exceptions import PermissaoNegadaDominioError
from apps.despesas.forms import DespesaForm
from apps.despesas.models import (
    CategoriaDespesa,
    Despesa,
    FormaPagamentoOriginal,
    StatusDespesa,
    TipoDespesa,
)
from apps.despesas.services import criar_ou_atualizar_despesa
from apps.financeiro.models import Coordenacao
from apps.usuarios.models import PapelUsuario, Usuario


class CorrecoesPosPR46TestCase(TestCase):
    """
    Suíte de regressão para as correções da auditoria pós-merge da PR #46 (Issue #47).

    - O que faz: Valida o recorte RBAC em `DespesaForm` e `criar_ou_atualizar_despesa`, o mapeamento
      `MESSAGE_TAGS` para `alert-danger` no Bootstrap 5 e a navegação/classe `active` dinâmica em `base.html`.
    - Como faz: Cria duas coordenações, coordenador e tesoureiro, exercitando formulário, serviço de domínio
      e endpoints HTTP via cliente de testes do Django.
    - Qual finalidade atende: Impede regressões de segurança (RBAC) e usabilidade/UI antes da apresentação do sistema.
    """

    def setUp(self):
        """
        Prepara coordenações e usuários de teste com papéis distintos.

        - O que faz: Cria pastas ALIM e INFRA, um coordenador vinculado apenas a ALIM e um tesoureiro.
        - Como faz: Persiste instâncias via ORM com tetos conhecidos em `Decimal`.
        - Qual finalidade atende: Fornece massa isolada para validar RBAC, mensagens e navegação.
        """
        self.alim = Coordenacao.objects.create(
            nome='Alimentação',
            sigla='ALIM',
            teto_orcamentario=Decimal('1000.00'),
        )
        self.infra = Coordenacao.objects.create(
            nome='Infraestrutura',
            sigla='INFRA',
            teto_orcamentario=Decimal('800.00'),
        )
        self.coordenador = Usuario.objects.create_user(
            username='coord_bug47',
            password='pass123',  # nosec B106
            papel=PapelUsuario.COORDENADOR,
            coordenacao=self.alim,
        )
        self.tesoureiro = Usuario.objects.create_user(
            username='tes_bug47',
            password='pass123',  # nosec B106
            papel=PapelUsuario.TESOUREIRO,
            is_staff=True,
        )

    def test_despesa_form_restringe_coordenacoes_ao_escopo_rbac(self):
        """
        Coordenador só vê a própria coordenação no formulário; Tesoureiro vê todas as ativas.

        - O que faz: Confere o queryset do campo `coordenacao` em `DespesaForm` e o HTML da view `despesas:nova`.
        - Como faz: Instancia `DespesaForm(usuario=...)` para ambos os papéis e verifica o GET autenticado.
        - Qual finalidade atende: Corrige o Bug 1 da Issue #47, alinhando o formulário ao recorte RBAC (RF01).
        """
        form_coord = DespesaForm(usuario=self.coordenador)
        self.assertEqual(
            list(form_coord.fields['coordenacao'].queryset.values_list('pk', flat=True)),
            [self.alim.pk],
        )

        form_tes = DespesaForm(usuario=self.tesoureiro)
        self.assertEqual(
            set(form_tes.fields['coordenacao'].queryset.values_list('pk', flat=True)),
            {self.alim.pk, self.infra.pk},
        )

        self.client.force_login(self.coordenador)
        resp = self.client.get(reverse('despesas:nova'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, f'value="{self.alim.pk}"')
        self.assertNotContains(resp, f'value="{self.infra.pk}"')

    def test_coordenador_bloqueado_ao_lancar_despesa_em_outra_coordenacao(self):
        """
        Bloqueia tanto no POST da view quanto na camada de serviço a tentativa de lançar gasto em outra pasta.

        - O que faz: Envia POST forjado para `despesas:nova` com `coordenacao=INFRA` e chama
          `criar_ou_atualizar_despesa` diretamente com outra pasta.
        - Como faz: Verifica que nenhuma `Despesa` é persistida no POST e que o serviço levanta
          `PermissaoNegadaDominioError`.
        - Qual finalidade atende: Fecha o bypass de RBAC do Bug 1 na camada de entrada e na camada de domínio.
        """
        self.client.force_login(self.coordenador)
        resp = self.client.post(
            reverse('despesas:nova'),
            {
                'coordenacao': self.infra.pk,
                'titulo': 'Tentativa fora da pasta',
                'categoria': CategoriaDespesa.INFRAESTRUTURA,
                'tipo': TipoDespesa.REEMBOLSO,
                'forma_pagamento_original': FormaPagamentoOriginal.PIX,
                'valor': '50,00',
                'data_despesa': timezone.now().date().isoformat(),
                'acao': 'rascunho',
            },
        )
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Despesa.objects.filter(titulo='Tentativa fora da pasta').exists())

        with self.assertRaises(PermissaoNegadaDominioError):
            criar_ou_atualizar_despesa(
                usuario=self.coordenador,
                dados_validados={
                    'coordenacao': self.infra,
                    'titulo': 'Bypass direto no service',
                    'categoria': CategoriaDespesa.INFRAESTRUTURA,
                    'tipo': TipoDespesa.REEMBOLSO,
                    'forma_pagamento_original': FormaPagamentoOriginal.PIX,
                    'valor': Decimal('50.00'),
                    'data_despesa': timezone.now().date(),
                },
                submeter_agora=False,
            )

    def test_mensagens_de_erro_renderizam_alert_danger_no_bootstrap(self):
        """
        Garante que `messages.error()` seja renderizado com a classe `alert-danger` do Bootstrap 5.

        - O que faz: Aciona uma ação que dispara `messages.error()` (edição de despesa já aprovada) e
          inspeciona o HTML da página de destino.
        - Como faz: Cria despesa `APROVADO`, faz GET em `despesas:editar` com `follow=True` e valida
          a presença de `alert-danger` e ausência de `alert-error`.
        - Qual finalidade atende: Corrige o Bug 3 da Issue #47, garantindo feedback visual de erro adequado.
        """
        despesa = Despesa.objects.create(
            coordenacao=self.alim,
            solicitante=self.coordenador,
            titulo='Despesa já aprovada',
            categoria=CategoriaDespesa.ALIMENTACAO,
            tipo=TipoDespesa.REEMBOLSO,
            forma_pagamento_original=FormaPagamentoOriginal.PIX,
            valor=Decimal('30.00'),
            data_despesa=timezone.now().date(),
            status=StatusDespesa.APROVADO,
        )
        self.client.force_login(self.coordenador)
        resp = self.client.get(reverse('despesas:editar', args=[despesa.pk]), follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'alert-danger')
        self.assertNotContains(resp, 'alert-error')

    def test_navbar_exibe_saldos_e_marca_rota_ativa_dinamicamente(self):
        """
        Verifica o link de `financeiro:saldos` na navbar e o destaque dinâmico da página atual.

        - O que faz: Navega em `dashboard`, `financeiro:saldos` e `relatorios:balancete` e valida qual link
          recebe a classe `active`.
        - Como faz: Executa GET autenticado nas três rotas e confere a presença de `href` para `financeiro:saldos`
          e a marcação `nav-link active` exclusiva da rota visitada.
        - Qual finalidade atende: Corrige o Bug 5 da Issue #47, expondo a tela de saldos na navegação principal.
        """
        self.client.force_login(self.coordenador)

        url_saldos = reverse('financeiro:saldos')
        url_dashboard = reverse('dashboard')
        url_balancete = reverse('relatorios:balancete')

        resp_dash = self.client.get(url_dashboard)
        self.assertEqual(resp_dash.status_code, 200)
        self.assertContains(resp_dash, f'href="{url_saldos}"')
        self.assertContains(resp_dash, f'class="nav-link active" aria-current="page" href="{url_dashboard}"')

        resp_saldos = self.client.get(url_saldos)
        self.assertEqual(resp_saldos.status_code, 200)
        self.assertContains(resp_saldos, f'class="nav-link active" aria-current="page" href="{url_saldos}"')
        self.assertNotContains(resp_saldos, f'class="nav-link active" aria-current="page" href="{url_dashboard}"')

        resp_balancete = self.client.get(url_balancete)
        self.assertEqual(resp_balancete.status_code, 200)
        self.assertContains(resp_balancete, f'class="nav-link active" aria-current="page" href="{url_balancete}"')
        self.assertNotContains(resp_balancete, f'class="nav-link active" aria-current="page" href="{url_dashboard}"')
