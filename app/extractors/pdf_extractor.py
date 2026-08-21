import pymupdf
from PIL import Image
import pytesseract


def extrair_texto_pdf(caminho_arquivo: str) -> str:
    documento = pymupdf.open(caminho_arquivo)

    textos = []

    try:
        for pagina in documento:
            # Primeiro tenta extrair texto digital do PDF
            texto_digital = pagina.get_text().strip()

            if texto_digital:
                textos.append(texto_digital)
                continue

            # Se não houver texto digital, usa OCR
            pix = pagina.get_pixmap(dpi=200)

            imagem = Image.frombytes(
                "RGB",
                [pix.width, pix.height],
                pix.samples
            )

            texto_ocr = pytesseract.image_to_string(
                imagem,
                lang="por+eng"
            ).strip()

            if texto_ocr:
                textos.append(texto_ocr)

    finally:
        documento.close()

    return "\n\n".join(textos)