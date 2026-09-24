from fastapi import APIRouter, Depends, HTTPException
from app.firebase_config import db
from app.utils.security import get_current_user
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(
    prefix="/admin",
    tags=["Administração"]
)

def is_admin(user_id: str = Depends(get_current_user)):
    """Dependência para verificar se o usuário é ADMIN."""
    user_ref = db.collection("users").document(user_id)
    user_doc = user_ref.get()
    if not user_doc.exists:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    user_data = user_doc.to_dict()
    if user_data.get("tipo_usuario") != "ADMIN":
        raise HTTPException(status_code=403, detail="Acesso negado. Permissão de administrador necessária.")
    return user_id

@router.get("/stats")
def get_admin_stats(admin_id: str = Depends(is_admin)):
    """Retorna estatísticas para o dashboard administrativo."""
    users_ref = db.collection("users").stream()
    total_users = sum(1 for _ in users_ref)

    docs_ref = db.collection("documents").stream()
    all_docs = [doc.to_dict() for doc in docs_ref]
    total_docs = len(all_docs)
    
    analyzed_docs = sum(1 for doc in all_docs if doc.get("status") in ["OCR_CONCLUIDO", "PROCESSADO"])
    
    ai_results_ref = db.collection("ai_results").stream()
    total_analyses = sum(1 for _ in ai_results_ref)

    # Documentos por tipo
    doc_types = {}
    for doc in all_docs:
        tipo = doc.get("tipo_arquivo", "desconhecido")
        doc_types[tipo] = doc_types.get(tipo, 0) + 1

    # Status das análises
    status_counts = {}
    for doc in all_docs:
        status = doc.get("status", "DESCONHECIDO")
        status_counts[status] = status_counts.get(status, 0) + 1

    return {
        "total_users": total_users,
        "total_docs": total_docs,
        "analyzed_docs": analyzed_docs,
        "total_analyses": total_analyses,
        "doc_types": doc_types,
        "status_counts": status_counts
    }

@router.get("/users", response_model=list[UserResponse])
def list_users(admin_id: str = Depends(is_admin)):
    """Lista todos os usuários cadastrados."""
    users_ref = db.collection("users").stream()
    users = []
    for user in users_ref:
        data = user.to_dict()
        # Remove a senha do retorno
        data.pop("senha", None)
        users.append(data)
    return users

@router.post("/users", response_model=UserResponse)
def create_user_admin(user_data: UserCreate, admin_id: str = Depends(is_admin)):
    """Cadastra um novo usuário (apenas ADMIN)."""
    from app.services.auth_service import create_user
    try:
        new_user = create_user(user_data)
        # Remove a senha do retorno
        new_user.pop("senha", None)
        return new_user
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

@router.get("/logs")
def get_logs(admin_id: str = Depends(is_admin)):
    """Retorna os logs mais recentes."""
    logs_ref = (
        db.collection("logs")
        .order_by("data", direction="DESCENDING")
        .limit(100)
        .stream()
    )
    logs = [log.to_dict() for log in logs_ref]
    return logs