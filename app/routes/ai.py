from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.document import Document
from app.models.ai_result import AIResult
from app.schemas.ai_result import AIResultResponse
from app.services.ai_service import analisar_documento
from app.utils.security import get_current_user


router = APIRouter(
    prefix="/ai",
    tags=["Inteligência Artificial"]
)


@router.post(
    "/analyze/{document_id}",
    response_model=AIResultResponse
)
def analisar_documento_ai(
    document_id: int,
    usuario_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verifica se o documento existe e pertence ao usuário
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
        resultado = analisar_documento(
            db=db,
            document_id=document_id
        )

        if not resultado["sucesso"]:
            raise HTTPException(
                status_code=400,
                detail=resultado["mensagem"]
            )

        return resultado["resultado"]

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao analisar documento: {str(error)}"
        )


@router.get(
    "/result/{document_id}",
    response_model=AIResultResponse
)
def obter_resultado_ai(
    document_id: int,
    usuario_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verifica se o documento pertence ao usuário
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

    # Busca o resultado da IA
    resultado_ai = (
        db.query(AIResult)
        .filter(
            AIResult.documento_id == document_id
        )
        .first()
    )

    if not resultado_ai:
        raise HTTPException(
            status_code=404,
            detail="Ainda não existe uma análise de IA para este documento"
        )

    return resultado_ai