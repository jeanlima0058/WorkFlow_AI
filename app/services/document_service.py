from datetime import datetime, timezone
from pathlib import Path

from fastapi import HTTPException, UploadFile

from app.firebase_config import db


# ============================================================
# EXTENSÕES PERMITIDAS
# ============================================================

EXTENSOES_PERMITIDAS = {
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".bmp",
    ".tiff",
    ".tif",
    ".gif",
    ".webp",
    ".txt",
    ".csv",
    ".xls",
    ".xlsx",
    ".xlsm",
    ".yaml",
    ".yml",
}


# ============================================================
# MIME TYPES
# ============================================================

MIMES_PERMITIDOS = {
    ".pdf": "application/pdf",

    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".bmp": "image/bmp",
    ".tiff": "image/tiff",
    ".tif": "image/tiff",
    ".webp": "image/webp",

    ".txt": "text/plain",
    ".csv": "text/csv",

    ".xls": "application/vnd.ms-excel",

    ".xlsx": (
        "application/vnd.openxmlformats-officedocument."
        "spreadsheetml.sheet"
    ),

    ".xlsm": (
        "application/vnd.ms-excel.sheet.macroEnabled.12"
    ),

    ".yaml": "application/x-yaml",
    ".yml": "application/x-yaml",
}


# ============================================================
# LIMITE DE TAMANHO
# ============================================================

TAMANHO_MAXIMO = 10 * 1024 * 1024


# ============================================================
# EXTENSÕES BLOQUEADAS
# ============================================================

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
    ".sh",
}


# ============================================================
# VALIDAÇÃO
# ============================================================

def validar_arquivo(
    arquivo: UploadFile,
    conteudo: bytes
) -> str:

    nome_arquivo = arquivo.filename or ""

    extensao = Path(
        nome_arquivo
    ).suffix.lower()


    if not extensao:

        raise HTTPException(
            status_code=400,
            detail="O arquivo precisa ter uma extensão",
        )


    if extensao in EXTENSOES_BLOQUEADAS:

        raise HTTPException(
            status_code=400,
            detail="Tipo de arquivo bloqueado por segurança",
        )


    if extensao not in EXTENSOES_PERMITIDAS:

        raise HTTPException(
            status_code=400,
            detail=(
                "Formato não permitido. "
                "Envie PDF, imagens, TXT, CSV, "
                "XLS, XLSX, XLSM, YAML ou YML."
            ),
        )


    if not conteudo:

        raise HTTPException(
            status_code=400,
            detail="O arquivo está vazio",
        )


    if len(conteudo) > TAMANHO_MAXIMO:

        raise HTTPException(
            status_code=413,
            detail="O arquivo excede o limite de 10 MB",
        )


    return extensao


# ============================================================
# MIME TYPE
# ============================================================

def obter_mime_type(
    extensao: str
) -> str:

    return MIMES_PERMITIDOS.get(
        extensao.lower(),
        "application/octet-stream",
    )


# ============================================================
# SALVAR DOCUMENTO
# ============================================================

def salvar_documento(
    arquivo: UploadFile,
    usuario_id: str,
    conteudo: bytes | None = None,
):

    nome_original = (
        arquivo.filename
        or "arquivo_sem_nome"
    )


    # Se o conteúdo ainda não foi recebido,
    # lê diretamente do UploadFile.
    if conteudo is None:

        conteudo = arquivo.file.read()


    extensao = validar_arquivo(
        arquivo,
        conteudo
    )


    mime_type = obter_mime_type(
        extensao
    )


    tamanho = len(conteudo)


    # ========================================================
    # CRIA DOCUMENTO NO FIRESTORE
    # ========================================================

    documento_ref = (
        db.collection("documents")
        .document()
    )


    data_upload = datetime.now(
        timezone.utc
    )


    documento = {

        "id": documento_ref.id,

        "usuario_id": str(
            usuario_id
        ),

        "nome_arquivo": nome_original,

        "tipo_arquivo": mime_type,

        "tamanho": tamanho,

        # Não existe Firebase Storage.
        # O arquivo é processado apenas durante
        # a requisição.
        "caminho_arquivo": None,

        "status": "RECEBIDO",

        "data_upload": data_upload,
    }


    documento_ref.set(
        documento
    )


    # ========================================================
    # CRIA RESULTADO DE OCR
    # ========================================================

    ocr_ref = (
        db.collection("ocr_results")
        .document()
    )


    ocr_ref.set({

        "id": ocr_ref.id,

        "documento_id": documento_ref.id,

        "status": "PENDENTE",

        "texto_extraido": None,

        "data_processamento": None,

    })


    return documento


# ============================================================
# BUSCA DE DOCUMENTOS
# ============================================================

def buscar_documentos_por_termo(
    usuario_id: str,
    termo: str
):

    resultados = []


    # ========================================================
    # DOCUMENTOS DO USUÁRIO
    # ========================================================

    docs_ref = (
        db.collection("documents")
        .where(
            "usuario_id",
            "==",
            str(usuario_id)
        )
        .stream()
    )


    docs_map = {
        doc.id: doc.to_dict()
        for doc in docs_ref
    }


    if not docs_map:
        return []


    # ========================================================
    # RESULTADOS DE IA
    # ========================================================

    ai_results_ref = (
        db.collection("ai_results")
        .stream()
    )


    for ai_doc in ai_results_ref:

        ai_data = ai_doc.to_dict()

        doc_id = ai_data.get(
            "documento_id"
        )


        if doc_id not in docs_map:
            continue


        doc = docs_map[
            doc_id
        ]


        match_found = False

        match_type = None

        insight_snippet = None


        # ====================================================
        # PALAVRAS-CHAVE
        # ====================================================

        palavras_chave = (
            ai_data.get(
                "palavras_chave"
            )
            or ""
        ).lower()


        if termo in palavras_chave:

            match_found = True

            match_type = (
                "palavra_chave"
            )


        # ====================================================
        # INSIGHTS
        # ====================================================

        insights = (
            ai_data.get(
                "insights"
            )
            or ""
        ).lower()


        if termo in insights:

            match_found = True

            match_type = "insight"


            idx = insights.find(
                termo
            )


            start = max(
                0,
                idx - 50
            )


            end = min(
                len(insights),
                idx + len(termo) + 50
            )


            insight_snippet = (
                "..."
                + ai_data["insights"][
                    start:end
                ]
                + "..."
            )


        # ====================================================
        # RESULTADO
        # ====================================================

        if match_found:

            resultados.append({

                "id": doc_id,

                "nome_arquivo": doc.get(
                    "nome_arquivo"
                ),

                "tipo_arquivo": doc.get(
                    "tipo_arquivo"
                ),

                "tamanho": doc.get(
                    "tamanho"
                ),

                "data_upload": doc.get(
                    "data_upload"
                ),

                "status": doc.get(
                    "status"
                ),

                "match_type": match_type,

                "insight_snippet":
                    insight_snippet,

                "palavras_chave":
                    ai_data.get(
                        "palavras_chave"
                    ),

            })


    return resultados