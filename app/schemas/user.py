from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict


class UserCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    tipo_usuario: str = "usuario"


class UserResponse(BaseModel):
    id: str
    nome: str
    email: EmailStr
    tipo_usuario: str
    data_criacao: datetime

    model_config = ConfigDict(
        from_attributes=True
    )