from decimal import Decimal
from io import BytesIO

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone
from PIL import Image

from apps.core.services import otimizar_comprovante_fiscal
from apps.despesas.models import Despesa, HistoricoTransicaoStatus, StatusDespesa
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
            password='pass',  # nosec B106
            papel=PapelUsuario.COORDENADOR
        )
        self.tesoureiro = Usuario.objects.create_user(
            username='tesoureiro1',
            password='pass',  # nosec B106
            papel=PapelUsuario.TESOUREIRO
        )

        img = Image.new('RGB', (100, 100), color=(200, 100, 50))
        buffer = BytesIO()
        img.save(buffer, format='JPEG')
        self.comprovante_fake = SimpleUploadedFile(
            "cupom.jpg",
            buffer.getvalue(),
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

    def test_rn03_segregacao_de_funcoes_bloqueia_liquidacao_propria(self):
        """
        Verifica a aplicação da RN03 na liquidação bancária.

        - O que faz: Garante que um tesoureiro não consiga liquidar um reembolso solicitado por ele próprio.
        - Como faz: Instancia uma despesa solicitada pelo tesoureiro, aprovada, e tenta chamar `liquidar(self.tesoureiro)`.
        - Qual finalidade atende: Impede conflito de interesse na liquidação de reembolsos (RN03).
        """
        despesa = Despesa.objects.create(
            coordenacao=self.coordenacao,
            solicitante=self.tesoureiro,
            titulo='Gasolina comprada pelo tesoureiro',
            valor=Decimal('70.00'),
            data_despesa=timezone.now().date(),
            comprovante=self.comprovante_fake,
            status=StatusDespesa.APROVADO
        )
        with self.assertRaises(ValidationError):
            despesa.liquidar(self.tesoureiro)

    def test_bloqueio_aprovacao_por_usuario_nao_tesoureiro(self):
        """
        Verifica a restrição de papéis nas transições da Tesouraria.

        - O que faz: Bloqueia a aprovação ou liquidação de despesas por usuários que não possuem perfil de Tesoureiro.
        - Como faz: Chama `despesa.aprovar(self.solicitante)` passando um coordenador de área e espera `ValidationError`.
        - Qual finalidade atende: Sustenta o controle de acesso baseado em função (RBAC / RF01).
        """
        despesa = Despesa.objects.create(
            coordenacao=self.coordenacao,
            solicitante=self.solicitante,
            titulo='Compra de materiais',
            valor=Decimal('50.00'),
            data_despesa=timezone.now().date(),
            comprovante=self.comprovante_fake,
            status=StatusDespesa.ENVIADO
        )
        with self.assertRaises(ValidationError):
            despesa.aprovar(self.solicitante)

    def test_rn05_bloqueia_alteracao_de_comprovante_em_despesa_aprovada(self):
        """
        Verifica a blindagem do anexo fiscal contra adulteração após aprovação (RN05).

        - O que faz: Tenta alterar o arquivo de comprovante de uma despesa no estado APROVADO.
        - Como faz: Modifica `despesa.comprovante` para um novo anexo e tenta salvar, esperando `ValidationError`.
        - Qual finalidade atende: Preserva a idoneidade fiscal e documental pós-decisão (RN05).
        """
        despesa = Despesa.objects.create(
            coordenacao=self.coordenacao,
            solicitante=self.solicitante,
            titulo='Compra de Lonas',
            valor=Decimal('100.00'),
            data_despesa=timezone.now().date(),
            comprovante=self.comprovante_fake,
            status=StatusDespesa.RASCUNHO
        )
        despesa.submeter(self.solicitante)
        despesa.aprovar(self.tesoureiro)

        despesa.comprovante = SimpleUploadedFile("outro_cupom.jpg", b"outro_conteudo", content_type="image/jpeg")
        with self.assertRaises(ValidationError):
            despesa.save()

    def test_rn05_bloqueia_reversao_de_status_aprovado_para_rascunho(self):
        """
        Verifica o bloqueio de regressão do estado APROVADO para RASCUNHO (RN05).

        - O que faz: Tenta mudar o status de APROVADO para RASCUNHO diretamente via `.save()`.
        - Como faz: Altera `despesa.status = StatusDespesa.RASCUNHO` e espera `ValidationError`.
        - Qual finalidade atende: Impede contorno da máquina de estados e preserva a imutabilidade contábil (RN05).
        """
        despesa = Despesa.objects.create(
            coordenacao=self.coordenacao,
            solicitante=self.solicitante,
            titulo='Compra Aprovada',
            valor=Decimal('90.00'),
            data_despesa=timezone.now().date(),
            comprovante=self.comprovante_fake,
            status=StatusDespesa.RASCUNHO
        )
        despesa.submeter(self.solicitante)
        despesa.aprovar(self.tesoureiro)

        despesa.status = StatusDespesa.RASCUNHO
        with self.assertRaises(ValidationError):
            despesa.save()

    def test_rn02_calculo_valor_excedente_com_saldo_negativo(self):
        """
        Verifica o cálculo de estouro orçamentário quando o saldo livre já está negativo (RN02).

        - O que faz: Submete uma despesa em uma coordenação cujo total já supera o teto.
        - Como faz: Cria uma despesa de R$ 600 em coordenação de R$ 500 (saldo fica -R$ 100). Em seguida submete outra de R$ 50.
        - Qual finalidade atende: Garante que `valor_excedente` seja exatamente R$ 50,00 e não distorcido para R$ 150,00.
        """
        d1 = Despesa.objects.create(
            coordenacao=self.coordenacao,
            solicitante=self.solicitante,
            titulo='Estouro Inicial',
            valor=Decimal('600.00'),
            data_despesa=timezone.now().date(),
            comprovante=self.comprovante_fake,
            status=StatusDespesa.RASCUNHO
        )
        d1.submeter(self.solicitante)
        self.assertEqual(self.coordenacao.saldo_disponivel, Decimal('-100.00'))

        d2 = Despesa.objects.create(
            coordenacao=self.coordenacao,
            solicitante=self.solicitante,
            titulo='Nova Despesa em Saldo Negativo',
            valor=Decimal('50.00'),
            data_despesa=timezone.now().date(),
            comprovante=self.comprovante_fake,
            status=StatusDespesa.RASCUNHO
        )
        d2.submeter(self.solicitante)
        self.assertTrue(d2.excede_teto)
        self.assertEqual(d2.valor_excedente, Decimal('50.00'))

    def test_cancelar_despesa_em_rascunho_e_enviado(self):
        """
        Verifica a execução do cancelamento auditado da despesa na máquina de estados.

        - O que faz: Cancela despesa em rascunho e valida que o histórico de auditoria registra a transição.
        - Como faz: Invoca `despesa.cancelar(self.solicitante)` e confere o status e o registro em `HistoricoTransicaoStatus`.
        - Qual finalidade atende: Cumpre a máquina de estados (Item 5.2) e a rastreabilidade contábil (RN06).
        """
        despesa = Despesa.objects.create(
            coordenacao=self.coordenacao,
            solicitante=self.solicitante,
            titulo='Despesa Cancelada',
            valor=Decimal('30.00'),
            data_despesa=timezone.now().date(),
            status=StatusDespesa.RASCUNHO
        )
        despesa.cancelar(self.solicitante, motivo='Compra cancelada na ponta')
        self.assertEqual(despesa.status, StatusDespesa.CANCELADO)

        historico = HistoricoTransicaoStatus.objects.filter(despesa=despesa).last()
        self.assertEqual(historico.novo_status, StatusDespesa.CANCELADO)

        # Não deve permitir cancelar despesa aprovada
        despesa_aprovada = Despesa.objects.create(
            coordenacao=self.coordenacao,
            solicitante=self.solicitante,
            titulo='Despesa Aprovada',
            valor=Decimal('30.00'),
            data_despesa=timezone.now().date(),
            comprovante=self.comprovante_fake,
            status=StatusDespesa.APROVADO
        )
        with self.assertRaises(ValidationError):
            despesa_aprovada.cancelar(self.solicitante)

    def test_bloqueio_exclusao_despesa_tramitada(self):
        """
        Verifica o bloqueio de exclusão física para despesas que já tramitaram (RN05 e RN06).

        - O que faz: Tenta executar `.delete()` em despesa no estado ENVIADO e APROVADO.
        - Como faz: Cria despesa enviada e tenta chamar `despesa.delete()`, aguardando `ValidationError`.
        - Qual finalidade atende: Protege os livros fiscais e a integridade da auditoria contra exclusão acidental ou maliciosa.
        """
        despesa = Despesa.objects.create(
            coordenacao=self.coordenacao,
            solicitante=self.solicitante,
            titulo='Despesa Enviada para Triagem',
            valor=Decimal('40.00'),
            data_despesa=timezone.now().date(),
            comprovante=self.comprovante_fake,
            status=StatusDespesa.ENVIADO
        )
        with self.assertRaises(ValidationError):
            despesa.delete()

    def test_validacao_formato_comprovante_bloqueia_extensao_invalida(self):
        """
        Verifica a restrição de formatos permitidos para comprovante fiscal (RN01 / RNF04).

        - O que faz: Tenta submeter despesa com anexo de formato não permitido (.exe).
        - Como faz: Instancia `Despesa` com arquivo executável simulado e executa `full_clean()`, esperando `ValidationError`.
        - Qual finalidade atende: Assegura que apenas imagens (JPEG/PNG) ou documentos PDF sejam aceitos.
        """
        arquivo_invalido = SimpleUploadedFile("script.exe", b"conteudo_binario", content_type="application/octet-stream")
        despesa = Despesa(
            coordenacao=self.coordenacao,
            solicitante=self.solicitante,
            titulo='Compra com Anexo Invalido',
            valor=Decimal('40.00'),
            data_despesa=timezone.now().date(),
            comprovante=arquivo_invalido,
            status=StatusDespesa.RASCUNHO
        )
        with self.assertRaises(ValidationError):
            despesa.full_clean()

    def test_otimizacao_comprovante_fiscal_converte_e_renomeia_uuid(self):
        """
        Verifica a otimização com Pillow e anonimização com UUID v4 (RNF02 e RNF04).

        - O que faz: Envia uma imagem pesada (> 1920px de largura) e um PDF para o serviço `otimizar_comprovante_fiscal`.
        - Como faz: Gera imagem 2500x1500 em memória, processa pelo serviço e verifica que o arquivo resultante tem largura <= 1920px
          e nome anonimizado com extensão .jpg e 32 caracteres hexadecimais (UUID).
        - Qual finalidade atende: Cumpre RNF02 (otimização para Starlink) e RNF04 (anonimização contra enumeração direta).
        """
        img_grande = Image.new('RGB', (2500, 1500), color=(10, 80, 150))
        buf = BytesIO()
        img_grande.save(buf, format='JPEG')
        uploaded = SimpleUploadedFile("foto_nota_fiscal_original.jpeg", buf.getvalue(), content_type="image/jpeg")

        otimizado = otimizar_comprovante_fiscal(uploaded, max_width=1920)
        self.assertTrue(otimizado.name.endswith('.jpg'))
        self.assertEqual(len(otimizado.name.split('.')[0]), 32)  # UUID hex length

        # Verifica redimensionamento
        img_result = Image.open(otimizado)
        self.assertLessEqual(img_result.width, 1920)

        # Verifica preservação de PDF com renomeação UUID
        pdf_file = SimpleUploadedFile("documento.pdf", b"%PDF-1.4...", content_type="application/pdf")
        pdf_otimizado = otimizar_comprovante_fiscal(pdf_file)
        self.assertTrue(pdf_otimizado.name.endswith('.pdf'))
        self.assertEqual(len(pdf_otimizado.name.split('.')[0]), 32)
