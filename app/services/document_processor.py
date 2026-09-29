import os

from app.services.text_extractor import extrair_texto_txt
from app.services.spreadsheet_extractor import extrair_planilha
from app.services.yaml_extractor import extrair_yaml


def processar_documento(caminho_arquivo: str) -> dict:

    extensao = os.path.splitext(
        caminho_arquivo
    )[1].lower()

    try:

        if extensao in [
            ".pdf", ".png", ".jpg", ".jpeg", ".bmp",
            ".tif", ".tiff", ".gif", ".webp"
        ]:
            return {
                "sucesso": False,
                "texto": "",
                "status": "OCR_REQUER_ROTA",
                "tipo": "DOCUMENTO_OCR",
                "mensagem": (
                    "Arquivos PDF e imagem devem ser processados pela "
                    "rota /ocr/process/{document_id}."
                )
            }

        elif extensao == ".txt":

            texto = extrair_texto_txt(
                caminho_arquivo
            )

            tipo = "TEXTO"

        elif extensao == ".csv":

            texto = extrair_planilha(
                caminho_arquivo
            )

            tipo = "CSV"

        elif extensao in [
            ".xls",
            ".xlsx",
            ".xlsm"
        ]:

            texto = extrair_planilha(
                caminho_arquivo
            )

            tipo = "PLANILHA"

        elif extensao in [
            ".yaml",
            ".yml"
        ]:

            texto = extrair_yaml(
                caminho_arquivo
            )

            tipo = "YAML"

        else:

            return {
                "sucesso": False,
                "texto": "",
                "status": "FORMATO_NAO_SUPORTADO",
                "tipo": "DESCONHECIDO",
                "mensagem": (
                    f"Formato {extensao} "
                    "não suportado"
                )
            }

        if not texto or not texto.strip():

            return {
                "sucesso": False,
                "texto": "",
                "status": "SEM_TEXTO_EXTRAIDO",
                "tipo": tipo,
                "mensagem": (
                    "O arquivo foi processado, "
                    "mas nenhum conteúdo foi extraído"
                )
            }

        return {
            "sucesso": True,
            "texto": texto,
            "status": "CONCLUIDO",
            "tipo": tipo,
            "mensagem": (
                "Documento processado "
                "com sucesso"
            )
        }

    except Exception as error:

        return {
            "sucesso": False,
            "texto": "",
            "status": "ERRO_PROCESSAMENTO",
            "tipo": "DESCONHECIDO",
            "mensagem": str(error)
        }