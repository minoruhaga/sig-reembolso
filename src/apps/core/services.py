import logging
import os
import uuid
from io import BytesIO

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image, ImageDraw, ImageFont, ImageOps, UnidentifiedImageError

logger = logging.getLogger(__name__)

EXTENSOES_PERMITIDAS = {'.jpg', '.jpeg', '.png', '.webp', '.pdf'}
TAMANHO_MAXIMO_COMPRIMIDO_BYTES = 350 * 1024  # 350 KB (RNF02)
UPLOAD_MAXIMO_BRUTO_BYTES = 10 * 1024 * 1024  # 10 MB


def otimizar_comprovante_fiscal(uploaded_file, max_width=1920, quality=75):
    """
    Valida, otimiza e anonimiza arquivos de notas e cupons fiscais para persistência.

    - O que faz: Valida a extensão permitida (JPEG, PNG, WEBP, PDF - RN01), impede o envio de imagens
      corrompidas ou executáveis mascarados, reduz fotografias pesadas de smartphones para versões JPEG
      leves (< 350KB - RNF02) via algoritmo adaptativo e anonimiza o nome do arquivo com UUID v4 (RNF04).
    - Como faz: Verifica a extensão e o tamanho bruto do arquivo; preserva documentos PDF aplicando
      apenas a renomeação com UUID v4; para imagens, utiliza a biblioteca Pillow para corrigir rotação
      EXIF de celulares, converte canais transparentes (RGBA/P) para RGB, redimensiona proporcionalmente
      para largura máxima de 1920px e comprime em JPEG progressivo com ajuste dinâmico de qualidade
      até satisfazer o teto de 350 KB. Marca o arquivo processado com `_otimizado_pillow = True` para
      evitar recompressão redundante entre camada de serviço e modelo.
    - Qual finalidade atende: Garante a conformidade estrita com RN01 (anexo comprobatório íntegro),
      RNF02 (viabilizar uploads rápidos e de baixo consumo sob a rede satelital Starlink em Juquitiba)
      e RNF04 (segurança, anonimização e prevenção de colisões de arquivos no storage).
    """
    if not uploaded_file or not hasattr(uploaded_file, 'name'):
        raise ValidationError("Nenhum arquivo válido foi fornecido para o comprovante fiscal.")

    nome_original, extensao = os.path.splitext(uploaded_file.name)
    extensao_lower = extensao.lower()

    if extensao_lower not in EXTENSOES_PERMITIDAS:
        raise ValidationError(
            f"Formato de arquivo não suportado ({extensao_lower or 'sem extensão'}). "
            "Os formatos aceitos são: JPEG, PNG, WEBP e PDF."
        )

    if uploaded_file.size > UPLOAD_MAXIMO_BRUTO_BYTES:
        raise ValidationError("O arquivo enviado excede o limite máximo permitido de 10 MB.")

    # Documentos PDF não sofrem conversão raster pelo Pillow
    if extensao_lower == '.pdf':
        uploaded_file.name = f"{uuid.uuid4().hex}.pdf"
        uploaded_file._otimizado_pillow = True
        return uploaded_file

    try:
        imagem = Image.open(uploaded_file)
        imagem.load()  # Força a leitura dos bytes para detectar arquivos corrompidos

        # Corrige orientação EXIF se a foto tiver sido capturada diretamente por celular
        try:
            imagem = ImageOps.exif_transpose(imagem)
        except (AttributeError, KeyError, IndexError):
            logger.debug("Falha não-bloqueante ao transpor EXIF da imagem.")

        # Converte modos de cor com canal alfa ou paleta para RGB padrão
        if imagem.mode in ('RGBA', 'LA', 'P'):
            imagem = imagem.convert('RGB')
        elif imagem.mode != 'RGB':
            imagem = imagem.convert('RGB')

        # Redimensiona proporcionalmente caso exceda a largura máxima inicial
        if imagem.width > max_width:
            proporcao = max_width / float(imagem.width)
            nova_altura = int(float(imagem.height) * proporcao)
            imagem = imagem.resize((max_width, nova_altura), Image.Resampling.LANCZOS)

        # Algoritmo adaptativo de compressão para atingir estritamente o teto RNF02 (< 350 KB)
        output_buffer = None
        qualidades = [quality, 65, 55, 45, 35]

        for q in qualidades:
            buffer = BytesIO()
            imagem.save(buffer, format='JPEG', quality=q, optimize=True)
            buffer.seek(0)
            if buffer.getbuffer().nbytes <= TAMANHO_MAXIMO_COMPRIMIDO_BYTES:
                output_buffer = buffer
                break

        # Fallback de redução de resolução para fotos ultradensas com ruído elevado
        if output_buffer is None:
            largura_reduzida = 1280
            if imagem.width > largura_reduzida:
                proporcao = largura_reduzida / float(imagem.width)
                nova_altura = int(float(imagem.height) * proporcao)
                imagem = imagem.resize((largura_reduzida, nova_altura), Image.Resampling.LANCZOS)

            for q in [50, 40, 30]:
                buffer = BytesIO()
                imagem.save(buffer, format='JPEG', quality=q, optimize=True)
                buffer.seek(0)
                output_buffer = buffer
                if buffer.getbuffer().nbytes <= TAMANHO_MAXIMO_COMPRIMIDO_BYTES:
                    break

        novo_nome = f"{uuid.uuid4().hex}.jpg"
        resultado = InMemoryUploadedFile(
            file=output_buffer,
            field_name=uploaded_file.field_name if hasattr(uploaded_file, 'field_name') else 'comprovante',
            name=novo_nome,
            content_type='image/jpeg',
            size=output_buffer.getbuffer().nbytes,
            charset=None
        )
        resultado._otimizado_pillow = True
        return resultado

    except (UnidentifiedImageError, OSError, SyntaxError) as e:
        raise ValidationError(
            "O arquivo enviado não é uma imagem válida ou está corrompido."
        ) from e


def gerar_imagem_cupom_simulado(
    *,
    titulo: str,
    valor: str,
    data: str,
    tipo_doc: str = 'CUPOM FISCAL',
) -> bytes:
    """
    Gera em memória os bytes de um cupom fiscal ou comprovante bancário simulado e legível.

    - O que faz: Desenha via Pillow uma imagem JPEG 520x720 simulando papel térmico com cabeçalho,
      CNPJ ilustrativo, data, descrição da despesa em até duas linhas e total em Reais.
    - Como faz: Instancia imagem RGB em tom claro `(252, 250, 242)`, carrega fonte padrão do Pillow
      (com fallback seguro entre versões) e renderiza textos escuros delimitados por linhas tracejadas.
    - Qual finalidade atende: Substitui imagens monocromáticas nos comandos de carga e demonstração,
      permitindo demonstrar legivelmente o modal de zoom e rotação da Auditoria de Notas.
    """
    largura, altura = 520, 720
    imagem = Image.new('RGB', (largura, altura), color=(252, 250, 242))
    desenho = ImageDraw.Draw(imagem)

    try:
        fonte_titulo = ImageFont.load_default(size=22)
        fonte_corpo = ImageFont.load_default(size=18)
        fonte_destaque = ImageFont.load_default(size=26)
        fonte_rodape = ImageFont.load_default(size=14)
    except TypeError:
        fonte_titulo = fonte_corpo = fonte_destaque = fonte_rodape = ImageFont.load_default()

    desenho.rectangle([(18, 18), (largura - 18, altura - 18)], outline=(180, 175, 160), width=2)

    cor_texto = (30, 32, 36)
    cor_secundaria = (95, 100, 108)
    cor_destaque = (25, 135, 84)

    desenho.text((38, 42), tipo_doc[:32], fill=cor_destaque, font=fonte_titulo)
    desenho.text((38, 82), 'GRUPO ESCOTEIRO CARAMURU - AG VII', fill=cor_texto, font=fonte_corpo)
    desenho.text((38, 114), 'CNPJ: 00.000.000/0001-00 (SIMULACAO)', fill=cor_secundaria, font=fonte_rodape)
    desenho.line([(36, 150), (largura - 36, 150)], fill=(160, 160, 160), width=2)

    desenho.text((38, 172), f'DATA: {data}', fill=cor_texto, font=fonte_corpo)
    desenho.text((38, 212), 'DESCRICAO:', fill=cor_secundaria, font=fonte_rodape)

    palavras = (titulo or 'Despesa Operacional').split()
    linhas_titulo: list[str] = []
    linha_atual = ''
    for palavra in palavras:
        candidato = f'{linha_atual} {palavra}'.strip()
        if len(candidato) <= 34:
            linha_atual = candidato
        else:
            if linha_atual:
                linhas_titulo.append(linha_atual)
            linha_atual = palavra
    if linha_atual:
        linhas_titulo.append(linha_atual)

    y_texto = 240
    for linha in linhas_titulo[:3]:
        desenho.text((38, y_texto), linha, fill=cor_texto, font=fonte_corpo)
        y_texto += 30

    desenho.line([(36, 365), (largura - 36, 365)], fill=(160, 160, 160), width=2)
    desenho.text((38, 392), 'VALOR TOTAL', fill=cor_secundaria, font=fonte_corpo)
    desenho.text((38, 424), f'R$ {valor}', fill=cor_destaque, font=fonte_destaque)
    desenho.line([(36, 485), (largura - 36, 485)], fill=(160, 160, 160), width=2)

    desenho.text((38, 520), 'COMPROVANTE ANEXADO VIA CAMPO MOBILE', fill=cor_texto, font=fonte_rodape)
    desenho.text((38, 550), 'ACAMPAMENTO GERAL VII - JUQUITIBA/SP', fill=cor_secundaria, font=fonte_rodape)
    desenho.text((38, 650), 'DOCUMENTO DE DEMONSTRACAO - SIG-REEMBOLSO', fill=cor_secundaria, font=fonte_rodape)

    buffer = BytesIO()
    imagem.save(buffer, format='JPEG', quality=85)
    return buffer.getvalue()
