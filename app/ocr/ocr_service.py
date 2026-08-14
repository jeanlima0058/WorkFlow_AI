import pytesseract
from PIL import Image


TESSERACT_PATH = (
    r"C:\Users\usrlabecon\AppData\Local\Tesseract-OCR\tesseract.exe"
)

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


def extrair_texto_imagem(caminho_arquivo: str) -> str:
    imagem = Image.open(caminho_arquivo)

    texto = pytesseract.image_to_string(
        imagem,
        lang="por+eng"
    )

    return texto.strip()