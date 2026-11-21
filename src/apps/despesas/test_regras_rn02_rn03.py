import shutil
import tempfile
from decimal import Decimal
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.utils import timezone
from PIL import Image

from apps.core.exceptions import (
    ComprovanteObrigatorioError,
    ImutabilidadeDespesaError,
    JustificativaRejeicaoObrigatoriaError,
    PermissaoNegadaDominioError,
    SegregacaoFuncoesError,
    TransicaoStatusInvalidaError,
)
from apps.despesas.models import Despesa, StatusDespesa
from apps.despesas.regras import (
    avaliar_alerta_estouro_rn02,
    calcular_soft_block_rn02,
    validar_segregacao_funcoes_rn03,
    verificar_impedimento_rn03,
)
from apps.financeiro.models import Coordenacao
from apps.usuarios.models import PapelUsuario, Usuario


class RegrasSoftBlockSegregacaoTestCase(TestCase):
    """
    Suíte de testes unitários dedicada ao motor de regras RN02 (Soft-block) e RN03 (Segregação de Funções).

    - O que faz: Valida cálculos exatos em `Decimal` de estouro de teto, metadados de alerta visual em
      vermelho (`alerta_estouro`), bloqueios de auto-aprovação/rejeição/liquidação e exceções semânticas.
    - Como faz: Testa isoladamente as funções puras de `apps.despesas.regras` e sua integração nos
      métodos transacionais do modelo `Despesa`.
    - Qual finalidade atende: Garante conformidade integral da Issue #12 e previne regressões em RN02 e RN03.
    """

    def setUp(self):
        """
        Prepara coordenação com teto definido, coordenador e dois tesoureiros distintos.

        - O que faz: Cria `SAUDE` (R$ 500,00), `coordenador`, `tesoureiro1`, `tesoureiro2` e mídia temporária.
        - Como faz: Usa `Coordenacao.objects.create`, `Usuario.objects.create_user` e `tempfile.mkdtemp()`.
        - Qual finalidade atende: Permite testar múltiplos cenários de limite de teto e segregação entre pares.
        """
        self.temp_media = tempfile.mkdtemp()
        self.coordenacao = Coordenacao.objects.create(
            nome='Saúde e Primeiros Socorros',
            sigla='SAUDE',
            teto_orcamentario=Decimal('500.00'),
        )
        self.coordenador = Usuario.objects.create_user(
            username='coord_saude',
            password='pass123',  # nosec B106
            papel=PapelUsuario.COORDENADOR,
            coordenacao=self.coordenacao,
        )
        self.tesoureiro1 = Usuario.objects.create_user(
            username='tesoureiro_um',
            password='pass123',  # nosec B106
            papel=PapelUsuario.TESOUREIRO,
        )
        self.tesoureiro2 = Usuario.objects.create_user(
            username='tesoureiro_dois',
            password='pass123',  # nosec B106
            papel=PapelUsuario.TESOUREIRO,
        )

    def tearDown(self):
        """
        Remove o diretório temporário de mídia após cada teste.

        - O que faz: Limpa os arquivos criados em disco temporário.
        - Como faz: Invoca `shutil.rmtree(self.temp_media, ignore_errors=True)`.
        - Qual finalidade atende: Mantém o ambiente limpo entre testes.
        """
        shutil.rmtree(self.temp_media, ignore_errors=True)

    def _criar_anexo(self) -> SimpleUploadedFile:
        """
        Cria um comprovante JPEG mínimo em memória para testes do domínio.

        - O que faz: Gera arquivo de imagem válido com Pillow.
        - Como faz: Serializa imagem 50x50 RGB para `SimpleUploadedFile`.
        - Qual finalidade atende: Satisfaz a obrigatoriedade documental (RN01) nos testes de RN02/RN03.
        """
        buf = BytesIO()
        Image.new('RGB', (50, 50), color=(200, 40, 40)).save(buf, format='JPEG')
        return SimpleUploadedFile('nota.jpg', buf.getvalue(), content_type='image/jpeg')

    def test_calcular_soft_block_rn02_todos_cenarios_limite(self):
        """
        Verifica o cálculo exato de estouro orçamentário em cenários normais, de borda e negativos.

        - O que faz: Testa valores abaixo do saldo, exatamente no teto, acima de saldo positivo e em saldo negativo.
        - Como faz: Invoca `calcular_soft_block_rn02` com combinações `Decimal` e valida o retorno booleano e excedente.
        - Qual finalidade atende: Evita erros de centavos ou distorções cumulativas quando o teto já estourou.
        """
        self.assertEqual(
            calcular_soft_block_rn02(Decimal('499.99'), Decimal('500.00')),
            (False, Decimal('0.00')),
        )
        self.assertEqual(
            calcular_soft_block_rn02(Decimal('500.00'), Decimal('500.00')),
            (False, Decimal('0.00')),
        )
        self.assertEqual(
            calcular_soft_block_rn02(Decimal('525.35'), Decimal('500.00')),
            (True, Decimal('25.35')),
        )
        self.assertEqual(
            calcular_soft_block_rn02(Decimal('40.00'), Decimal('-120.00')),
            (True, Decimal('40.00')),
        )

    def test_alerta_estouro_visual_e_integracao_no_model_despesa(self):
        """
        Verifica os metadados visuais de destaque em vermelho quando há estouro de teto (RN02).

        - O que faz: Submete uma despesa dentro do teto e outra estourando o teto, conferindo `alerta_estouro`.
        - Como faz: Avalia `despesa.alerta_estouro` e `avaliar_alerta_estouro_rn02` esperando `bg-success` e `bg-danger`.
        - Qual finalidade atende: Entrega informações prontas do domínio para o destaque vermelho na triagem.
        """
        with override_settings(MEDIA_ROOT=self.temp_media):
            d_ok = Despesa.objects.create(
                coordenacao=self.coordenacao,
                solicitante=self.coordenador,
                titulo='Termômetro Digital',
                valor=Decimal('200.00'),
                data_despesa=timezone.now().date(),
                comprovante=self._criar_anexo(),
                status=StatusDespesa.RASCUNHO,
            )
            d_ok.submeter(self.coordenador)
            self.assertFalse(d_ok.alerta_estouro['excede_teto'])
            self.assertEqual(d_ok.alerta_estouro['classe_badge'], 'bg-success')
            self.assertEqual(d_ok.alerta_estouro['texto_alerta'], 'Dentro do Teto')

            d_estouro = Despesa.objects.create(
                coordenacao=self.coordenacao,
                solicitante=self.coordenador,
                titulo='Desfibrilador Emergencial',
                valor=Decimal('450.50'),
                data_despesa=timezone.now().date(),
                comprovante=self._criar_anexo(),
                status=StatusDespesa.RASCUNHO,
            )
            d_estouro.submeter(self.coordenador)
            alerta = avaliar_alerta_estouro_rn02(d_estouro)
            self.assertTrue(alerta['excede_teto'])
            self.assertEqual(alerta['valor_excedente'], Decimal('150.50'))
            self.assertEqual(alerta['classe_badge'], 'bg-danger')
            self.assertIn('ESTOURO DE TETO (+R$ 150.50)', alerta['texto_alerta'])

    def test_segregacao_rn03_impede_auto_decisao_e_permite_segundo_tesoureiro(self):
        """
        Garante que tesoureiro não decide sobre compra própria, mas outro tesoureiro pode aprovar e liquidar (RN03).

        - O que faz: Cria despesa solicitada por `tesoureiro1`, valida `SegregacaoFuncoesError` em aprovar/rejeitar/liquidar
          com `tesoureiro1`, `PermissaoNegadaDominioError` com coordenador, e sucesso total com `tesoureiro2`.
        - Como faz: Testa `verificar_impedimento_rn03`, `validar_segregacao_funcoes_rn03` e os métodos do model.
        - Qual finalidade atende: Comprova a conformidade estrita de governança da RN03 sem travar reembolsos legítimos.
        """
        with override_settings(MEDIA_ROOT=self.temp_media):
            despesa = Despesa.objects.create(
                coordenacao=self.coordenacao,
                solicitante=self.tesoureiro1,
                titulo='Soro Fisiológico em Farmácia',
                valor=Decimal('85.00'),
                data_despesa=timezone.now().date(),
                comprovante=self._criar_anexo(),
                status=StatusDespesa.RASCUNHO,
            )
            despesa.submeter(self.tesoureiro1)

            self.assertTrue(verificar_impedimento_rn03(despesa, self.tesoureiro1))
            self.assertFalse(verificar_impedimento_rn03(despesa, self.tesoureiro2))

            with self.assertRaises(PermissaoNegadaDominioError):
                despesa.aprovar(self.coordenador)

            with self.assertRaises(SegregacaoFuncoesError) as ctx_aprovar:
                despesa.aprovar(self.tesoureiro1)
            self.assertIn('Segregação de Funções', str(ctx_aprovar.exception))

            with self.assertRaises(SegregacaoFuncoesError):
                despesa.rejeitar(self.tesoureiro1, motivo='Tentativa própria')

            with self.assertRaises(SegregacaoFuncoesError):
                validar_segregacao_funcoes_rn03(despesa=despesa, operador=self.tesoureiro1, acao='liquidar')

            # Outro tesoureiro aprova e liquida sem impedimentos
            despesa.aprovar(self.tesoureiro2)
            self.assertEqual(despesa.status, StatusDespesa.APROVADO)

            with self.assertRaises(SegregacaoFuncoesError):
                despesa.liquidar(self.tesoureiro1)

            despesa.liquidar(self.tesoureiro2)
            self.assertEqual(despesa.status, StatusDespesa.PAGO)

    def test_excecoes_semanticas_de_dominio_nos_demais_fluxos(self):
        """
        Valida o disparo das exceções tipadas de `apps.core.exceptions` nos métodos de `Despesa`.

        - O que faz: Confirma `ComprovanteObrigatorioError`, `TransicaoStatusInvalidaError`,
          `JustificativaRejeicaoObrigatoriaError` e `ImutabilidadeDespesaError`.
        - Como faz: Exercita fluxos inválidos no modelo aguardando cada subclasse específica de erro.
        - Qual finalidade atende: Garante diagnósticos semânticos consistentes em toda a camada de domínio.
        """
        with override_settings(MEDIA_ROOT=self.temp_media):
            d_sem_anexo = Despesa.objects.create(
                coordenacao=self.coordenacao,
                solicitante=self.coordenador,
                titulo='Sem Anexo',
                valor=Decimal('10.00'),
                data_despesa=timezone.now().date(),
                status=StatusDespesa.RASCUNHO,
            )
            with self.assertRaises(ComprovanteObrigatorioError):
                d_sem_anexo.submeter(self.coordenador)

            with self.assertRaises(TransicaoStatusInvalidaError):
                d_sem_anexo.aprovar(self.tesoureiro1)

            d_valida = Despesa.objects.create(
                coordenacao=self.coordenacao,
                solicitante=self.coordenador,
                titulo='Com Anexo',
                valor=Decimal('20.00'),
                data_despesa=timezone.now().date(),
                comprovante=self._criar_anexo(),
                status=StatusDespesa.RASCUNHO,
            )
            d_valida.submeter(self.coordenador)

            with self.assertRaises(JustificativaRejeicaoObrigatoriaError):
                d_valida.rejeitar(self.tesoureiro1, motivo='  ')

            d_valida.aprovar(self.tesoureiro1)
            with self.assertRaises(ImutabilidadeDespesaError):
                d_valida.cancelar(self.coordenador)
