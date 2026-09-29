from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from app.firebase_config import db
from app.utils.security import (
    get_current_user,
)


router = APIRouter(

    prefix="/ocr",

    tags=[
        "Processamento de Documentos"
    ],

)


# ============================================================
# BUSCAR DOCUMENTO DO USUÁRIO
# ============================================================

def buscar_documento_usuario(
    document_id: str,
    usuario_id: str,
):

    documento_ref = (
        db.collection(
            "documents"
        ).document(
            document_id
        )
    )


    documento_snapshot = (
        documento_ref.get()
    )


    if not documento_snapshot.exists:

        raise HTTPException(

            status_code=404,

            detail=
                "Documento não encontrado",

        )


    documento = (
        documento_snapshot.to_dict()
    )


    if documento.get(
        "usuario_id"
    ) != str(usuario_id):

        raise HTTPException(

            status_code=404,

            detail=
                "Documento não encontrado",

        )


    return (
        documento_ref,
        documento
    )


# ============================================================
# PROCESSAR OCR
# ============================================================

@router.post(
    "/process/{document_id}"
)
def processar_documento_arquivo(

    document_id: str,

    usuario_id: str = Depends(
        get_current_user
    ),

):

    """
    Compatibilidade com o frontend.

    O OCR é executado durante:
        POST /documents/upload

    Como não utilizamos Firebase Storage,
    não existe arquivo disponível para uma
    segunda requisição.

    Esta rota apenas retorna o resultado
    que já foi salvo no Firestore.
    """

    _, documento = (
        buscar_documento_usuario(

            document_id,

            usuario_id,

        )
    )


    # ========================================================
    # BUSCA RESULTADO OCR
    # ========================================================

    resultados_query = (

        db.collection(
            "ocr_results"
        )

        .where(
            "documento_id",
            "==",
            document_id
        )

        .limit(1)

        .stream()

    )


    resultado_snapshot = next(

        resultados_query,

        None

    )


    if not resultado_snapshot:

        raise HTTPException(

            status_code=404,

            detail=(
                "Este documento ainda "
                "não possui resultado "
                "de OCR"
            ),

        )


    resultado = (
        resultado_snapshot.to_dict()
    )


    # ========================================================
    # VERIFICA STATUS
    # ========================================================

    if resultado.get(
        "status"
    ) != "CONCLUIDO":

        raise HTTPException(

            status_code=409,

            detail=(
                "O OCR deste documento "
                "não foi concluído. "
                "Envie o arquivo novamente "
                "para processá-lo."
            ),

        )


    return {

        "message":
            "Documento já processado com sucesso",

        "documento_id":
            document_id,

        "status":
            resultado.get(
                "status"
            ),

        "texto_extraido":
            resultado.get(
                "texto_extraido"
            ),

    }


# ============================================================
# LISTAR RESULTADOS OCR
# ============================================================

@router.get("/")
def listar_resultados_ocr(

    usuario_id: str = Depends(
        get_current_user
    ),

):

    documentos_query = (

        db.collection(
            "documents"
        )

        .where(
            "usuario_id",
            "==",
            str(usuario_id)
        )

        .stream()

    )


    documentos = {

        documento.id:
            documento.to_dict()

        for documento
        in documentos_query

    }


    resultados_query = (
        db.collection(
            "ocr_results"
        ).stream()
    )


    resultados = []


    for resultado_snapshot in (
        resultados_query
    ):

        resultado = (
            resultado_snapshot.to_dict()
        )


        documento_id = (
            resultado.get(
                "documento_id"
            )
        )


        documento = documentos.get(
            documento_id
        )


        if not documento:

            continue


        resultados.append({

            "id":
                resultado.get(
                    "id"
                ),

            "documento_id":
                documento_id,

            "nome_arquivo":
                documento.get(
                    "nome_arquivo"
                ),

            "status":
                resultado.get(
                    "status"
                ),

            "texto_extraido":
                resultado.get(
                    "texto_extraido"
                ),

            "data_processamento":
                resultado.get(
                    "data_processamento"
                ),

        })


    resultados.sort(

        key=lambda resultado:
            resultado.get(
                "data_processamento"
            ) or "",

        reverse=True,

    )


    return resultados


# ============================================================
# OBTER RESULTADO OCR
# ============================================================

@router.get(
    "/{document_id}"
)
def obter_resultado_ocr(

    document_id: str,

    usuario_id: str = Depends(
        get_current_user
    ),

):

    _, documento = (
        buscar_documento_usuario(

            document_id,

            usuario_id,

        )
    )


    resultados_query = (

        db.collection(
            "ocr_results"
        )

        .where(
            "documento_id",
            "==",
            document_id
        )

        .limit(1)

        .stream()

    )


    resultado_snapshot = next(

        resultados_query,

        None

    )


    if not resultado_snapshot:

        raise HTTPException(

            status_code=404,

            detail=(
                "Este documento ainda "
                "não possui um resultado "
                "de processamento"
            ),

        )


    resultado = (
        resultado_snapshot.to_dict()
    )


    return {

        "id":
            resultado.get(
                "id"
            ),

        "documento_id":
            document_id,

        "nome_arquivo":
            documento.get(
                "nome_arquivo"
            ),

        "tipo_arquivo":
            documento.get(
                "tipo_arquivo"
            ),

        "status_documento":
            documento.get(
                "status"
            ),

        "status_ocr":
            resultado.get(
                "status"
            ),

        "texto_extraido":
            resultado.get(
                "texto_extraido"
            ),

        "data_processamento":
            resultado.get(
                "data_processamento"
            ),

    }