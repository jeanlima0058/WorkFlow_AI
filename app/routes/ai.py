from fastapi import APIRouter, Depends, HTTPException

from app.firebase_config import db
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
    document_id: str,
    usuario_id: str = Depends(get_current_user)
):
    # Busca o documento no Firestore
    documento_ref = db.collection("documents").document(document_id)
    documento_snapshot = documento_ref.get()

    if not documento_snapshot.exists:
        raise HTTPException(
            status_code=404,
            detail="Documento não encontrado"
        )

    documento = documento_snapshot.to_dict()

    # Verifica se o documento pertence ao usuário
    if str(documento.get("usuario_id")) != str(usuario_id):
        raise HTTPException(
            status_code=404,
            detail="Documento não encontrado"
        )

    try:
        resultado = analisar_documento(
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
    document_id: str,
    usuario_id: str = Depends(get_current_user)
):
    # Busca o documento no Firestore
    documento_ref = db.collection("documents").document(document_id)
    documento_snapshot = documento_ref.get()

    if not documento_snapshot.exists:
        raise HTTPException(
            status_code=404,
            detail="Documento não encontrado"
        )

    documento = documento_snapshot.to_dict()

    # Verifica se o documento pertence ao usuário
    if str(documento.get("usuario_id")) != str(usuario_id):
        raise HTTPException(
            status_code=404,
            detail="Documento não encontrado"
        )

    # Busca o resultado da IA no Firestore
    resultados = (
        db.collection("ai_results")
        .where("documento_id", "==", document_id)
        .limit(1)
        .stream()
    )

    resultado_snapshot = next(resultados, None)

    if resultado_snapshot is None:
        raise HTTPException(
            status_code=404,
            detail="Ainda não existe uma análise de IA para este documento"
        )

    resultado_ai = resultado_snapshot.to_dict()

    # Garante que o ID do resultado esteja disponível
    resultado_ai["id"] = resultado_snapshot.id

    return resultado_ai