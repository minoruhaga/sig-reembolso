import csv
from decimal import Decimal
from io import StringIO

from django.apps import apps
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.despesas.models import CategoriaDespesa, Despesa, FormaPagamentoOriginal, StatusDespesa, TipoDespesa
from apps.financeiro.models import Coordenacao
from apps.relatorios.services import gerar_balancete_sintetico, gerar_csv_despesas
from apps.usuarios.models import PapelUsuario, Usuario


class RelatoriosAppConfigTestCase(TestCase):
    """
    Testes de registro e integridade estrutural do aplicativo `apps.relatorios`.

    - O que faz: Valida que o app de relatórios está corretamente registrado em `INSTALLED_APPS`
      e acessível pelo registro central de aplicações do Django.
    - Como faz: Consulta `django.apps.apps.is_installed` e `apps.get_app_config('relatorios')`.
    - Qual finalidade atende: Garante que o esqueleto criado para a frente de relatórios (Issue #34)
      esteja íntegro e pronto para receber os serviços e rotas de exportação RF08.
    """

    def test_app_relatorios_esta_instalado_e_configurado(self):
        """
        Verifica se `apps.relatorios` está instalado e com `name` esperado no registry do Django.

        - O que faz: Confirma a presença de `apps.relatorios` e valida `AppConfig.name`.
        - Como faz: Executa `assertTrue(apps.is_installed('apps.relatorios'))` e compara `config.name`.
        - Qual finalidade atende: Previne falhas silenciosas de importação ou configuração antes da entrega RF08.
        """
        self.assertTrue(apps.is_installed('apps.relatorios'))
        app_config = apps.get_app_config('relatorios')
        self.assertEqual(app_config.name, 'apps.relatorios')


class PrestacaoContasRelatoriosTestCase(TestCase):
    """
    Suíte unitária e de integração da exportação CSV e do balancete sintético (Issue #34 / RF08).

    - O que faz: Confere somas em `Decimal`, filtros de coordenação, categoria e status, e o isolamento RBAC.
    - Como faz: Cria duas pastas e despesas com centavos fracionários, chama os serviços e os endpoints HTTP.
    - Qual finalidade atende: Garante a prestação de contas consolidada do AG VII sem vazamento entre coordenações.
    """

    def setUp(self):
        """
        Prepara pastas, papéis e lançamentos com centavos que denunciam erro de ponto flutuante.

        - O que faz: Cria ALIM e INFRA, coordenador, tesoureiro e administrador, e quatro despesas conhecidas.
        - Como faz: Persiste via ORM valores `Decimal('0.10')`, `Decimal('0.20')`, `Decimal('5.00')` e `Decimal('7.00')`.
        - Qual finalidade atende: Isola a massa da Issue #34 para validar precisão monetária e escopo por papel.
        """
        self.alim = Coordenacao.objects.create(
            nome='Alimentação',
            sigla='ALIM',
            teto_orcamentario=Decimal('1000.00'),
        )
        self.infra = Coordenacao.objects.create(
            nome='Infraestrutura',
            sigla='INFRA',
            teto_orcamentario=Decimal('500.00'),
        )
        self.coordenador = Usuario.objects.create_user(
            username='coord_alim',
            password='pass123',  # nosec B106
            papel=PapelUsuario.COORDENADOR,
            coordenacao=self.alim,
        )
        self.tesoureiro = Usuario.objects.create_user(
            username='tesoureiro_rel',
            password='pass123',  # nosec B106
            papel=PapelUsuario.TESOUREIRO,
            is_staff=True,
        )
        self.admin = Usuario.objects.create_user(
            username='admin_rel',
            password='pass123',  # nosec B106
            papel=PapelUsuario.ADMIN,
            is_staff=True,
        )
        self._criar_despesa(
            coordenacao=self.alim,
            titulo='Arroz',
            categoria=CategoriaDespesa.ALIMENTACAO,
            status=StatusDespesa.PAGO,
            valor=Decimal('0.10'),
        )
        self._criar_despesa(
            coordenacao=self.alim,
            titulo='Feijão',
            categoria=CategoriaDespesa.ALIMENTACAO,
            status=StatusDespesa.PAGO,
            valor=Decimal('0.20'),
        )
        self._criar_despesa(
            coordenacao=self.alim,
            titulo='Gasolina da cozinha',
            categoria=CategoriaDespesa.COMBUSTIVEL,
            status=StatusDespesa.ENVIADO,
            valor=Decimal('5.00'),
        )
        self._criar_despesa(
            coordenacao=self.infra,
            titulo='Lona',
            categoria=CategoriaDespesa.ALIMENTACAO,
            status=StatusDespesa.PAGO,
            valor=Decimal('7.00'),
        )

    def _criar_despesa(self, *, coordenacao, titulo, categoria, status, valor):
        """
        Grava uma despesa mínima para os cenários de relatório.

        - O que faz: Persiste título, categoria, status e valor na coordenação informada.
        - Como faz: Usa `Despesa.objects.create` com data de hoje e solicitante coordenador de ALIM.
        - Qual finalidade atende: Monta a base contábil controlada dos testes de RF08.
        """
        return Despesa.objects.create(
            coordenacao=coordenacao,
            solicitante=self.coordenador,
            titulo=titulo,
            categoria=categoria,
            tipo=TipoDespesa.REEMBOLSO,
            forma_pagamento_original=FormaPagamentoOriginal.PIX,
            valor=valor,
            data_despesa=timezone.now().date(),
            status=status,
        )

    def _ler_csv(self, conteudo: str):
        """
        Interpreta o CSV gerado pelo serviço.

        - O que faz: Devolve as linhas já separadas pelo delimitador da planilha.
        - Como faz: Usa `csv.reader` com separador `;` sobre o texto retornado por `gerar_csv_despesas`.
        - Qual finalidade atende: Evita asserts frágeis na conferência da exportação RF08.
        """
        return list(csv.reader(StringIO(conteudo), delimiter=';'))

    def test_balancete_soma_centavos_em_decimal_por_coordenacao_e_categoria(self):
        """
        Soma 0,10 e 0,20 como Decimal('0.30') na mesma categoria, sem contaminar a outra pasta.

        - O que faz: Gera o balancete do tesoureiro e localiza a linha ALIM/Alimentação.
        - Como faz: Compara `total` com `Decimal('0.30')` e o consolidado com `Decimal('12.30')`.
        - Qual finalidade atende: Cumpre a precisão monetária do balancete sintético (RF08).
        """
        balancete = gerar_balancete_sintetico(self.tesoureiro)
        self.assertIsInstance(balancete['total_geral'], Decimal)
        self.assertEqual(balancete['total_geral'], Decimal('12.30'))
        self.assertEqual(balancete['quantidade_total'], 4)

        alimentacao = next(
            linha for linha in balancete['linhas']
            if linha['sigla'] == 'ALIM' and linha['categoria'] == CategoriaDespesa.ALIMENTACAO
        )
        self.assertIsInstance(alimentacao['total'], Decimal)
        self.assertEqual(alimentacao['total'], Decimal('0.30'))
        self.assertEqual(alimentacao['quantidade'], 2)
        self.assertNotIsInstance(alimentacao['total'], float)

    def test_csv_filtra_categoria_e_status_com_valor_em_centavos(self):
        """
        Exporta só despesas pagas de alimentação e preserva o centavo na célula.

        - O que faz: Gera o CSV do tesoureiro com categoria e status informados.
        - Como faz: Lê o cabeçalho e confere as duas linhas de ALIM com valores `0,10` e `0,20`.
        - Qual finalidade atende: Atende ao filtro da planilha estruturada da Issue #34.
        """
        conteudo = gerar_csv_despesas(
            self.tesoureiro,
            categoria=CategoriaDespesa.ALIMENTACAO,
            status=StatusDespesa.PAGO,
        )
        linhas = self._ler_csv(conteudo)
        self.assertEqual(
            linhas[0],
            [
                'id',
                'data_despesa',
                'sigla_coordenacao',
                'coordenacao',
                'categoria',
                'categoria_descricao',
                'status',
                'status_descricao',
                'titulo',
                'tipo',
                'forma_pagamento',
                'valor',
            ],
        )
        valores = sorted(linha[-1] for linha in linhas[1:])
        siglas = {linha[2] for linha in linhas[1:]}
        self.assertEqual(valores, ['0,10', '0,20', '7,00'])
        self.assertEqual(siglas, {'ALIM', 'INFRA'})
        self.assertNotIn('5,00', valores)

    def test_coordenador_nao_enxerga_outra_pasta_nem_forcando_sigla(self):
        """
        Coordenador de ALIM não recebe lançamentos de INFRA, mesmo filtrando essa sigla.

        - O que faz: Gera balancete e CSV no escopo do coordenador e com filtro explícito de INFRA.
        - Como faz: Confere totais `Decimal` e a ausência da sigla INFRA no CSV forçado.
        - Qual finalidade atende: Aplica o RBAC da prestação de contas (RF01/RF08).
        """
        balancete = gerar_balancete_sintetico(self.coordenador)
        self.assertEqual(balancete['total_geral'], Decimal('5.30'))
        self.assertEqual({linha['sigla'] for linha in balancete['linhas']}, {'ALIM'})

        forcado = gerar_csv_despesas(self.coordenador, coordenacao='INFRA')
        linhas = self._ler_csv(forcado)
        self.assertEqual(len(linhas), 1)

        proprio = gerar_csv_despesas(self.coordenador, coordenacao='alim', status=StatusDespesa.PAGO)
        pagos = self._ler_csv(proprio)
        self.assertEqual(sorted(linha[-1] for linha in pagos[1:]), ['0,10', '0,20'])

    def test_endpoints_exigem_login_e_respeitam_rbac(self):
        """
        Visitante é enviado ao login; coordenador e tesoureiro recebem recortes diferentes.

        - O que faz: Exercita GET anônimo, de coordenador e de tesoureiro no balancete e no CSV.
        - Como faz: Usa o cliente de teste do Django e confere status, conteúdo HTML e anexo CSV.
        - Qual finalidade atende: Cobre o critério de endpoints protegidos da Issue #34.
        """
        anonimo = self.client.get(reverse('relatorios:balancete'))
        self.assertEqual(anonimo.status_code, 302)
        self.assertIn(reverse('usuarios:login'), anonimo.url)

        anonimo_csv = self.client.get(reverse('relatorios:exportar_csv'))
        self.assertEqual(anonimo_csv.status_code, 302)
        self.assertIn(reverse('usuarios:login'), anonimo_csv.url)

        self.client.force_login(self.coordenador)
        pagina = self.client.get(reverse('relatorios:balancete'))
        self.assertEqual(pagina.status_code, 200)
        self.assertContains(pagina, 'ALIM')
        self.assertContains(pagina, '0,30')
        self.assertContains(pagina, '5,30')
        self.assertNotContains(pagina, 'value="INFRA"')

        csv_coord = self.client.get(reverse('relatorios:exportar_csv'), {'status': StatusDespesa.ENVIADO})
        self.assertEqual(csv_coord.status_code, 200)
        self.assertIn('text/csv', csv_coord['Content-Type'])
        self.assertIn('prestacao_contas_ag7.csv', csv_coord['Content-Disposition'])
        corpo = csv_coord.content.decode('utf-8-sig')
        self.assertIn('5,00', corpo)
        self.assertNotIn('7,00', corpo)
        self.assertNotIn('INFRA', corpo)

        self.client.force_login(self.tesoureiro)
        pagina_tes = self.client.get(
            reverse('relatorios:balancete'),
            {'coordenacao': 'INFRA', 'categoria': CategoriaDespesa.ALIMENTACAO},
        )
        self.assertContains(pagina_tes, 'value="INFRA"')
        self.assertContains(pagina_tes, '7,00')
        self.assertNotContains(pagina_tes, '0,30')
        self.assertNotContains(pagina_tes, '5,00')

        self.client.force_login(self.admin)
        pagina_admin = self.client.get(reverse('relatorios:balancete'))
        self.assertContains(pagina_admin, 'ALIM')
        self.assertContains(pagina_admin, 'INFRA')
        self.assertContains(pagina_admin, '12,30')
