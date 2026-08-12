from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)

    usuario_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False
    )

    nome_arquivo = Column(String(255), nullable=False)
    tipo_arquivo = Column(String(100), nullable=False)
    tamanho = Column(BigInteger)
    caminho_arquivo = Column(String(500), nullable=False)
    status = Column(String(30), nullable=False, default="RECEBIDO")
    data_upload = Column(DateTime, server_default=func.now())

    usuario = relationship(
        "User",
        back_populates="documents"
    )

    ocr_result = relationship(
        "OCRResult",
        back_populates="documento",
        uselist=False,
        cascade="all, delete-orphan"
    )

    ai_result = relationship(
        "AIResult",
        back_populates="documento",
        uselist=False,
        cascade="all, delete-orphan"
    )