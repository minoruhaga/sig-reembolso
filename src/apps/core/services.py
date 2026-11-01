import logging
import os
import uuid
from io import BytesIO

from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image, ImageOps

logger = logging.getLogger(__name__)


def otimizar_comprovante_fiscal(uploaded_file, max_width=1920, quality=75):
    """
    Otimiza e anonimiza arquivos de notas e cupons fiscais para persistência.

    - O que faz: Reduz fotografias pesadas de smartphones para versões JPEG leves (< 350KB),
      renomeando os arquivos com UUID v4 para evitar colisões ou enumeração direta.
    - Como faz: Utiliza a biblioteca Pillow para corrigir orientação EXIF de celulares, redimensionar
      proporcionalmente caso exceda a largura máxima de 1920px e comprimir em JPEG otimizado. Arquivos
      PDF são preservados integralmente sem conversão.
    - Qual finalidade atende: Cumpre o requisito RNF02 (viabilizar uploads rápidos e estáveis sob a rede
      satelital Starlink em Juquitiba) e RNF04 (segurança e anonimização de anexos).
    """
    nome_original, extensao = os.path.splitext(uploaded_file.name)
    extensao_lower = extensao.lower()

    # PDFs não sofrem compressão por Pillow, apenas renomeação por UUID
    if extensao_lower == '.pdf':
        novo_nome = f"{uuid.uuid4().hex}.pdf"
        uploaded_file.name = novo_nome
        return uploaded_file

    try:
        imagem = Image.open(uploaded_file)

        # Trata orientação EXIF se a foto tiver sido tirada no celular
        try:
            imagem = ImageOps.exif_transpose(imagem)
        except (AttributeError, KeyError, IndexError):
            logger.debug("Falha não-bloqueante ao transpor EXIF da imagem.")

        # Converte para RGB se necessário
        if imagem.mode in ('RGBA', 'P'):
            imagem = imagem.convert('RGB')

        # Redimensiona se largura exceder max_width
        if imagem.width > max_width:
            proporcao = max_width / float(imagem.width)
            nova_altura = int(float(imagem.height) * proporcao)
            imagem = imagem.resize((max_width, nova_altura), Image.Resampling.LANCZOS)

        output = BytesIO()
        imagem.save(output, format='JPEG', quality=quality, optimize=True)
        output.seek(0)

        novo_nome = f"{uuid.uuid4().hex}.jpg"
        return InMemoryUploadedFile(
            file=output,
            field_name=uploaded_file.field_name if hasattr(uploaded_file, 'field_name') else 'comprovante',
            name=novo_nome,
            content_type='image/jpeg',
            size=output.getbuffer().nbytes,
            charset=None
        )
    except Exception as exc:
        logger.warning("Falha ao otimizar imagem com Pillow, mantendo original com UUID: %s", exc)
        uploaded_file.name = f"{uuid.uuid4().hex}{extensao_lower}"
        return uploaded_file
