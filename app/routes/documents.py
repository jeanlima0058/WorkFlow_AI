from datetime import datetime, timezone
from typing import List

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
)

from app.firebase_config import db
from app.ocr.ocr_service import (
    processar_conteudo_documento,
)
from app.schemas.document import DocumentResponse
from app.services.document_service import (
    buscar_documentos_por_termo,
    salvar_documento,
)
from app.utils.security import (
    get_current_user,
)


router = APIRouter(
    prefix="/documents",
    tags=["Documentos"],
)


# ============================================================
# UPLOAD
# ============================================================

@router.post(
    "/upload",
    response_model=DocumentResponse
)
async def upload_documento(
    arquivo: UploadFile = File(...),
    usuario_id: str = Depends(
        get_current_user
    ),
):

    try:

        # ====================================================
        # LÊ O ARQUIVO NA MEMÓRIA
        # ====================================================

        conteudo = await arquivo.read()


        # ====================================================
        # CRIA REGISTRO DO DOCUMENTO
        # ====================================================

        documento = salvar_documento(

            arquivo=arquivo,

            usuario_id=usuario_id,

            conteudo=conteudo,

        )


        documento_ref = (
            db.collection("documents")
            .document(
                documento["id"]
            )
        )


        # ====================================================
        # LOCALIZA OCR
        # ====================================================

        ocr_query = (
            db.collection("ocr_results")
            .where(
                "documento_id",
                "==",
                documento["id"]
            )
            .limit(1)
            .stream()
        )


        ocr_snapshot = next(
            ocr_query,
            None
        )


        if ocr_snapshot:

            ocr_ref = (
                ocr_snapshot.reference
            )

        else:

            ocr_ref = (
                db.collection(
                    "ocr_results"
                ).document()
            )


            ocr_ref.set({

                "id": ocr_ref.id,

                "documento_id":
                    documento["id"],

                "status": "PENDENTE",

                "texto_extraido": None,

                "data_processamento":
                    None,

            })


        # ====================================================
        # STATUS PROCESSANDO
        # ====================================================

        documento_ref.update({

            "status":
                "PROCESSANDO"

        })


        ocr_ref.update({

            "status":
                "PROCESSANDO"

        })


        # ====================================================
        # PROCESSAMENTO
        # ====================================================

        texto_extraido = (
            processar_conteudo_documento(

                conteudo=conteudo,

                nome_arquivo=
                    documento[
                        "nome_arquivo"
                    ],

            )
        )


        # ====================================================
        # VERIFICA TEXTO
        # ====================================================

        if not texto_extraido:

            raise ValueError(
                "O arquivo foi processado, "
                "mas nenhum conteúdo foi extraído"
            )


        agora = datetime.now(
            timezone.utc
        )


        # ====================================================
        # SALVA OCR
        # ====================================================

        ocr_ref.update({

            "status":
                "CONCLUIDO",

            "texto_extraido":
                texto_extraido,

            "data_processamento":
                agora,

        })


        # ====================================================
        # ATUALIZA DOCUMENTO
        # ====================================================

        documento_ref.update({

            "status":
                "PROCESSADO",

        })


        documento["status"] = (
            "PROCESSADO"
        )


        return documento


    except HTTPException:

        raise


    except Exception as erro:

        # ====================================================
        # REGISTRA ERRO
        # ====================================================

        if "documento" in locals():

            documento_ref = (
                db.collection(
                    "documents"
                ).document(
                    documento["id"]
                )
            )


            documento_ref.update({

                "status":
                    "ERRO"

            })


            ocr_query = (
                db.collection(
                    "ocr_results"
                )
                .where(
                    "documento_id",
                    "==",
                    documento["id"]
                )
                .limit(1)
                .stream()
            )


            ocr_snapshot = next(
                ocr_query,
                None
            )


            if ocr_snapshot:

                ocr_snapshot.reference.update({

                    "status":
                        "ERRO",

                    "data_processamento":
                        datetime.now(
                            timezone.utc
                        ),

                })


        raise HTTPException(

            status_code=500,

            detail=(
                "Erro ao processar documento: "
                f"{str(erro)}"
            ),

        )


# ============================================================
# LISTAR DOCUMENTOS
# ============================================================

@router.get(
    "/",
    response_model=List[
        DocumentResponse
    ]
)
def listar_documentos(
    usuario_id: str = Depends(
        get_current_user
    ),
):

    documentos_ref = (
        db.collection("documents")
        .where(
            "usuario_id",
            "==",
            str(usuario_id)
        )
        .stream()
    )


    documentos = [

        documento.to_dict()

        for documento
        in documentos_ref

    ]


    documentos.sort(

        key=lambda doc:
            doc.get(
                "data_upload"
            ) or "",

        reverse=True,

    )


    return documentos


# ============================================================
# PESQUISAR DOCUMENTOS
# ============================================================

@router.get("/search")
def pesquisar_documentos(

    q: str = Query(
        ...,
        description=
            "Termo de pesquisa"
    ),

    usuario_id: str = Depends(
        get_current_user
    ),

):

    if not q or len(
        q.strip()
    ) < 2:

        raise HTTPException(

            status_code=400,

            detail=(
                "O termo de pesquisa "
                "deve ter pelo menos "
                "2 caracteres."
            ),

        )


    termo = q.strip().lower()


    return buscar_documentos_por_termo(

        usuario_id,
        termo

    )


# ============================================================
# OBTER DOCUMENTO
# ============================================================

@router.get(
    "/{document_id}",
    response_model=DocumentResponse
)
def obter_documento(

    document_id: str,

    usuario_id: str = Depends(
        get_current_user
    ),

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


    return documento


# ============================================================
# EXCLUIR DOCUMENTO
# ============================================================

@router.delete(
    "/{document_id}"
)
def excluir_documento(

    document_id: str,

    usuario_id: str = Depends(
        get_current_user
    ),

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


    try:

        # ====================================================
        # NÃO EXISTE ARQUIVO NO STORAGE
        # ====================================================

        # O arquivo já foi processado durante o upload.
        # Portanto, não existe arquivo físico para excluir.


        # ====================================================
        # EXCLUI OCR
        # ====================================================

        ocr_docs = (
            db.collection(
                "ocr_results"
            )
            .where(
                "documento_id",
                "==",
                document_id
            )
            .stream()
        )


        for ocr_doc in ocr_docs:

            ocr_doc.reference.delete()


        # ====================================================
        # EXCLUI RESULTADO DA IA
        # ====================================================

        ai_docs = (
            db.collection(
                "ai_results"
            )
            .where(
                "documento_id",
                "==",
                document_id
            )
            .stream()
        )


        for ai_doc in ai_docs:

            ai_doc.reference.delete()


        # ====================================================
        # EXCLUI DOCUMENTO
        # ====================================================

        documento_ref.delete()


        return {

            "message":
                "Documento excluído com sucesso"

        }


    except Exception as erro:

        raise HTTPException(

            status_code=500,

            detail=(
                "Erro ao excluir documento: "
                f"{str(erro)}"
            ),

        )