from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AIResultResponse(BaseModel):

    id: int

    documento_id: int

    tipo_documento: Optional[str] = None

    categoria: Optional[str] = None

    resumo: Optional[str] = None

    informacoes_principais: Optional[str] = None

    insights: Optional[str] = None

    recomendacoes: Optional[str] = None

    palavras_chave: Optional[str] = None

    alertas: Optional[str] = None

    confianca: Optional[float] = None

    status: str

    data_processamento: Optional[datetime] = None

    class Config:
        from_attributes = True