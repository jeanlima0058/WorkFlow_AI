from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.document import Document
from app.models.ocr_result import OCRResult
from app.ocr.ocr_service import extrair_texto_pdf, extrair_texto_imagem
from app.utils.security import get_current_user

import os


router = APIRouter(
    prefix="/ocr",
    tags=["OCR"]
)


@router.post("/process/{document_id}")
def processar_ocr(
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

        extensao = os.path.splitext(
            documento.nome_arquivo
        )[1].lower()

        if extensao == ".pdf":

            texto = extrair_texto_pdf(
                documento.caminho_arquivo
            )

        elif extensao in [".png", ".jpg", ".jpeg"]:

            texto = extrair_texto_imagem(
                documento.caminho_arquivo
            )

        else:

            raise HTTPException(
                status_code=400,
                detail="Tipo de arquivo não suportado pelo OCR"
            )

        resultado = (
            db.query(OCRResult)
            .filter(
                OCRResult.documento_id == documento.id
            )
            .first()
        )

        if resultado:

            resultado.texto_extraido = texto
            resultado.status = "CONCLUIDO"

        else:

            resultado = OCRResult(
                documento_id=documento.id,
                texto_extraido=texto,
                status="CONCLUIDO"
            )

            db.add(resultado)

        documento.status = "OCR_CONCLUIDO"

        db.commit()
        db.refresh(resultado)

        return {
            "message": "OCR processado com sucesso",
            "documento_id": documento.id,
            "status": resultado.status,
            "texto_extraido": resultado.texto_extraido
        }

    except HTTPException:
        raise

    except Exception as error:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar OCR: {str(error)}"
        )