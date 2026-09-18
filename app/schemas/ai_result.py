from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AIResultResponse(BaseModel):
    id: str
    documento_id: str

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

    model_config = ConfigDict(from_attributes=True)