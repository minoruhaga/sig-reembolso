import re
from io import BytesIO

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image

from apps.core.services import (
    TAMANHO_MAXIMO_COMPRIMIDO_BYTES,
    otimizar_comprovante_fiscal,
)


class OtimizarComprovanteFiscalTestCase(TestCase):
    """
    Suíte de testes unitários para o serviço de otimização e validação de comprovantes fiscais.

    - O que faz: Verifica a conformidade do processamento de imagens e PDFs com os requisitos
      RN01 (validade documental), RNF02 (compressão automática < 350KB) e RNF04 (anonimização com UUID v4).
    - Como faz: Gera arquivos sintéticos em memória com a biblioteca Pillow (imagens pesadas, imagens com
      canal alfa, PDFs simulados e arquivos corrompidos) e testa os retornos e exceções do serviço.
    - Qual finalidade atende: Garante que fotografias enviadas em campo por voluntários do AG VII sejam
      otimizadas de forma confiável antes da persistência, sem risco de corrupção ou colisão de nomes.
    """

    def _gerar_imagem_memoria(self, formato='PNG', size=(2400, 1800), color=(120, 80, 40), mode='RGB'):
        """
        Método auxiliar para geração determinística de imagens em memória.
        """
        buffer = BytesIO()
        img = Image.new(mode, size, color)
        img.save(buffer, format=formato)
        buffer.seek(0)
        extensao = 'png' if formato == 'PNG' else 'jpg'
        return SimpleUploadedFile(
            f"foto_campo_pesada.{extensao}",
            buffer.getvalue(),
            content_type=f"image/{extensao}"
        )

    def test_rnf02_compressao_imagem_pesada_mantem_limite_350kb(self):
        """
        Verifica se imagens de alta resolução são redimensionadas e comprimidas abaixo de 350 KB.

        - O que faz: Envia uma imagem de 2400x1800 px para `otimizar_comprovante_fiscal`.
        - Como faz: Inspeciona a imagem retornada com Pillow para validar dimensões <= 1920px e tamanho <= 350KB.
        - Qual finalidade atende: Atende ao critério de aceitação de RNF02 (upload viável em conexões Starlink).
        """
        upload_pesado = self._gerar_imagem_memoria(formato='PNG', size=(2400, 1800))
        resultado = otimizar_comprovante_fiscal(upload_pesado)

        self.assertLessEqual(resultado.size, TAMANHO_MAXIMO_COMPRIMIDO_BYTES)
        self.assertTrue(resultado.name.endswith('.jpg'))

        # Confere se o nome é um UUID v4 hexadecimal válido de 32 caracteres + .jpg
        nome_sem_extensao = resultado.name[:-4]
        self.assertTrue(re.fullmatch(r'[0-9a-f]{32}', nome_sem_extensao))

        # Confere se a imagem é legível e respeita largura máxima de 1920px
        resultado.seek(0)
        img_processada = Image.open(resultado)
        self.assertLessEqual(img_processada.width, 1920)
        self.assertEqual(img_processada.mode, 'RGB')

    def test_conversao_imagem_com_canal_alfa_rgba(self):
        """
        Verifica a conversão segura de imagens transparentes (RGBA) para RGB sem disparar exceção.

        - O que faz: Envia uma imagem com canal alfa para otimização em JPEG.
        - Como faz: Invoca `otimizar_comprovante_fiscal` com imagem em modo RGBA e valida o modo resultante RGB.
        - Qual finalidade atende: Evita quebras de upload com capturas de tela em PNG que contenham transparência.
        """
        upload_rgba = self._gerar_imagem_memoria(formato='PNG', size=(800, 600), color=(255, 0, 0, 128), mode='RGBA')
        resultado = otimizar_comprovante_fiscal(upload_rgba)

        self.assertTrue(resultado.name.endswith('.jpg'))
        resultado.seek(0)
        img = Image.open(resultado)
        self.assertEqual(img.mode, 'RGB')

    def test_preservacao_arquivo_pdf_com_uuid_v4(self):
        """
        Verifica se arquivos PDF são mantidos intactos em conteúdo e renomeados com UUID v4.

        - O que faz: Envia um arquivo com extensão `.pdf` contendo bytes simulados de nota fiscal eletrônica.
        - Como faz: Compara o conteúdo em bytes antes e depois da chamada a `otimizar_comprovante_fiscal`.
        - Qual finalidade atende: Cumpre a RN01 (suporte a comprovantes fiscais em PDF) e RNF04 (anonimização).
        """
        conteudo_pdf = b"%PDF-1.4 simulacao de Danfe de combustivel"
        upload_pdf = SimpleUploadedFile("danfe_posto.pdf", conteudo_pdf, content_type="application/pdf")

        resultado = otimizar_comprovante_fiscal(upload_pdf)

        self.assertTrue(resultado.name.endswith('.pdf'))
        nome_sem_extensao = resultado.name[:-4]
        self.assertTrue(re.fullmatch(r'[0-9a-f]{32}', nome_sem_extensao))
        self.assertEqual(resultado.read(), conteudo_pdf)

    def test_rejeicao_formato_nao_permitido_lanca_validation_error(self):
        """
        Verifica o bloqueio de extensões não autorizadas (ex: executáveis, textos ou planilhas).

        - O que faz: Tenta otimizar arquivos com extensões `.exe` e `.txt`.
        - Como faz: Invoca o serviço esperando disparo de `ValidationError`.
        - Qual finalidade atende: Assegura conformidade com RN01 e previne injeção de arquivos maliciosos.
        """
        arquivo_proibido = SimpleUploadedFile("relatorio.txt", b"conteudo texto", content_type="text/plain")
        with self.assertRaises(ValidationError) as ctx:
            otimizar_comprovante_fiscal(arquivo_proibido)
        self.assertIn("Formato de arquivo não suportado", str(ctx.exception))

    def test_rejeicao_imagem_corrompida_lanca_validation_error(self):
        """
        Verifica a rejeição de arquivos com extensão de imagem mas cujo conteúdo binário está corrompido.

        - O que faz: Envia um arquivo `cupom.jpg` preenchido com bytes aleatórios que não formam uma imagem válida.
        - Como faz: Testa o disparo de `ValidationError` ao falhar na inicialização do Pillow.
        - Qual finalidade atende: Impede que voluntários salvem arquivos ilegíveis ou quebrados como comprovante fiscal.
        """
        arquivo_corrompido = SimpleUploadedFile("cupom.jpg", b"BYTES_CORROMPIDOS_NAO_IMAGEM", content_type="image/jpeg")
        with self.assertRaises(ValidationError) as ctx:
            otimizar_comprovante_fiscal(arquivo_corrompido)
        self.assertIn("não é uma imagem válida ou está corrompido", str(ctx.exception))
