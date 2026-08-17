import os
import uuid
from datetime import datetime

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.ocr_result import OCRResult
from app.ocr.ocr_service import (
    extrair_texto_imagem,
    extrair_texto_pdf
)


UPLOAD_DIR = "uploads"


def salvar_documento(
    db: Session,
    arquivo: UploadFile,
    usuario_id: int
):
    # Garante que a pasta uploads exista
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # Recupera a extensão do arquivo original
    extensao = os.path.splitext(
        arquivo.filename
    )[1].lower()

    # Gera um nome único
    nome_unico = f"{uuid.uuid4()}{extensao}"

    # Define o caminho
    caminho = os.path.join(
        UPLOAD_DIR,
        nome_unico
    )

    # Salva o arquivo
    with open(caminho, "wb") as buffer:
        buffer.write(arquivo.file.read())

    # Obtém o tamanho
    tamanho = os.path.getsize(caminho)

    # Cria o documento
    documento = Document(
        usuario_id=usuario_id,
        nome_arquivo=arquivo.filename,
        tipo_arquivo=arquivo.content_type or "application/octet-stream",
        tamanho=tamanho,
        caminho_arquivo=caminho,
        status="RECEBIDO"
    )

    db.add(documento)
    db.commit()
    db.refresh(documento)

    # Cria o registro do OCR
    ocr_resultado = OCRResult(
        documento_id=documento.id,
        status="PROCESSANDO"
    )

    db.add(ocr_resultado)
    db.commit()

    try:
        # PDF
        if extensao == ".pdf":
            texto = extrair_texto_pdf(caminho)

        # Imagens
        elif extensao in [".png", ".jpg", ".jpeg", ".bmp", ".tiff"]:
            texto = extrair_texto_imagem(caminho)

        # Formato não suportado pelo OCR
        else:
            ocr_resultado.status = "NAO_SUPORTADO"
            ocr_resultado.texto_extraido = None

            documento.status = "RECEBIDO"

            db.commit()

            return documento

        # Salva o texto extraído
        ocr_resultado.texto_extraido = texto
        ocr_resultado.status = "CONCLUIDO"
        ocr_resultado.data_processamento = datetime.now()

        documento.status = "OCR_CONCLUIDO"

        db.commit()

    except Exception as erro:
        db.rollback()

        # Busca novamente os registros
        documento = (
            db.query(Document)
            .filter(Document.id == documento.id)
            .first()
        )

        ocr_resultado = (
            db.query(OCRResult)
            .filter(OCRResult.documento_id == documento.id)
            .first()
        )

        if ocr_resultado:
            ocr_resultado.status = "ERRO"
            ocr_resultado.data_processamento = datetime.now()

        if documento:
            documento.status = "OCR_ERRO"

        db.commit()

    return documento