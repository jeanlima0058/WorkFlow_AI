import os
import uuid

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.document import Document


UPLOAD_DIR = "uploads"


def salvar_documento(
    db: Session,
    arquivo: UploadFile,
    usuario_id: int
):
    # Garante que a pasta uploads exista
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # Recupera a extensão do arquivo original
    extensao = os.path.splitext(arquivo.filename)[1].lower()

    # Gera um nome único para o arquivo
    nome_unico = f"{uuid.uuid4()}{extensao}"

    # Define onde o arquivo será armazenado
    caminho = os.path.join(
        UPLOAD_DIR,
        nome_unico
    )

    # Salva o arquivo
    with open(caminho, "wb") as buffer:
        buffer.write(arquivo.file.read())

    # Obtém o tamanho do arquivo
    tamanho = os.path.getsize(caminho)

    # Cria o registro no banco
    documento = Document(
        usuario_id=usuario_id,
        nome_arquivo=arquivo.filename,
        tipo_arquivo=arquivo.content_type or "application/octet-stream",
        tamanho=tamanho,
        caminho_arquivo=caminho,
        status="RECEBIDO"
    )

    db.add(documento)
    db.commit()
    db.refresh(documento)

    return documento