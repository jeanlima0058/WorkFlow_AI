from fastapi import APIRouter, Depends, File, UploadFile
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session


from app.database import get_db
from app.schemas.document import DocumentResponse
from app.services.document_service import salvar_documento
from app.utils.security import get_current_user
from app.models.document import Document


router = APIRouter(
    prefix="/documents",
    tags=["Documentos"]
)


@router.post(
    "/upload",
    response_model=DocumentResponse
)
def upload_documento(
    arquivo: UploadFile = File(...),
    usuario_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    documento = salvar_documento(
        db=db,
        arquivo=arquivo,
        usuario_id=usuario_id
    )

    return documento


@router.get(
    "/",
    response_model=list[DocumentResponse]
)
def listar_documentos(
    usuario_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    documentos = (
        db.query(Document)
        .filter(Document.usuario_id == usuario_id)
        .order_by(Document.data_upload.desc())
        .all()
    )

    return documentos

@router.get(
    "/{document_id}",
    response_model=DocumentResponse
)
def obter_documento(
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

    return documento

@router.delete("/{document_id}")
def excluir_documento(
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

    try:
        import os

        if os.path.exists(documento.caminho_arquivo):
            os.remove(documento.caminho_arquivo)

        db.delete(documento)
        db.commit()

        return {
            "message": "Documento excluído com sucesso"
        }

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Erro ao excluir documento"
        )