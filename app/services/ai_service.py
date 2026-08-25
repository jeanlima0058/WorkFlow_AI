from datetime import datetime

from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.ocr_result import OCRResult
from app.models.ai_result import AIResult


def analisar_documento(
    db: Session,
    document_id: int
):
    # Busca o documento
    documento = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if not documento:
        return {
            "sucesso": False,
            "mensagem": "Documento não encontrado"
        }

    # Busca o resultado do processamento/OCR
    resultado_ocr = (
        db.query(OCRResult)
        .filter(OCRResult.documento_id == document_id)
        .first()
    )

    if not resultado_ocr:
        return {
            "sucesso": False,
            "mensagem": "O documento ainda não foi processado"
        }

    if not resultado_ocr.texto_extraido:
        return {
            "sucesso": False,
            "mensagem": "Não foi possível obter conteúdo para análise"
        }

    texto = resultado_ocr.texto_extraido

    # ==================================================
    # ANÁLISE SIMULADA
    # Futuramente esta parte será substituída pelo Gemini
    # ==================================================

    analise = {
        "tipo_documento": "Documento não identificado",
        "categoria": "Geral",
        "resumo": texto[:500],
        "informacoes_principais": (
            "Análise inicial do conteúdo extraído do documento."
        ),
        "palavras_chave": "documento, análise, processamento",
        "alertas": "Nenhum alerta identificado",
        "confianca": 0.80
    }

    # Verifica se já existe análise para o documento
    resultado_ai = (
        db.query(AIResult)
        .filter(AIResult.documento_id == document_id)
        .first()
    )

    # Atualiza uma análise existente
    if resultado_ai:

        resultado_ai.tipo_documento = analise["tipo_documento"]
        resultado_ai.categoria = analise["categoria"]
        resultado_ai.resumo = analise["resumo"]
        resultado_ai.informacoes_principais = (
            analise["informacoes_principais"]
        )
        resultado_ai.palavras_chave = analise["palavras_chave"]
        resultado_ai.alertas = analise["alertas"]
        resultado_ai.confianca = analise["confianca"]
        resultado_ai.status = "CONCLUIDO"
        resultado_ai.data_processamento = datetime.now()

    # Cria uma nova análise
    else:

        resultado_ai = AIResult(
            documento_id=document_id,
            tipo_documento=analise["tipo_documento"],
            categoria=analise["categoria"],
            resumo=analise["resumo"],
            informacoes_principais=(
                analise["informacoes_principais"]
            ),
            palavras_chave=analise["palavras_chave"],
            alertas=analise["alertas"],
            confianca=analise["confianca"],
            status="CONCLUIDO",
            data_processamento=datetime.now()
        )

        db.add(resultado_ai)

    db.commit()
    db.refresh(resultado_ai)

    return {
        "sucesso": True,
        "mensagem": "Análise realizada com sucesso",
        "resultado": resultado_ai
    }