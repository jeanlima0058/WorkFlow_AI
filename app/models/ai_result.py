from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Float
)

from sqlalchemy.orm import relationship

from app.database import Base


class AIResult(Base):
    __tablename__ = "ai_results"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    documento_id = Column(
        Integer,
        ForeignKey(
            "documents.id",
            ondelete="CASCADE",
            onupdate="CASCADE"
        ),
        nullable=False,
        unique=True
    )

    tipo_documento = Column(
        String(100),
        nullable=True
    )

    categoria = Column(
        String(100),
        nullable=True
    )

    resumo = Column(
        Text,
        nullable=True
    )

    informacoes_principais = Column(
        Text,
        nullable=True
    )

    palavras_chave = Column(
        Text,
        nullable=True
    )

    alertas = Column(
        Text,
        nullable=True
    )

    confianca = Column(
        Float,
        nullable=True
    )

    status = Column(
        String(30),
        nullable=False,
        default="PENDENTE"
    )

    data_processamento = Column(
        DateTime,
        nullable=True
    )

    documento = relationship(
        "Document",
        back_populates="ai_result"
    )