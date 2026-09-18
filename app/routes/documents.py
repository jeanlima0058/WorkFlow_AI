from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
    HTTPException
)

from app.firebase_config import db

from app.schemas.document import DocumentResponse

from app.services.document_service import (
    salvar_documento
)

from app.utils.security import get_current_user


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
    usuario_id: str = Depends(get_current_user)
):
    try:
        documento = salvar_documento(
            arquivo=arquivo,
            usuario_id=usuario_id
        )

        return documento

    except Exception as erro:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao salvar documento: {str(erro)}"
        )


@router.get(
    "/",
    response_model=list[DocumentResponse]
)
def listar_documentos(
    usuario_id: str = Depends(get_current_user)
):
    documentos_ref = (
        db.collection("documents")
        .where("usuario_id", "==", str(usuario_id))
        .stream()
    )

    documentos = [
        documento.to_dict()
        for documento in documentos_ref
    ]

    documentos.sort(
        key=lambda documento: documento.get(
            "data_upload"
        ) or "",
        reverse=True
    )

    return documentos


@router.get(
    "/{document_id}",
    response_model=DocumentResponse
)
def obter_documento(
    document_id: str,
    usuario_id: str = Depends(get_current_user)
):
    documento_ref = db.collection(
        "documents"
    ).document(document_id)

    documento_snapshot = documento_ref.get()

    if not documento_snapshot.exists:
        raise HTTPException(
            status_code=404,
            detail="Documento não encontrado"
        )

    documento = documento_snapshot.to_dict()

    if documento.get("usuario_id") != str(usuario_id):
        raise HTTPException(
            status_code=404,
            detail="Documento não encontrado"
        )

    return documento


@router.delete("/{document_id}")
def excluir_documento(
    document_id: str,
    usuario_id: str = Depends(get_current_user)
):
    documento_ref = db.collection(
        "documents"
    ).document(document_id)

    documento_snapshot = documento_ref.get()

    if not documento_snapshot.exists:
        raise HTTPException(
            status_code=404,
            detail="Documento não encontrado"
        )

    documento = documento_snapshot.to_dict()

    if documento.get("usuario_id") != str(usuario_id):
        raise HTTPException(
            status_code=404,
            detail="Documento não encontrado"
        )

    try:
        caminho = documento.get("caminho_arquivo")

        if caminho:
            import os

            if os.path.exists(caminho):
                os.remove(caminho)

        # Exclui os resultados OCR relacionados
        ocr_documentos = (
            db.collection("ocr_results")
            .where(
                "documento_id",
                "==",
                document_id
            )
            .stream()
        )

        for ocr_documento in ocr_documentos:
            ocr_documento.reference.delete()

        # Exclui o documento
        documento_ref.delete()

        return {
            "message": "Documento excluído com sucesso"
        }

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Erro ao excluir documento"
        )