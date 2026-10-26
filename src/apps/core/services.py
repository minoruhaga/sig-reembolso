import os
import uuid
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile


def otimizar_comprovante_fiscal(uploaded_file, max_width=1920, quality=75):
    """
    RNF02: Comprime e otimiza imagens de notas fiscais/cupons antes do salvamento.
    Reduz fotos pesadas de celulares (5MB) para versões legíveis (< 350KB),
    viabilizando tráfego leve no link satelital Starlink.
    Preserva arquivos PDF sem alteração.
    """
    nome_original, extensao = os.path.splitext(uploaded_file.name)
    extensao_lower = extensao.lower()

    # PDFs não sofrem compressão por Pillow
    if extensao_lower == '.pdf':
        novo_nome = f"{uuid.uuid4().hex}.pdf"
        uploaded_file.name = novo_nome
        return uploaded_file

    try:
        imagem = Image.open(uploaded_file)

        # Trata orientação EXIF se a foto tiver sido tirada no celular
        try:
            from PIL import ImageOps
            imagem = ImageOps.exif_transpose(imagem)
        except Exception:
            pass

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
    except Exception:
        # Em caso de falha na manipulação, retorna com nome UUID
        uploaded_file.name = f"{uuid.uuid4().hex}{extensao_lower}"
        return uploaded_file
