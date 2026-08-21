import os

from app.ocr.ocr_service import (
    extrair_texto_pdf,
    extrair_texto_imagem
)

from app.services.text_extractor import (
    extrair_texto_txt
)


def processar_documento(caminho_arquivo: str) -> dict:

    extensao = os.path.splitext(
        caminho_arquivo
    )[1].lower()

    try:

        # PROCESSAMENTO DE PDF
        if extensao == ".pdf":

            texto = extrair_texto_pdf(
                caminho_arquivo
            )

            if texto:
                return {
                    "sucesso": True,
                    "texto": texto,
                    "status": "PROCESSADO",
                    "mensagem": "PDF processado com sucesso"
                }

            return {
                "sucesso": False,
                "texto": "",
                "status": "SEM_TEXTO_EXTRAIDO",
                "mensagem": "Nenhum texto foi extraído do PDF"
            }

        # PROCESSAMENTO DE IMAGENS
        elif extensao in [
            ".png",
            ".jpg",
            ".jpeg"
        ]:

            texto = extrair_texto_imagem(
                caminho_arquivo
            )

            if texto:
                return {
                    "sucesso": True,
                    "texto": texto,
                    "status": "PROCESSADO",
                    "mensagem": "Imagem processada com sucesso"
                }

            return {
                "sucesso": False,
                "texto": "",
                "status": "SEM_TEXTO_EXTRAIDO",
                "mensagem": "Nenhum texto foi encontrado na imagem"
            }

        # PROCESSAMENTO DE TXT
        elif extensao == ".txt":

            texto = extrair_texto_txt(
                caminho_arquivo
            )

            if texto:
                return {
                    "sucesso": True,
                    "texto": texto,
                    "status": "PROCESSADO",
                    "mensagem": "Arquivo TXT processado com sucesso"
                }

            return {
                "sucesso": False,
                "texto": "",
                "status": "SEM_TEXTO_EXTRAIDO",
                "mensagem": "O arquivo TXT está vazio"
            }

        # FORMATO NÃO SUPORTADO
        else:

            return {
                "sucesso": False,
                "texto": "",
                "status": "FORMATO_NAO_SUPORTADO",
                "mensagem": f"O formato {extensao} ainda não é suportado"
            }

    except Exception as error:

        return {
            "sucesso": False,
            "texto": "",
            "status": "ERRO_PROCESSAMENTO",
            "mensagem": f"Erro ao processar o arquivo: {str(error)}"
        }