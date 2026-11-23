from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from apps.despesas.models import Despesa, StatusDespesa
from apps.despesas.services import simular_impacto_orcamentario
from apps.financeiro.models import Coordenacao
from apps.usuarios.models import PapelUsuario, Usuario


class TelaMobileDespesaTestCase(TestCase):
    """
    Testes da tela mobile de lançamento de despesa e do termômetro de verba (Issue #8).

    - O que faz: Verifica a captura nativa pela câmera (RNF01), a coordenação já preenchida, a data inicial
      em formato aceito pelo `<input type="date">`, a projeção de saldo com soft-block (RN02/RF03) e o
      recorte RBAC do endpoint de prévia.
    - Como faz: Cria duas coordenações, um coordenador vinculado a uma delas e uma despesa já enviada que
      consome parte do teto; usa o test client do Django e chama o serviço de domínio diretamente.
    - Qual finalidade atende: Garante que o voluntário em campo abra a câmera em poucos toques e veja, antes
      de enviar, se a compra cabe na verba, sem que a tela vaze saldos de outras coordenações.
    """

    def setUp(self):
        """
        Prepara coordenações, coordenador vinculado e uma despesa ENVIADA de R$ 700,00 na pasta ALIM.
        """
        self.alim = Coordenacao.objects.create(
            nome='Alimentação', sigla='ALIM', teto_orcamentario=Decimal('1000.00'), ativo=True
        )
        self.infra = Coordenacao.objects.create(
            nome='Infraestrutura', sigla='INFRA', teto_orcamentario=Decimal('500.00'), ativo=True
        )
        self.coordenador = Usuario.objects.create_user(
            username='coord_alim', password='senha_teste_123',
            papel=PapelUsuario.COORDENADOR, coordenacao=self.alim,
        )
        Despesa.objects.create(
            coordenacao=self.alim, solicitante=self.coordenador, titulo='Feira',
            valor=Decimal('700.00'), data_despesa='2026-11-01', status=StatusDespesa.ENVIADO,
        )
        self.client.login(username='coord_alim', password='senha_teste_123')

    def test_formulario_abre_camera_traseira_e_preenche_coordenacao(self):
        """
        A tela nova traz input de arquivo com `capture="environment"`, coordenação do usuário e data ISO.
        """
        resposta = self.client.get(reverse('despesas:nova'))

        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, 'capture="environment"')
        self.assertContains(resposta, 'Tirar foto da NF ou recibo')
        self.assertEqual(resposta.context['form']['coordenacao'].value(), self.alim.id)
        self.assertRegex(
            resposta.content.decode(), r'name="data_despesa" value="\d{4}-\d{2}-\d{2}"'
        )

    def test_termometro_inicial_mostra_saldo_da_coordenacao(self):
        """
        O primeiro carregamento já traz a prévia do termômetro, sem depender de JavaScript.
        """
        resposta = self.client.get(reverse('despesas:nova'))

        previa = resposta.context['previa']
        self.assertEqual(previa['sigla'], 'ALIM')
        self.assertEqual(previa['saldo_atual'], Decimal('300.00'))
        self.assertFalse(previa['excede_teto'])
        self.assertContains(resposta, 'Saldo livre: R$ 300,00.')

    def test_simulacao_dentro_do_saldo(self):
        """
        Compra de R$ 120,00 com saldo de R$ 300,00 deixa R$ 180,00 e não aciona RN02.
        """
        previa = simular_impacto_orcamentario(
            usuario=self.coordenador, coordenacao_id=self.alim.id, valor=Decimal('120.00')
        )

        self.assertEqual(previa['saldo_apos'], Decimal('180.00'))
        self.assertFalse(previa['excede_teto'])
        self.assertEqual(previa['pct_comprometido'], 70.0)
        self.assertEqual(previa['pct_compra'], 12.0)

    def test_simulacao_acima_do_saldo_sinaliza_soft_block(self):
        """
        Compra de R$ 450,00 com saldo de R$ 300,00 passa do teto em R$ 150,00 (RN02) sem bloquear nada.
        """
        previa = simular_impacto_orcamentario(
            usuario=self.coordenador, coordenacao_id=self.alim.id, valor=Decimal('450.00')
        )

        self.assertTrue(previa['excede_teto'])
        self.assertEqual(previa['valor_excedente'], Decimal('150.00'))
        self.assertEqual(previa['pct_compra'], 30.0)
        self.assertEqual(Despesa.objects.count(), 1)

    def test_endpoint_previa_responde_json_com_valores_em_texto(self):
        """
        O endpoint devolve montantes como strings com duas casas (sem float) e aceita vírgula decimal.
        """
        resposta = self.client.get(
            reverse('despesas:previa_orcamento'), {'coordenacao': self.alim.id, 'valor': '450,00'}
        )

        self.assertEqual(resposta.status_code, 200)
        dados = resposta.json()
        self.assertEqual(dados['saldo_atual'], '300.00')
        self.assertEqual(dados['valor_excedente'], '150.00')
        self.assertTrue(dados['excede_teto'])

    def test_endpoint_previa_nao_expoe_outra_coordenacao(self):
        """
        Coordenador não vê o saldo de uma pasta que não é a sua (RF01): resposta 404.
        """
        resposta = self.client.get(
            reverse('despesas:previa_orcamento'), {'coordenacao': self.infra.id, 'valor': '10'}
        )
        self.assertEqual(resposta.status_code, 404)

    def test_endpoint_previa_rejeita_valor_invalido(self):
        """
        Valor não numérico devolve 400 em vez de erro interno.
        """
        resposta = self.client.get(
            reverse('despesas:previa_orcamento'), {'coordenacao': self.alim.id, 'valor': 'abc'}
        )
        self.assertEqual(resposta.status_code, 400)

    def test_endpoint_previa_exige_login(self):
        """
        Usuário anônimo é redirecionado ao login.
        """
        self.client.logout()
        resposta = self.client.get(reverse('despesas:previa_orcamento'), {'coordenacao': self.alim.id})
        self.assertEqual(resposta.status_code, 302)


class ValorEmReaisTestCase(TestCase):
    """
    Testes da leitura e exibição do valor em reais usado pela máscara de centavos da tela mobile.

    - O que faz: Confere que "1.250,40" (formato da máscara), "1250.40" (formato técnico) e textos inválidos
      são tratados corretamente pelo formulário, pela prévia e pela tela de edição.
    - Como faz: Chama `converter_valor_reais` diretamente e usa o test client para enviar e abrir despesas.
    - Qual finalidade atende: Garante que digitar "1000" e ver "10,00" na tela grave exatamente R$ 10,00,
      sem perda de centavos.
    """

    def setUp(self):
        """
        Cria coordenação, coordenador vinculado e faz login.
        """
        self.coordenacao = Coordenacao.objects.create(
            nome='Alimentação', sigla='ALIM', teto_orcamentario=Decimal('5000.00'), ativo=True
        )
        self.coordenador = Usuario.objects.create_user(
            username='coord_valor', password='senha_teste_123',
            papel=PapelUsuario.COORDENADOR, coordenacao=self.coordenacao,
        )
        self.client.login(username='coord_valor', password='senha_teste_123')

    def test_converter_valor_reais_aceita_formatos_da_tela(self):
        """
        Formato brasileiro, técnico e com símbolo viram o mesmo `Decimal`; lixo vira `None`.
        """
        from apps.despesas.forms import converter_valor_reais

        self.assertEqual(converter_valor_reais('1.250,40'), Decimal('1250.40'))
        self.assertEqual(converter_valor_reais('10,00'), Decimal('10.00'))
        self.assertEqual(converter_valor_reais('R$ 0,05'), Decimal('0.05'))
        self.assertEqual(converter_valor_reais('185.50'), Decimal('185.50'))
        self.assertIsNone(converter_valor_reais('abc'))
        self.assertIsNone(converter_valor_reais(''))
        self.assertIsNone(converter_valor_reais('NaN'))

    def test_rascunho_com_valor_mascarado_grava_decimal_exato(self):
        """
        O valor "1.250,40" enviado pela máscara é gravado como R$ 1.250,40.
        """
        resposta = self.client.post(reverse('despesas:nova'), {
            'coordenacao': self.coordenacao.id,
            'titulo': 'Compra de hortifruti',
            'categoria': 'ALIMENTACAO',
            'tipo': 'REEMBOLSO',
            'forma_pagamento_original': 'PIX',
            'valor': '1.250,40',
            'data_despesa': '2026-11-20',
            'acao': 'rascunho',
        })

        self.assertRedirects(resposta, reverse('despesas:minhas'))
        self.assertEqual(Despesa.objects.get().valor, Decimal('1250.40'))

    def test_valor_invalido_mostra_erro_no_campo(self):
        """
        Texto que não é número não grava a despesa e aponta o erro no campo de valor.
        """
        resposta = self.client.post(reverse('despesas:nova'), {
            'coordenacao': self.coordenacao.id,
            'titulo': 'Compra',
            'valor': 'dez reais',
            'data_despesa': '2026-11-20',
            'acao': 'rascunho',
        })

        self.assertEqual(resposta.status_code, 200)
        self.assertIn('valor', resposta.context['form'].errors)
        self.assertEqual(Despesa.objects.count(), 0)

    def test_edicao_exibe_valor_salvo_no_formato_brasileiro(self):
        """
        Ao abrir um rascunho de R$ 1.250,40, o campo mostra "1.250,40".
        """
        despesa = Despesa.objects.create(
            coordenacao=self.coordenacao, solicitante=self.coordenador, titulo='Feira',
            valor=Decimal('1250.40'), data_despesa='2026-11-01', status=StatusDespesa.RASCUNHO,
        )

        resposta = self.client.get(reverse('despesas:editar', args=[despesa.id]))

        self.assertContains(resposta, 'value="1.250,40"')

    def test_previa_aceita_valor_mascarado(self):
        """
        A prévia do termômetro lê o valor no formato da máscara.
        """
        resposta = self.client.get(
            reverse('despesas:previa_orcamento'), {'coordenacao': self.coordenacao.id, 'valor': '1.250,40'}
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json()['saldo_apos'], '3749.60')

    def test_envio_sem_cupom_explica_erro_sem_codigo_de_regra(self):
        """
        A mensagem de cupom ausente diz o que fazer e não mostra códigos como "RN01".
        """
        resposta = self.client.post(reverse('despesas:nova'), {
            'coordenacao': self.coordenacao.id,
            'titulo': 'Compra',
            'categoria': 'ALIMENTACAO',
            'tipo': 'REEMBOLSO',
            'forma_pagamento_original': 'PIX',
            'valor': '10,00',
            'data_despesa': '2026-11-20',
            'acao': 'submeter',
        })

        self.assertContains(resposta, 'Anexe a foto ou o PDF da NF ou recibo para enviar a despesa à tesouraria.')
        self.assertNotRegex(resposta.content.decode(), r'RN\d{2}')

    def test_valor_zero_pede_valor_maior_que_zero(self):
        """
        Valor "0,00" não grava a despesa e a mensagem diz o que digitar, sem jargão.
        """
        resposta = self.client.post(reverse('despesas:nova'), {
            'coordenacao': self.coordenacao.id,
            'titulo': 'Compra',
            'categoria': 'ALIMENTACAO',
            'tipo': 'REEMBOLSO',
            'forma_pagamento_original': 'PIX',
            'valor': '0,00',
            'data_despesa': '2026-11-20',
            'acao': 'rascunho',
        })

        self.assertFormError(resposta.context['form'], 'valor', 'Informe um valor maior que R$ 0,00.')
        self.assertEqual(Despesa.objects.count(), 0)

    def test_rascunho_salvo_explica_proximo_passo(self):
        """
        Depois de salvar o rascunho, a mensagem diz que falta anexar a NF ou recibo e enviar.
        """
        resposta = self.client.post(reverse('despesas:nova'), {
            'coordenacao': self.coordenacao.id,
            'titulo': 'Compra',
            'categoria': 'ALIMENTACAO',
            'tipo': 'REEMBOLSO',
            'forma_pagamento_original': 'PIX',
            'valor': '10,00',
            'data_despesa': '2026-11-20',
            'acao': 'rascunho',
        }, follow=True)

        despesa = Despesa.objects.get()
        self.assertContains(
            resposta,
            f'Rascunho #{despesa.id} salvo. Você pode voltar depois para anexar a foto da NF ou recibo e enviar.',
        )
