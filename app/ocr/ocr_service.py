import json
import os
import tempfile
from pathlib import Path

from google.api_core.client_options import ClientOptions
from google.cloud import documentai_v1 as documentai
from google.oauth2 import service_account

from app.services.document_processor import (
    processar_documento,
)


# ============================================================
# FORMATOS SUPORTADOS PELO DOCUMENT AI
# ============================================================

SUPPORTED_MIME_TYPES = {

    ".pdf":
        "application/pdf",

    ".gif":
        "image/gif",

    ".tif":
        "image/tiff",

    ".tiff":
        "image/tiff",

    ".jpg":
        "image/jpeg",

    ".jpeg":
        "image/jpeg",

    ".png":
        "image/png",

    ".bmp":
        "image/bmp",

    ".webp":
        "image/webp",

}


OCR_EXTENSIONS = set(
    SUPPORTED_MIME_TYPES
)


# ============================================================
# CLIENTE DOCUMENT AI
# ============================================================

def _get_document_ai_client():

    project_id = os.getenv(
        "DOCUMENT_AI_PROJECT_ID",
        ""
    ).strip()


    location = os.getenv(
        "DOCUMENT_AI_LOCATION",
        "us"
    ).strip()


    credentials_json = os.getenv(
        "DOCUMENT_AI_CREDENTIALS_JSON",
        ""
    ).strip()


    credentials_path = os.getenv(
        "DOCUMENT_AI_CREDENTIALS_PATH",
        ""
    ).strip()


    if not project_id:

        raise RuntimeError(
            "DOCUMENT_AI_PROJECT_ID não configurado"
        )


    if (
        not credentials_json
        and not credentials_path
    ):

        raise RuntimeError(

            "Credenciais do Document AI "
            "não configuradas. "
            "Use DOCUMENT_AI_CREDENTIALS_JSON "
            "ou DOCUMENT_AI_CREDENTIALS_PATH."

        )


    google_credentials = None


    # ========================================================
    # RENDER
    # ========================================================

    if credentials_json:

        try:

            credentials_data = json.loads(
                credentials_json
            )

        except json.JSONDecodeError as erro:

            raise RuntimeError(

                "DOCUMENT_AI_CREDENTIALS_JSON "
                "contém um JSON inválido"

            ) from erro


        google_credentials = (
            service_account
            .Credentials
            .from_service_account_info(
                credentials_data
            )
        )


    # ========================================================
    # AMBIENTE LOCAL
    # ========================================================

    elif credentials_path:

        google_credentials = (
            service_account
            .Credentials
            .from_service_account_file(
                credentials_path
            )
        )


    client_options = ClientOptions(

        api_endpoint=(
            f"{location}"
            "-documentai.googleapis.com"
        )

    )


    return (
        documentai
        .DocumentProcessorServiceClient(

            client_options=
                client_options,

            credentials=
                google_credentials,

        )
    )


# ============================================================
# PROCESSOR
# ============================================================

def _get_processor_name(
    client
):

    project_id = os.getenv(
        "DOCUMENT_AI_PROJECT_ID",
        ""
    ).strip()


    location = os.getenv(
        "DOCUMENT_AI_LOCATION",
        "us"
    ).strip()


    processor_id = os.getenv(
        "DOCUMENT_AI_PROCESSOR_ID",
        ""
    ).strip()


    if not processor_id:

        raise RuntimeError(
            "DOCUMENT_AI_PROCESSOR_ID "
            "não configurado"
        )


    return client.processor_path(

        project=project_id,

        location=location,

        processor=processor_id,

    )


# ============================================================
# DOCUMENT AI
# ============================================================

def _processar_bytes_document_ai(

    conteudo: bytes,

    nome_arquivo: str,

) -> str:

    extensao = (
        Path(
            nome_arquivo
        ).suffix.lower()
    )


    mime_type = (
        SUPPORTED_MIME_TYPES.get(
            extensao
        )
    )


    if not mime_type:

        raise ValueError(

            "Formato "
            f"{extensao or '(sem extensão)'} "
            "não suportado pelo Document AI"

        )


    if not conteudo:

        raise ValueError(
            "O arquivo está vazio"
        )


    client = (
        _get_document_ai_client()
    )


    processor_name = (
        _get_processor_name(
            client
        )
    )


    raw_document = (
        documentai.RawDocument(

            content=conteudo,

            mime_type=mime_type,

            display_name=(
                Path(
                    nome_arquivo
                ).name
            ),

        )
    )


    request = (
        documentai.ProcessRequest(

            name=processor_name,

            raw_document=raw_document,

            skip_human_review=True,

        )
    )


    response = (
        client.process_document(
            request=request
        )
    )


    texto = (
        response.document.text
        or ""
    )


    return texto.strip()


# ============================================================
# PROCESSAR QUALQUER DOCUMENTO
# ============================================================

def processar_conteudo_documento(

    conteudo: bytes,

    nome_arquivo: str,

) -> str:

    """
    PDF/imagens:
        Google Document AI.

    TXT/CSV/Excel/YAML:
        Extratores existentes.

    Nenhum arquivo é enviado para
    Firebase Storage.
    """

    if not conteudo:

        raise ValueError(
            "O arquivo está vazio"
        )


    extensao = (
        Path(
            nome_arquivo
        ).suffix.lower()
    )


    # ========================================================
    # PDF E IMAGENS
    # ========================================================

    if extensao in OCR_EXTENSIONS:

        return _processar_bytes_document_ai(

            conteudo,

            nome_arquivo,

        )


    # ========================================================
    # TXT / CSV / EXCEL / YAML
    # ========================================================

    try:

        with tempfile.NamedTemporaryFile(

            mode="wb",

            suffix=extensao,

            delete=True,

        ) as arquivo_temporario:

            arquivo_temporario.write(
                conteudo
            )

            arquivo_temporario.flush()


            resultado = (
                processar_documento(
                    arquivo_temporario.name
                )
            )


        if not resultado.get(
            "sucesso"
        ):

            raise ValueError(

                resultado.get(
                    "mensagem"
                )
                or
                "Erro ao processar documento"

            )


        return (
            resultado.get(
                "texto"
            )
            or ""
        ).strip()


    except Exception:

        raise


# ============================================================
# COMPATIBILIDADE
# ============================================================

def extrair_texto_arquivo(
    caminho_arquivo: str
) -> str:

    caminho = Path(
        caminho_arquivo
    )


    if not caminho.exists():

        raise FileNotFoundError(

            "Arquivo não encontrado: "
            f"{caminho_arquivo}"

        )


    return processar_conteudo_documento(

        caminho.read_bytes(),

        caminho.name,

    )


def extrair_texto_imagem(
    caminho_arquivo: str
) -> str:

    return extrair_texto_arquivo(
        caminho_arquivo
    )


def extrair_texto_pdf(
    caminho_arquivo: str
) -> str:

    return extrair_texto_arquivo(
        caminho_arquivo
    )