from datetime import datetime, timezone
from app.firebase_config import db
from app.schemas.user import UserCreate
from app.utils.security import hash_password, verify_password, create_access_token

def create_user(user_data: UserCreate) -> dict:
    email = str(user_data.email).lower().strip()
    
    existing_users = db.collection("users").where("email", "==", email).limit(1).stream()
    if next(existing_users, None) is not None:
        raise ValueError("E-mail já cadastrado")

    user_ref = db.collection("users").document()
    user_data_firestore = {
        "id": user_ref.id,
        "nome": user_data.nome,
        "email": email,
        "senha": hash_password(user_data.senha),
        "tipo_usuario": user_data.tipo_usuario,
        "data_criacao": datetime.now(timezone.utc)
    }
    user_ref.set(user_data_firestore)
    return user_data_firestore

def authenticate_user(email: str, senha: str):
    email = email.lower().strip()
    users = db.collection("users").where("email", "==", email).limit(1).stream()
    user_document = next(users, None)
    if user_document is None:
        return None
    user = user_document.to_dict()
    if not verify_password(senha, user["senha"]):
        return None
    return user

def login_user(email: str, senha: str) -> str:
    user = authenticate_user(email, senha)
    if not user:
        raise ValueError("E-mail ou senha inválidos")
    token = create_access_token({"sub": str(user["id"]), "email": user["email"]})
    return token

def get_user_by_id(user_id: str):
    user_ref = db.collection("users").document(str(user_id))
    user_document = user_ref.get()
    if not user_document.exists:
        return None
    return user_document.to_dict()