from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.firebase_config import db
from app.schemas.ai_result import AIResultResponse
from app.services.ai_service import analisar_documento
from app.services.direct_ai_service import analisar_arquivo_gemini
from app.services.document_service import salvar_documento
from app.utils.security import get_current_user

router = APIRouter(prefix="/ai", tags=["Inteligência Artificial"])


def registrar_log_ai(usuario_id: str, documento_id: str, acao: str, descricao: str):
    log_ref = db.collection("logs").document()
    log_ref.set({
        "id": log_ref.id,
        "usuario_id": str(usuario_id),
        "usuario_email": "",
        "acao": acao,
        "descricao": descricao,
        "documento_id": documento_id,
        "data": datetime.now(timezone.utc),
    })


@router.post("/analyze-upload", response_model=AIResultResponse)
async def analisar_upload_direto(
    arquivo: UploadFile = File(...),
    instrucao: str = Form(default=""),
    provedor: str = Form(default="gemini"),
    usuario_id: str = Depends(get_current_user),
):
    """Cria o registro, envia o arquivo diretamente à IA e devolve o resultado ao frontend."""
    conteudo = await arquivo.read()
    if not conteudo:
        raise HTTPException(status_code=400, detail="O arquivo está vazio.")

    provedor = (provedor or "gemini").strip().lower()
    if provedor not in {"gemini", "grok", "llama"}:
        raise HTTPException(status_code=400, detail="Provedor de IA inválido.")
    if provedor != "gemini":
        raise HTTPException(
            status_code=501,
            detail=f"{provedor.capitalize()} aparece como opção, mas sua integração ainda não foi configurada. Use Gemini por enquanto.",
        )

    try:
        documento = salvar_documento(
            arquivo=arquivo,
            usuario_id=usuario_id,
            conteudo=conteudo,
        )
    except HTTPException:
        raise
    except Exception as erro:
        raise HTTPException(status_code=500, detail=f"Não foi possível registrar o documento: {erro}") from erro

    documento_id = documento["id"]
    documento_ref = db.collection("documents").document(documento_id)
    documento_ref.update({"status": "ANALISANDO"})

    # O registro de OCR é mantido para compatibilidade com o histórico antigo,
    # mas não é executado neste fluxo.
    ocr_query = db.collection("ocr_results").where("documento_id", "==", documento_id).limit(1).stream()
    ocr_snapshot = next(ocr_query, None)
    if ocr_snapshot:
        ocr_snapshot.reference.update({"status": "DISPENSADO_LEITURA_DIRETA"})

    try:
        analise = analisar_arquivo_gemini(
            conteudo=conteudo,
            nome_arquivo=arquivo.filename or "arquivo",
            instrucao=instrucao,
            provedor=provedor,
        )
    except NotImplementedError as erro:
        documento_ref.update({"status": "ERRO"})
        raise HTTPException(status_code=501, detail=str(erro)) from erro
    except ValueError as erro:
        documento_ref.update({"status": "ERRO"})
        raise HTTPException(status_code=415, detail=str(erro)) from erro
    except Exception as erro:
        documento_ref.update({"status": "ERRO"})
        raise HTTPException(status_code=502, detail=f"Falha na análise com Gemini: {erro}") from erro

    agora = datetime.now(timezone.utc)
    resultado_ref = db.collection("ai_results").document()
    resultado = {
        "id": resultado_ref.id,
        "documento_id": documento_id,
        **analise,
        "provedor": provedor,
        "status": "CONCLUIDO",
        "data_processamento": agora,
    }
    resultado_ref.set(resultado)
    documento_ref.update({"status": "ANALISADO"})

    registrar_log_ai(
        usuario_id=usuario_id,
        documento_id=documento_id,
        acao="AI_ANALYSIS",
        descricao=f"Análise direta concluída para {documento.get('nome_arquivo')} usando {provedor}.",
    )
    return resultado


@router.post("/analyze/{document_id}", response_model=AIResultResponse)
def analisar_documento_ai(document_id: str, usuario_id: str = Depends(get_current_user)):
    documento_ref = db.collection("documents").document(document_id)
    documento_snapshot = documento_ref.get()
    if not documento_snapshot.exists:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    documento = documento_snapshot.to_dict()
    if str(documento.get("usuario_id")) != str(usuario_id):
        raise HTTPException(status_code=404, detail="Documento não encontrado")

    try:
        resultado = analisar_documento(document_id=document_id)
        if not resultado["sucesso"]:
            raise HTTPException(status_code=400, detail=resultado["mensagem"])
        registrar_log_ai(
            usuario_id=usuario_id,
            documento_id=document_id,
            acao="AI_ANALYSIS",
            descricao=f"Análise de IA concluída para documento {documento.get('nome_arquivo')}",
        )
        return resultado["resultado"]
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Erro ao analisar documento: {str(error)}") from error


@router.get("/result/{document_id}", response_model=AIResultResponse)
def obter_resultado_ai(document_id: str, usuario_id: str = Depends(get_current_user)):
    documento_ref = db.collection("documents").document(document_id)
    documento_snapshot = documento_ref.get()
    if not documento_snapshot.exists:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    documento = documento_snapshot.to_dict()
    if str(documento.get("usuario_id")) != str(usuario_id):
        raise HTTPException(status_code=404, detail="Documento não encontrado")

    resultados = db.collection("ai_results").where("documento_id", "==", document_id).limit(1).stream()
    resultado_snapshot = next(resultados, None)
    if resultado_snapshot is None:
        raise HTTPException(status_code=404, detail="Ainda não existe uma análise de IA para este documento")
    resultado_ai = resultado_snapshot.to_dict()
    resultado_ai["id"] = resultado_snapshot.id
    return resultado_ai
