import os
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from app.firebase_config import db
from app.ocr.ocr_service import (
    extrair_texto_imagem,
    extrair_texto_pdf
)
from app.utils.security import get_current_user


router = APIRouter(
    prefix="/ocr",
    tags=["Processamento de Documentos"]
)


EXTENSOES_IMAGEM = {
    ".png",
    ".jpg",
    ".jpeg",
    ".bmp",
    ".tiff"
}

EXTENSOES_PDF = {
    ".pdf"
}


def buscar_documento_usuario(
    document_id: str,
    usuario_id: str
):
    documento_ref = db.collection("documents").document(document_id)
    documento_snapshot = documento_ref.get()

    if not documento_snapshot.exists:
        raise HTTPException(
            status_code=404,
            detail="Documento não encontrado"
        )

    documento = documento_snapshot.to_dict()

    if documento.get("usuario_id") != str(usuario_id):
        raise HTTPException(
            status_code=404,
            detail="Documento não encontrado"
        )

    return documento_ref, documento


def executar_ocr(caminho_arquivo: str) -> str:
    extensao = os.path.splitext(caminho_arquivo)[1].lower()

    if extensao in EXTENSOES_IMAGEM:
        return extrair_texto_imagem(caminho_arquivo)

    if extensao in EXTENSOES_PDF:
        return extrair_texto_pdf(caminho_arquivo)

    raise ValueError("Formato de arquivo não suportado")


@router.post("/process/{document_id}")
def processar_documento_arquivo(
    document_id: str,
    usuario_id: str = Depends(get_current_user)
):
    documento_ref, documento = buscar_documento_usuario(
        document_id,
        usuario_id
    )

    caminho_arquivo = documento.get("caminho_arquivo")

    if not caminho_arquivo or not os.path.exists(caminho_arquivo):
        raise HTTPException(
            status_code=404,
            detail="Arquivo do documento não encontrado"
        )

    ocr_query = (
        db.collection("ocr_results")
        .where("documento_id", "==", document_id)
        .limit(1)
        .stream()
    )

    resultado_documento = next(ocr_query, None)

    agora = datetime.now(timezone.utc)

    try:
        documento_ref.update({
            "status": "PROCESSANDO"
        })

        if resultado_documento:
            resultado_ref = resultado_documento.reference
        else:
            resultado_ref = db.collection("ocr_results").document()

            resultado_ref.set({
                "id": resultado_ref.id,
                "documento_id": document_id,
                "status": "PROCESSANDO",
                "texto_extraido": None,
                "data_processamento": None
            })

        resultado_ref.update({
            "status": "PROCESSANDO"
        })

        texto_extraido = executar_ocr(caminho_arquivo)

        resultado_ref.update({
            "status": "CONCLUIDO",
            "texto_extraido": texto_extraido,
            "data_processamento": agora
        })

        documento_ref.update({
            "status": "PROCESSADO"
        })

        return {
            "message": "Documento processado com sucesso",
            "documento_id": document_id,
            "status": "CONCLUIDO",
            "texto_extraido": texto_extraido
        }

    except Exception as error:
        documento_ref.update({
            "status": "ERRO"
        })

        if resultado_documento:
            resultado_documento.reference.update({
                "status": "ERRO",
                "data_processamento": agora
            })

        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar documento: {str(error)}"
        )


@router.get("/")
def listar_resultados_ocr(
    usuario_id: str = Depends(get_current_user)
):
    documentos_query = (
        db.collection("documents")
        .where("usuario_id", "==", str(usuario_id))
        .stream()
    )

    documentos = {
        documento.id: documento.to_dict()
        for documento in documentos_query
    }

    resultados_query = (
        db.collection("ocr_results")
        .stream()
    )

    resultados = []

    for resultado_snapshot in resultados_query:
        resultado = resultado_snapshot.to_dict()
        documento_id = resultado.get("documento_id")

        documento = documentos.get(documento_id)

        if not documento:
            continue

        resultados.append({
            "id": resultado.get("id"),
            "documento_id": documento_id,
            "nome_arquivo": documento.get("nome_arquivo"),
            "status": resultado.get("status"),
            "texto_extraido": resultado.get("texto_extraido"),
            "data_processamento": resultado.get(
                "data_processamento"
            )
        })

    resultados.sort(
        key=lambda resultado: (
            resultado.get("data_processamento") or ""
        ),
        reverse=True
    )

    return resultados


@router.get("/{document_id}")
def obter_resultado_ocr(
    document_id: str,
    usuario_id: str = Depends(get_current_user)
):
    _, documento = buscar_documento_usuario(
        document_id,
        usuario_id
    )

    resultados_query = (
        db.collection("ocr_results")
        .where("documento_id", "==", document_id)
        .limit(1)
        .stream()
    )

    resultado_snapshot = next(resultados_query, None)

    if not resultado_snapshot:
        raise HTTPException(
            status_code=404,
            detail=(
                "Este documento ainda não possui "
                "um resultado de processamento"
            )
        )

    resultado = resultado_snapshot.to_dict()

    return {
        "id": resultado.get("id"),
        "documento_id": document_id,
        "nome_arquivo": documento.get("nome_arquivo"),
        "tipo_arquivo": documento.get("tipo_arquivo"),
        "status_documento": documento.get("status"),
        "status_ocr": resultado.get("status"),
        "texto_extraido": resultado.get("texto_extraido"),
        "data_processamento": resultado.get(
            "data_processamento"
        )
    }