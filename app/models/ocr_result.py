from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class OCRResult(Base):
    __tablename__ = "ocr_results"

    id = Column(Integer, primary_key=True, autoincrement=True)

    documento_id = Column(
        Integer,
        ForeignKey("documents.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False
    )

    texto_extraido = Column(Text)
    status = Column(String(30), nullable=False, default="PENDENTE")
    data_processamento = Column(DateTime, nullable=True)

    documento = relationship(
        "Document",
        back_populates="ocr_result"
    )