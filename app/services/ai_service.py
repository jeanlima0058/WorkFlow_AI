import os
import json
from datetime import datetime

from dotenv import load_dotenv
from google import genai
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.ocr_result import OCRResult
from app.models.ai_result import AIResult


# ==================================================
# CONFIGURAÇÃO DO GEMINI
# ==================================================

# Carrega as variáveis do arquivo .env
load_dotenv()

# Obtém a chave da API
api_key = os.getenv("GEMINI_API_KEY")

# Verifica se a chave foi encontrada
if not api_key:
    raise ValueError(
        "A variável GEMINI_API_KEY não foi encontrada no arquivo .env"
    )


# Cria o cliente do Gemini
client = genai.Client(
    api_key=api_key
)


# ==================================================
# FUNÇÃO PRINCIPAL DE ANÁLISE
# ==================================================

def analisar_documento(
    db: Session,
    document_id: int
):
    # ==================================================
    # BUSCA O DOCUMENTO
    # ==================================================

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


    # ==================================================
    # BUSCA O RESULTADO DO PROCESSAMENTO/OCR
    # ==================================================

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


    # ==================================================
    # VERIFICA SE EXISTE CONTEÚDO PARA ANALISAR
    # ==================================================

    if not resultado_ocr.texto_extraido:
        return {
            "sucesso": False,
            "mensagem": (
                "Não foi possível obter conteúdo para análise"
            )
        }


    # Texto extraído do documento
    texto = resultado_ocr.texto_extraido


    # ==================================================
    # ANÁLISE COM GEMINI
    # ==================================================

    try:

        # Limita inicialmente a quantidade de caracteres
        # enviados para a IA.
        #
        # Posteriormente podemos melhorar isso para analisar
        # documentos muito grandes em partes.
        texto_para_analise = texto[:20000]


        # Prompt enviado para o Gemini
        prompt = f"""
Você é uma inteligência artificial especializada em análise de documentos.

Analise o conteúdo do documento fornecido abaixo.

Sua função é identificar, organizar e resumir as informações mais
importantes presentes no documento.

Retorne EXCLUSIVAMENTE um JSON válido.

NÃO utilize markdown.
NÃO utilize explicações antes ou depois do JSON.
NÃO utilize ```json.
NÃO invente informações que não estejam presentes no documento.

Utilize exatamente esta estrutura:

{{
    "tipo_documento": "tipo identificado do documento",
    "categoria": "categoria ou área do documento",
    "resumo": "resumo claro e objetivo do conteúdo",
    "informacoes_principais": "principais informações encontradas",
    "palavras_chave": "palavras-chave separadas por vírgula",
    "alertas": "problemas, riscos, inconsistências ou nenhum alerta identificado",
    "confianca": 0.0
}}

REGRAS:

- Identifique o tipo real do documento sempre que possível.
- A categoria deve representar a área ou finalidade do documento.
- O resumo deve ser claro e objetivo.
- Extraia as principais informações realmente presentes no conteúdo.
- Identifique possíveis riscos, problemas ou inconsistências.
- Se não existir nenhum alerta, informe: Nenhum alerta identificado.
- O campo confianca deve ser um número entre 0.0 e 1.0.
- Não invente dados.
- Se alguma informação não puder ser identificada, informe isso no
  respectivo campo.

CONTEÚDO DO DOCUMENTO:

{texto_para_analise}
"""


        # ==================================================
        # ENVIA O CONTEÚDO PARA O GEMINI
        # ==================================================

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )


        # Obtém a resposta da IA
        resposta_texto = response.text.strip()


        # ==================================================
        # CONVERTE A RESPOSTA JSON EM DICIONÁRIO PYTHON
        # ==================================================

        analise = json.loads(
            resposta_texto
        )


        # ==================================================
        # ORGANIZA E VALIDA OS CAMPOS RETORNADOS
        # ==================================================

        analise_formatada = {

            "tipo_documento": analise.get(
                "tipo_documento",
                "Não identificado"
            ),

            "categoria": analise.get(
                "categoria",
                "Geral"
            ),

            "resumo": analise.get(
                "resumo",
                "Resumo não disponível"
            ),

            "informacoes_principais": analise.get(
                "informacoes_principais",
                "Informações não identificadas"
            ),

            "palavras_chave": analise.get(
                "palavras_chave",
                ""
            ),

            "alertas": analise.get(
                "alertas",
                "Nenhum alerta identificado"
            ),

            "confianca": analise.get(
                "confianca",
                0.0
            )
        }


        # ==================================================
        # GARANTE QUE A CONFIANÇA SEJA UM NÚMERO
        # ==================================================

        try:

            analise_formatada["confianca"] = float(
                analise_formatada["confianca"]
            )

        except (ValueError, TypeError):

            analise_formatada["confianca"] = 0.0


        # ==================================================
        # GARANTE QUE A CONFIANÇA FIQUE ENTRE 0 E 1
        # ==================================================

        analise_formatada["confianca"] = max(
            0.0,
            min(
                1.0,
                analise_formatada["confianca"]
            )
        )


    # ==================================================
    # ERRO CASO A IA NÃO RETORNE UM JSON VÁLIDO
    # ==================================================

    except json.JSONDecodeError:

        return {
            "sucesso": False,
            "mensagem": (
                "A IA retornou uma resposta em formato inválido"
            )
        }


    # ==================================================
    # OUTROS ERROS DURANTE A ANÁLISE
    # ==================================================

    except Exception as error:

        return {
            "sucesso": False,
            "mensagem": (
                f"Erro ao analisar documento com Gemini: {str(error)}"
            )
        }


    # ==================================================
    # VERIFICA SE JÁ EXISTE UMA ANÁLISE NO BANCO
    # ==================================================

    resultado_ai = (
        db.query(AIResult)
        .filter(AIResult.documento_id == document_id)
        .first()
    )


    # ==================================================
    # ATUALIZA UMA ANÁLISE EXISTENTE
    # ==================================================

    if resultado_ai:

        resultado_ai.tipo_documento = (
            analise_formatada["tipo_documento"]
        )

        resultado_ai.categoria = (
            analise_formatada["categoria"]
        )

        resultado_ai.resumo = (
            analise_formatada["resumo"]
        )

        resultado_ai.informacoes_principais = (
            analise_formatada["informacoes_principais"]
        )

        resultado_ai.palavras_chave = (
            analise_formatada["palavras_chave"]
        )

        resultado_ai.alertas = (
            analise_formatada["alertas"]
        )

        resultado_ai.confianca = (
            analise_formatada["confianca"]
        )

        resultado_ai.status = "CONCLUIDO"

        resultado_ai.data_processamento = (
            datetime.now()
        )


    # ==================================================
    # CRIA UMA NOVA ANÁLISE
    # ==================================================

    else:

        resultado_ai = AIResult(

            documento_id=document_id,

            tipo_documento=(
                analise_formatada["tipo_documento"]
            ),

            categoria=(
                analise_formatada["categoria"]
            ),

            resumo=(
                analise_formatada["resumo"]
            ),

            informacoes_principais=(
                analise_formatada[
                    "informacoes_principais"
                ]
            ),

            palavras_chave=(
                analise_formatada["palavras_chave"]
            ),

            alertas=(
                analise_formatada["alertas"]
            ),

            confianca=(
                analise_formatada["confianca"]
            ),

            status="CONCLUIDO",

            data_processamento=(
                datetime.now()
            )
        )

        # Adiciona a análise ao banco
        db.add(resultado_ai)


    # ==================================================
    # ATUALIZA O STATUS DO DOCUMENTO
    # ==================================================

    documento.status = "ANALISADO"


    # ==================================================
    # SALVA AS ALTERAÇÕES
    # ==================================================

    db.commit()

    db.refresh(resultado_ai)


    # ==================================================
    # RETORNO DA ANÁLISE
    # ==================================================

    return {

        "sucesso": True,

        "mensagem": (
            "Documento analisado com sucesso pelo Gemini"
        ),

        "resultado": resultado_ai
    }
