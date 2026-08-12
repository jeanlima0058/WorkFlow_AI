from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    senha = Column(String(255), nullable=False)
    tipo_usuario = Column(String(30), nullable=False, default="usuario")
    data_criacao = Column(DateTime, server_default=func.now())

    documents = relationship(
        "Document",
        back_populates="usuario",
        cascade="all, delete-orphan"
    )