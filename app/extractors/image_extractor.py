from PIL import Image
import pytesseract


def extrair_texto_imagem(caminho_arquivo: str) -> str:
    imagem = Image.open(caminho_arquivo)

    try:
        texto = pytesseract.image_to_string(
            imagem,
            lang="por+eng"
        )

        return texto.strip()

    finally:
        imagem.close()