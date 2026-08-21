from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.document import Document
from app.models.ocr_result import OCRResult
from app.services.document_processor import processar_documento
from app.utils.security import get_current_user

import os
from datetime import datetime


router = APIRouter(
    prefix="/ocr",
    tags=["Processamento de Documentos"]
)


@router.post("/process/{document_id}")
def processar_documento_arquivo(
    document_id: int,
    usuario_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    documento = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.usuario_id == usuario_id
        )
        .first()
    )

    if not documento:
        raise HTTPException(
            status_code=404,
            detail="Documento não encontrado"
        )

    if not os.path.exists(documento.caminho_arquivo):
        raise HTTPException(
            status_code=404,
            detail="Arquivo do documento não encontrado"
        )

    try:

        documento.status = "PROCESSANDO"
        db.commit()

        processamento = processar_documento(
            documento.caminho_arquivo
        )

        resultado = (
            db.query(OCRResult)
            .filter(
                OCRResult.documento_id == documento.id
            )
            .first()
        )

        if processamento["sucesso"]:

            if resultado:

                resultado.texto_extraido = processamento["texto"]
                resultado.status = "CONCLUIDO"
                resultado.data_processamento = datetime.now()

            else:

                resultado = OCRResult(
                    documento_id=documento.id,
                    texto_extraido=processamento["texto"],
                    status="CONCLUIDO",
                    data_processamento=datetime.now()
                )

                db.add(resultado)

            documento.status = "PROCESSADO"

        else:

            if resultado:

                resultado.texto_extraido = None
                resultado.status = processamento["status"]
                resultado.data_processamento = datetime.now()

            else:

                resultado = OCRResult(
                    documento_id=documento.id,
                    texto_extraido=None,
                    status=processamento["status"],
                    data_processamento=datetime.now()
                )

                db.add(resultado)

            documento.status = processamento["status"]

        db.commit()
        db.refresh(resultado)

        return {
            "message": processamento["mensagem"],
            "documento_id": documento.id,
            "status": processamento["status"],
            "texto_extraido": processamento["texto"]
        }

    except Exception as error:

        db.rollback()

        documento.status = "ERRO"

        db.commit()

        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar documento: {str(error)}"
        )