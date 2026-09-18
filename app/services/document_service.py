import os
import uuid

from datetime import datetime, timezone
from pathlib import Path

from fastapi import UploadFile, HTTPException

from app.firebase_config import db

from app.ocr.ocr_service import (
    extrair_texto_imagem,
    extrair_texto_pdf
)


UPLOAD_DIR = "uploads"

EXTENSOES_PERMITIDAS = {
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".bmp",
    ".tiff"
}

TAMANHO_MAXIMO = 10 * 1024 * 1024  # 10 MB

EXTENSOES_BLOQUEADAS = {
    ".exe",
    ".bat",
    ".cmd",
    ".com",
    ".msi",
    ".ps1",
    ".vbs",
    ".js",
    ".jar",
    ".scr",
    ".dll",
    ".sh"
}

def validar_arquivo(arquivo: UploadFile, conteudo: bytes):
    nome_arquivo = arquivo.filename or ""

    extensao = Path(nome_arquivo).suffix.lower()

    if not extensao:
        raise HTTPException(
            status_code=400,
            detail="O arquivo precisa ter uma extensão"
        )

    if extensao in EXTENSOES_BLOQUEADAS:
        raise HTTPException(
            status_code=400,
            detail="Tipo de arquivo bloqueado por segurança"
        )

    if extensao not in EXTENSOES_PERMITIDAS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Formato não permitido. "
                "Envie PDF ou uma imagem compatível"
            )
        )

    if not conteudo:
        raise HTTPException(
            status_code=400,
            detail="O arquivo está vazio"
        )

    if len(conteudo) > TAMANHO_MAXIMO:
        raise HTTPException(
            status_code=413,
            detail="O arquivo excede o limite de 10 MB"
        )

def salvar_documento(
    arquivo: UploadFile,
    usuario_id: str
):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    nome_original = arquivo.filename or "arquivo_sem_nome"

    extensao = Path(nome_original).suffix.lower()

    # Lê o conteúdo antes de salvar
    conteudo = arquivo.file.read()

    # Valida o arquivo antes de gravá-lo
    validar_arquivo(arquivo, conteudo)

    nome_unico = f"{uuid.uuid4()}{extensao}"

    caminho = os.path.join(
        UPLOAD_DIR,
        nome_unico
    )

    # Salva somente após a validação
    with open(caminho, "wb") as buffer:
        buffer.write(conteudo)

    tamanho = len(conteudo)

    documento_ref = db.collection("documents").document()

    data_upload = datetime.now(timezone.utc)

    documento = {
        "id": documento_ref.id,
        "usuario_id": str(usuario_id),
        "nome_arquivo": arquivo.filename or "arquivo_sem_nome",
        "tipo_arquivo": (
            arquivo.content_type
            or "application/octet-stream"
        ),
        "tamanho": tamanho,
        "caminho_arquivo": caminho,
        "status": "RECEBIDO",
        "data_upload": data_upload
    }

    documento_ref.set(documento)

    ocr_ref = db.collection("ocr_results").document()

    ocr_resultado = {
        "id": ocr_ref.id,
        "documento_id": documento_ref.id,
        "status": "PROCESSANDO",
        "texto_extraido": None,
        "data_processamento": None
    }

    ocr_ref.set(ocr_resultado)

    try:
        # Processamento de PDF
        if extensao == ".pdf":
            texto = extrair_texto_pdf(caminho)

        # Processamento de imagens
        elif extensao in [
            ".png",
            ".jpg",
            ".jpeg",
            ".bmp",
            ".tiff"
        ]:
            texto = extrair_texto_imagem(caminho)

        # Formato não suportado
        else:
            db.collection("ocr_results").document(
                ocr_ref.id
            ).update({
                "status": "NAO_SUPORTADO",
                "texto_extraido": None
            })

            db.collection("documents").document(
                documento_ref.id
            ).update({
                "status": "RECEBIDO"
            })

            return documento

        data_processamento = datetime.now(timezone.utc)

        db.collection("ocr_results").document(
            ocr_ref.id
        ).update({
            "texto_extraido": texto,
            "status": "CONCLUIDO",
            "data_processamento": data_processamento
        })

        db.collection("documents").document(
            documento_ref.id
        ).update({
            "status": "OCR_CONCLUIDO"
        })

        documento["status"] = "OCR_CONCLUIDO"

    except Exception:
        data_processamento = datetime.now(timezone.utc)

        db.collection("ocr_results").document(
            ocr_ref.id
        ).update({
            "status": "ERRO",
            "data_processamento": data_processamento
        })

        db.collection("documents").document(
            documento_ref.id
        ).update({
            "status": "OCR_ERRO"
        })

        documento["status"] = "OCR_ERRO"

    return documento