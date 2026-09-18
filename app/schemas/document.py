from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    id: str
    usuario_id: str
    nome_arquivo: str
    tipo_arquivo: str
    tamanho: int | None = None
    caminho_arquivo: str
    status: str
    data_upload: datetime

    model_config = ConfigDict(from_attributes=True)