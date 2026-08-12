from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate
from app.utils.security import hash_password, verify_password, create_access_token


def create_user(db: Session, user_data: UserCreate) -> User:
    existing_user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if existing_user:
        raise ValueError("E-mail já cadastrado")

    new_user = User(
        nome=user_data.nome,
        email=user_data.email,
        senha=hash_password(user_data.senha),
        tipo_usuario=user_data.tipo_usuario,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def authenticate_user(db: Session, email: str, senha: str):
    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:
        return None

    if not verify_password(senha, user.senha):
        return None

    return user


def login_user(db: Session, email: str, senha: str) -> str:
    user = authenticate_user(db, email, senha)

    if not user:
        raise ValueError("E-mail ou senha inválidos")

    token = create_access_token(
        {
            "sub": str(user.id),
            "email": user.email
        }
    )

    return token