from decimal import Decimal
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from apps.core.exceptions import PermissaoNegadaDominioError, SigReembolsoDomainError
from apps.despesas.models import Despesa, StatusDespesa
from apps.financeiro.models import Coordenacao
from apps.financeiro.services import (
    atualizar_teto_orcamentario,
    calcular_termometro_coordenacao,
    obter_resumo_orcamentario,
)
from apps.usuarios.models import PapelUsuario, Usuario


class SaldosTetosFinanceiroTestCase(TestCase):
    """
    Suíte de testes unitários e de integração para cálculo dinâmico de saldos, termômetros e tetos (Issue #10).

    - O que faz: Valida a atualização instantânea dos indicadores em `Decimal` durante todo o ciclo de vida
      da despesa (`ENVIADO`, `APROVADO`, `PAGO`, `REJEITADO`, `CANCELADO`), o isolamento RBAC na API JSON e
      na view HTML, e a parametrização segura de tetos pela Tesouraria (RF02 e RF03).
    - Como faz: Cria duas coordenações (`ALIM` e `INFRA`), usuários coordenador e tesoureiro, executa
      transições reais no modelo `Despesa` e envia requisições HTTP GET/POST aos endpoints do app `financeiro`.
    - Qual finalidade atende: Garante precisão contábil de centavos (sem `float`) e integridade RBAC da Issue #10.
    """

    def setUp(self):
        """
        Prepara coordenações e usuários representativos para os cenários financeiros.

        - O que faz: Instancia `ALIM` (R$ 1.000,00), `INFRA` (R$ 500,00), coordenador e tesoureiro.
        - Como faz: Utiliza ORM transacional do Django com imagem JPEG mínima para anexos válidos.
        - Qual finalidade atende: Isola a massa de testes da Issue #10 de quaisquer fixtures externas.
        """
        self.alim = Coordenacao.objects.create(
            nome='Alimentação e Cozinha Central',
            sigla='ALIM',
            teto_orcamentario=Decimal('1000.00'),
        )
        self.infra = Coordenacao.objects.create(
            nome='Infraestrutura e Campo',
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
            username='tesoureiro_fin',
            password='pass123',  # nosec B106
            papel=PapelUsuario.TESOUREIRO,
            is_staff=True,
        )

    def _criar_comprovante_valido(self) -> SimpleUploadedFile:
        """
        Gera um comprovante JPEG válido em memória para submissões de teste.

        - O que faz: Cria um `SimpleUploadedFile` com imagem RGB válida.
        - Como faz: Desenha imagem 50x50 com Pillow em `BytesIO`.
        - Qual finalidade atende: Cumpre RN01 ao transicionar despesas durante os testes financeiros.
        """
        buf = BytesIO()
        Image.new('RGB', (50, 50), color=(20, 100, 60)).save(buf, format='JPEG')
        return SimpleUploadedFile('cupom.jpg', buf.getvalue(), content_type='image/jpeg')

    def test_calculo_dinamico_precisao_decimal_em_todas_transicoes(self):
        """
        Verifica atualização instantânea e exata de centavos no termômetro ao longo do workflow.

        - O que faz: Cria despesa `RASCUNHO` (não compromete), submete (`ENVIADO`), aprova (`APROVADO`),
          liquida (`PAGO`), e verifica outra despesa sendo rejeitada (`REJEITADO` libera saldo).
        - Como faz: Chama `calcular_termometro_coordenacao` após cada transição conferindo valores em `Decimal`.
        - Qual finalidade atende: Garante aderência estrita da RF03 com zero divergência de centavos.
        """
        d1 = Despesa.objects.create(
            coordenacao=self.alim,
            solicitante=self.coordenador,
            titulo='Compra Temperos',
            valor=Decimal('123.45'),
            data_despesa=timezone.now().date(),
            comprovante=self._criar_comprovante_valido(),
            status=StatusDespesa.RASCUNHO,
        )
        # RASCUNHO não compromete verba
        ind = calcular_termometro_coordenacao(self.alim)
        self.assertEqual(ind['total_comprometido'], Decimal('0.00'))
        self.assertEqual(ind['saldo_disponivel'], Decimal('1000.00'))

        # Submissão -> ENVIADO sensibiliza imediatamente
        d1.submeter(self.coordenador)
        ind = calcular_termometro_coordenacao(self.alim)
        self.assertEqual(ind['total_enviado'], Decimal('123.45'))
        self.assertEqual(ind['total_comprometido'], Decimal('123.45'))
        self.assertEqual(ind['saldo_disponivel'], Decimal('876.55'))

        # Aprovação -> migra de ENVIADO para APROVADO
        d1.aprovar(self.tesoureiro)
        ind = calcular_termometro_coordenacao(self.alim)
        self.assertEqual(ind['total_enviado'], Decimal('0.00'))
        self.assertEqual(ind['total_aprovado'], Decimal('123.45'))
        self.assertEqual(ind['saldo_disponivel'], Decimal('876.55'))

        # Liquidação -> migra de APROVADO para PAGO
        d1.liquidar(self.tesoureiro)
        ind = calcular_termometro_coordenacao(self.alim)
        self.assertEqual(ind['total_aprovado'], Decimal('0.00'))
        self.assertEqual(ind['total_pago'], Decimal('123.45'))
        self.assertEqual(ind['saldo_disponivel'], Decimal('876.55'))

        # Segunda despesa submetida e depois rejeitada deve liberar o saldo
        d2 = Despesa.objects.create(
            coordenacao=self.alim,
            solicitante=self.coordenador,
            titulo='Item Duplicado',
            valor=Decimal('200.55'),
            data_despesa=timezone.now().date(),
            comprovante=self._criar_comprovante_valido(),
            status=StatusDespesa.RASCUNHO,
        )
        d2.submeter(self.coordenador)
        ind = calcular_termometro_coordenacao(self.alim)
        self.assertEqual(ind['saldo_disponivel'], Decimal('676.00'))

        d2.rejeitar(self.tesoureiro, motivo='Nota duplicada')
        ind = calcular_termometro_coordenacao(self.alim)
        self.assertEqual(ind['total_comprometido'], Decimal('123.45'))
        self.assertEqual(ind['saldo_disponivel'], Decimal('876.55'))

    def test_api_e_view_saldos_respeitam_isolamento_rbac(self):
        """
        Verifica o isolamento por papel na view HTML e no endpoint JSON `api_saldos`.

        - O que faz: Autentica coordenador de ALIM e tesoureiro e compara os retornos HTML e JSON.
        - Como faz: Faz GET em `financeiro:saldos` e `financeiro:api_saldos` verificando `status_code` e payloads.
        - Qual finalidade atende: Impede vazamento de saldos de outras coordenações para coordenadores de área.
        """
        Despesa.objects.create(
            coordenacao=self.alim,
            solicitante=self.coordenador,
            titulo='Gás Cozinha',
            valor=Decimal('650.00'),
            data_despesa=timezone.now().date(),
            comprovante=self._criar_comprovante_valido(),
            status=StatusDespesa.APROVADO,
        )

        # Coordenador vê apenas ALIM
        self.client.force_login(self.coordenador)
        resp_html = self.client.get(reverse('financeiro:saldos'))
        self.assertEqual(resp_html.status_code, 200)
        self.assertContains(resp_html, 'ALIM')
        self.assertNotContains(resp_html, 'INFRA')

        resp_json = self.client.get(reverse('financeiro:api_saldos'))
        self.assertEqual(resp_json.status_code, 200)
        dados = resp_json.json()
        self.assertEqual(len(dados['coordenacoes']), 1)
        self.assertEqual(dados['coordenacoes'][0]['sigla'], 'ALIM')
        self.assertEqual(dados['coordenacoes'][0]['saldo_disponivel'], '350.00')
        self.assertEqual(dados['coordenacoes'][0]['percentual_consumido'], 65.0)
        self.assertEqual(dados['coordenacoes'][0]['nivel_alerta'], 'warning')

        # Tesoureiro vê ambas as pastas e resumo consolidado
        self.client.force_login(self.tesoureiro)
        resp_tes = self.client.get(reverse('financeiro:api_saldos'))
        dados_tes = resp_tes.json()
        self.assertEqual(len(dados_tes['coordenacoes']), 2)
        self.assertEqual(dados_tes['totais']['total_orcado'], '1500.00')
        self.assertEqual(dados_tes['totais']['total_saldo_livre'], '850.00')

    def test_atualizar_teto_orcamentario_apenas_tesouraria_e_nao_negativo(self):
        """
        Verifica a regra RF02 para ajuste de teto orçamentário e bloqueio de acesso não autorizado.

        - O que faz: Testa atualização válida pelo tesoureiro (via view e service), rejeição de valor negativo
          e bloqueio HTTP 403 quando um coordenador tenta alterar o teto.
        - Como faz: Invoca `atualizar_teto_orcamentario` e faz POST em `financeiro:atualizar_teto`.
        - Qual finalidade atende: Protege a governança financeira dos tetos das 15 coordenações.
        """
        # Coordenador recebe 403 na view e PermissaoNegadaDominioError no service
        with self.assertRaises(PermissaoNegadaDominioError):
            atualizar_teto_orcamentario(
                usuario=self.coordenador,
                coordenacao=self.alim,
                novo_teto=Decimal('5000.00'),
            )

        self.client.force_login(self.coordenador)
        resp_forbidden = self.client.post(
            reverse('financeiro:atualizar_teto', args=[self.alim.id]),
            {'novo_teto': '5000.00'},
        )
        self.assertEqual(resp_forbidden.status_code, 403)

        # Tesoureiro não pode definir valor negativo
        with self.assertRaises(SigReembolsoDomainError):
            atualizar_teto_orcamentario(
                usuario=self.tesoureiro,
                coordenacao=self.alim,
                novo_teto=Decimal('-10.00'),
            )

        # Tesoureiro atualiza corretamente via view
        self.client.force_login(self.tesoureiro)
        resp_ok = self.client.post(
            reverse('financeiro:atualizar_teto', args=[self.alim.id]),
            {'novo_teto': '1250.75'},
        )
        self.assertRedirects(resp_ok, reverse('financeiro:saldos'))
        self.alim.refresh_from_db()
        self.assertEqual(self.alim.teto_orcamentario, Decimal('1250.75'))

        resumo = obter_resumo_orcamentario(self.tesoureiro, sigla='ALIM')
        self.assertEqual(resumo['coordenacoes'][0]['teto_orcamentario'], Decimal('1250.75'))
