import pytesseract
import pymupdf

from PIL import Image


TESSERACT_PATH = (
    r"C:\Users\usrlabeco2N\AppData\Local\Tesseract-OCR\tesseract.exe"
)

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


def extrair_texto_imagem(caminho_arquivo: str) -> str:
    imagem = Image.open(caminho_arquivo)

    texto = pytesseract.image_to_string(
        imagem,
        lang="por+eng"
    )

    return texto.strip()


def extrair_texto_pdf(caminho_arquivo: str) -> str:
    documento = pymupdf.open(caminho_arquivo)

    textos = []

    for pagina in documento:
        pix = pagina.get_pixmap(dpi=200)

        imagem = Image.frombytes(
            "RGB",
            [pix.width, pix.height],
            pix.samples
        )

        texto = pytesseract.image_to_string(
            imagem,
            lang="por+eng"
        )

        if texto.strip():
            textos.append(texto.strip())

    documento.close()

    return "\n\n".join(textos)