from fastapi import APIRouter, Depends, HTTPException
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth_service import create_user, login_user, get_user_by_id
from app.utils.security import get_current_user
from app.firebase_config import db
from datetime import datetime, timezone

router = APIRouter(prefix="/auth", tags=["Autenticação"])

def registrar_log(usuario_id: str, usuario_email: str, acao: str, descricao: str, documento_id: str = None):
    """Registra um log no Firestore."""
    log_ref = db.collection("logs").document()
    log_ref.set({
        "id": log_ref.id,
        "usuario_id": str(usuario_id),
        "usuario_email": usuario_email,
        "acao": acao,
        "descricao": descricao,
        "documento_id": documento_id,
        "data": datetime.now(timezone.utc)
    })

@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate):
    try:
        new_user = create_user(user_data)
        registrar_log(
            usuario_id=new_user["id"],
            usuario_email=new_user["email"],
            acao="CADASTRO_USUARIO",
            descricao=f"Novo usuário cadastrado: {new_user['email']}"
        )
        return new_user
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

@router.post("/login", response_model=TokenResponse)
def login(login_data: LoginRequest):
    try:
        token = login_user(login_data.email, login_data.senha)
        # Busca o usuário para pegar o ID e registrar o log
        users = db.collection("users").where("email", "==", login_data.email.lower().strip()).limit(1).stream()
        user_doc = next(users, None)
        if user_doc:
            user_data = user_doc.to_dict()
            registrar_log(
                usuario_id=user_data["id"],
                usuario_email=user_data["email"],
                acao="LOGIN",
                descricao="Login realizado com sucesso"
            )
        return {"access_token": token, "token_type": "bearer"}
    except ValueError as error:
        raise HTTPException(status_code=401, detail=str(error))

@router.get("/me", response_model=UserResponse)
def get_me(user_id: str = Depends(get_current_user)):
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    # Remove a senha antes de retornar
    user.pop("senha", None)
    return user