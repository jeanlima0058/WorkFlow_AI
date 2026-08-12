from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth_service import create_user, login_user

from app.models.user import User
from app.utils.security import get_current_user

router = APIRouter(
    prefix="/auth",
    tags=["Autenticação"]
)


@router.post("/register", response_model=UserResponse)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    try:
        return create_user(db, user_data)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@router.post("/login", response_model=TokenResponse)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    try:
        token = login_user(
            db,
            login_data.email,
            login_data.senha
        )

        return {
            "access_token": token,
            "token_type": "bearer"
        }

    except ValueError as error:
        raise HTTPException(
            status_code=401,
            detail=str(error)
        )

@router.get("/me", response_model=UserResponse)
def get_me(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado"
        )

    return user