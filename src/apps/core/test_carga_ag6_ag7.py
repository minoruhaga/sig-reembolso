import shutil
import tempfile
from decimal import Decimal
from io import StringIO

from django.core.management import call_command
from django.db.models import Sum
from django.test import TestCase, override_settings

from apps.despesas.models import CategoriaDespesa, Despesa, HistoricoTransicaoStatus, StatusDespesa
from apps.financeiro.models import Coordenacao
from apps.usuarios.models import PapelUsuario, Usuario


class CargaDadosAG6AG7TestCase(TestCase):
    """
    Suíte de testes automatizados para o comando de carga de dados reais do AG VI e AG VII (Issue #9).

    - O que faz: Valida a importação completa das 15 coordenações, dos coordenadores nominais do AG VII e das
      despesas históricas de Alimentação e Saúde do AG VI, além da idempotência e integridade monetária.
    - Como faz: Invoca `call_command('carregar_dados_ag6_ag7')` em diretório temporário de mídia e confere
      contagens, papéis RBAC, vínculos de coordenação, totais exatos em `Decimal` e logs de auditoria.
    - Qual finalidade atende: Garante que a massa realista da Issue #9 funcione de forma reprodutível no
      ambiente da equipe, nos testes de CI e na demonstração à banca.
    """

    def setUp(self):
        """
        Prepara diretório temporário isolado para arquivos de mídia gerados durante o teste.

        - O que faz: Cria um diretório temporário via `tempfile.mkdtemp` e registra sua limpeza em `tearDown`.
        - Como faz: Armazena o caminho em `self.temp_media` para uso com `@override_settings(MEDIA_ROOT=...)`.
        - Qual finalidade atende: Evita poluição da pasta local `src/media/` durante a execução da suíte de testes.
        """
        self.temp_media = tempfile.mkdtemp()

    def tearDown(self):
        """
        Remove o diretório temporário de mídia ao finalizar cada caso de teste.

        - O que faz: Exclui recursivamente os anexos sintéticos criados durante o teste.
        - Como faz: Chama `shutil.rmtree(self.temp_media, ignore_errors=True)`.
        - Qual finalidade atende: Mantém o workspace limpo após a execução automatizada.
        """
        shutil.rmtree(self.temp_media, ignore_errors=True)

    def test_carga_completa_coordenadores_ag7_e_gastos_ag6(self):
        """
        Verifica a carga fiel dos CSVs de coordenadores do AG VII e gastos históricos do AG VI.

        - O que faz: Executa `carregar_dados_ag6_ag7`, verifica as 15 coordenações, coordenadores vinculados e
          os lançamentos históricos de Assaí Atacadista, CEAGESP e Saúde com soma exata em `Decimal`.
        - Como faz: Utiliza `override_settings(MEDIA_ROOT=...)`, chama o comando e realiza asserções no ORM.
        - Qual finalidade atende: Valida integralmente os dois critérios de aceitação da Issue #9.
        """
        with override_settings(MEDIA_ROOT=self.temp_media):
            out = StringIO()
            call_command('carregar_dados_ag6_ag7', stdout=out)

            # 15 coordenações da fixture oficial
            self.assertEqual(Coordenacao.objects.count(), 15)

            # Coordenadores e Tesoureiros do AG VII vinculados às áreas corretas
            tesoureiro_minoru = Usuario.objects.get(username='ag7_minoru_tes')
            self.assertEqual(tesoureiro_minoru.papel, PapelUsuario.TESOUREIRO)
            self.assertEqual(tesoureiro_minoru.coordenacao.sigla, 'TES')

            coord_alim = Usuario.objects.get(username='ag7_gabiru_alim')
            self.assertEqual(coord_alim.papel, PapelUsuario.COORDENADOR)
            self.assertEqual(coord_alim.coordenacao.sigla, 'ALIM')

            coord_saude = Usuario.objects.get(username='ag7_akemi_saude')
            self.assertEqual(coord_saude.papel, PapelUsuario.COORDENADOR)
            self.assertEqual(coord_saude.coordenacao.sigla, 'SAUDE')

            # Compras históricas do Assaí, CEAGESP e Saúde com valores exatos em Decimal
            self.assertTrue(Despesa.objects.filter(titulo__icontains='Assaí Atacadista').exists())
            self.assertTrue(Despesa.objects.filter(titulo__icontains='CEAGESP').exists())

            total_alim = Despesa.objects.filter(
                categoria=CategoriaDespesa.ALIMENTACAO
            ).aggregate(total=Sum('valor'))['total']
            self.assertEqual(total_alim, Decimal('39398.83'))

            total_saude = Despesa.objects.filter(
                categoria=CategoriaDespesa.SAUDE
            ).aggregate(total=Sum('valor'))['total']
            self.assertEqual(total_saude, Decimal('1011.57'))

            # Verifica que há despesas PAGO e 1 pendente (ENVIADO) conforme alimentacao_gastos_ag6.csv
            self.assertTrue(Despesa.objects.filter(status=StatusDespesa.ENVIADO).exists())
            self.assertTrue(Despesa.objects.filter(status=StatusDespesa.PAGO).exists())
            self.assertGreater(HistoricoTransicaoStatus.objects.count(), 0)

    def test_idempotencia_reexecucao_carregar_dados_e_popular_demo(self):
        """
        Garante que reexecutar a carga e `popular_dados_demo` não gera registros duplicados.

        - O que faz: Executa `carregar_dados_ag6_ag7` duas vezes e `popular_dados_demo` em seguida.
        - Como faz: Compara as contagens de usuários, coordenações e despesas após múltiplas execuções.
        - Qual finalidade atende: Permite rodar o setup em ambientes já populados sem corromper saldos.
        """
        with override_settings(MEDIA_ROOT=self.temp_media):
            out = StringIO()
            call_command('carregar_dados_ag6_ag7', stdout=out)
            qtd_usuarios_1 = Usuario.objects.count()
            qtd_despesas_1 = Despesa.objects.count()

            call_command('carregar_dados_ag6_ag7', stdout=out)
            self.assertEqual(Usuario.objects.count(), qtd_usuarios_1)
            self.assertEqual(Despesa.objects.count(), qtd_despesas_1)

            # Executa também o popular_dados_demo integrado
            call_command('popular_dados_demo', stdout=out)
            self.assertTrue(Usuario.objects.filter(username='coord_cozinha').exists())
            self.assertEqual(Coordenacao.objects.count(), 15)
