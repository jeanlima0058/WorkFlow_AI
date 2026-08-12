from sqlalchemy import Column, Integer, String, JSON, DECIMAL, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class AIResult(Base):
    __tablename__ = "ai_results"

    id = Column(Integer, primary_key=True, autoincrement=True)

    documento_id = Column(
        Integer,
        ForeignKey("documents.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False
    )

    tipo_documento = Column(String(100))
    dados_extraidos = Column(JSON)
    confianca = Column(DECIMAL(5, 4))
    data_analise = Column(DateTime, server_default=func.now())

    documento = relationship(
        "Document",
        back_populates="ai_result"
    )