from fastapi import APIRouter, Depends, HTTPException
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import LoginRequest, TokenResponse

from app.services.auth_service import (
    create_user,
    login_user,
    get_user_by_id
)

from app.utils.security import get_current_user


router = APIRouter(
    prefix="/auth",
    tags=["Autenticação"]
)


@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate):

    try:
        return create_user(user_data)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@router.post("/login", response_model=TokenResponse)
def login(login_data: LoginRequest):

    try:
        token = login_user(
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
def get_me(user_id: str = Depends(get_current_user)):
    user = get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado"
        )

    return user