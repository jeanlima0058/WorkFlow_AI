from fastapi import APIRouter, Depends, HTTPException
from app.firebase_config import db
from app.schemas.ai_result import AIResultResponse
from app.services.ai_service import analisar_documento
from app.utils.security import get_current_user
from datetime import datetime, timezone

router = APIRouter(prefix="/ai", tags=["Inteligência Artificial"])

def registrar_log_ai(usuario_id: str, documento_id: str, acao: str, descricao: str):
    """Registra log de ações de IA."""
    log_ref = db.collection("logs").document()
    log_ref.set({
        "id": log_ref.id,
        "usuario_id": str(usuario_id),
        "usuario_email": "", # Pode ser preenchido se necessário
        "acao": acao,
        "descricao": descricao,
        "documento_id": documento_id,
        "data": datetime.now(timezone.utc)
    })

@router.post("/analyze/{document_id}", response_model=AIResultResponse)
def analisar_documento_ai(document_id: str, usuario_id: str = Depends(get_current_user)):
    documento_ref = db.collection("documents").document(document_id)
    documento_snapshot = documento_ref.get()
    if not documento_snapshot.exists:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    documento = documento_snapshot.to_dict()
    if str(documento.get("usuario_id")) != str(usuario_id):
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    
    try:
        resultado = analisar_documento(document_id=document_id)
        if not resultado["sucesso"]:
            raise HTTPException(status_code=400, detail=resultado["mensagem"])
        
        # Registrar log de análise
        registrar_log_ai(
            usuario_id=usuario_id,
            documento_id=document_id,
            acao="AI_ANALYSIS",
            descricao=f"Análise de IA concluída para documento {documento.get('nome_arquivo')}"
        )
        
        return resultado["resultado"]
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Erro ao analisar documento: {str(error)}")

@router.get("/result/{document_id}", response_model=AIResultResponse)
def obter_resultado_ai(document_id: str, usuario_id: str = Depends(get_current_user)):
    documento_ref = db.collection("documents").document(document_id)
    documento_snapshot = documento_ref.get()
    if not documento_snapshot.exists:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    documento = documento_snapshot.to_dict()
    if str(documento.get("usuario_id")) != str(usuario_id):
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    
    resultados = db.collection("ai_results").where("documento_id", "==", document_id).limit(1).stream()
    resultado_snapshot = next(resultados, None)
    if resultado_snapshot is None:
        raise HTTPException(status_code=404, detail="Ainda não existe uma análise de IA para este documento")
    
    resultado_ai = resultado_snapshot.to_dict()
    resultado_ai["id"] = resultado_snapshot.id
    return resultado_ai