
import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

PROMPT_BASE = """
Você é uma IA especializada em análise de documentos. Leia o arquivo enviado diretamente e produza uma análise fiel ao seu conteúdo.

Regras:
- Use somente informações presentes no documento.
- Não invente nomes, números, datas, valores ou acontecimentos.
- Diferencie fatos de interpretações e recomendações.
- Preserve valores e unidades como aparecem no documento.
- Quando uma informação não existir ou estiver ilegível, informe isso claramente.
- Considere também a instrução personalizada do usuário, sem ignorar as regras acima.

Retorne exclusivamente um JSON válido com esta estrutura e todos estes campos:
{
  "tipo_documento": "",
  "categoria": "",
  "resumo": "",
  "informacoes_principais": "",
  "insights": "",
  "recomendacoes": "",
  "palavras_chave": "",
  "alertas": "",
  "confianca": 0.0
}
O campo confianca deve ser um número entre 0 e 1.
""".strip()


def _mime_por_extensao(extensao: str) -> str:
    mimes = {
        ".pdf": "application/pdf",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".bmp": "image/bmp",
        ".gif": "image/gif",
        ".txt": "text/plain",
        ".csv": "text/csv",
        ".yaml": "text/plain",
        ".yml": "text/plain",
    }
    return mimes.get(extensao.lower(), "")


def _codigo_erro(erro: Exception):
    """Obtém o código HTTP do erro, quando disponível."""
    codigo = getattr(erro, "code", None)
    if codigo is None:
        codigo = getattr(erro, "status_code", None)

    try:
        return int(codigo)
    except (TypeError, ValueError):
        return None


def _gerar_com_tentativas(client, modelo, contents):
    """Tenta novamente em erros temporários de disponibilidade."""
    max_tentativas = 4
    ultimo_erro = None

    for tentativa in range(max_tentativas):
        try:
            return client.models.generate_content(
                model=modelo,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                ),
            )
        except Exception as erro:
            ultimo_erro = erro
            codigo = _codigo_erro(erro)

            # Só repetir erros temporários.
            if codigo not in (429, 500, 502, 503, 504):
                raise

            if tentativa < max_tentativas - 1:
                espera = 2 ** tentativa
                time.sleep(espera)

    raise ultimo_erro


def analisar_arquivo_gemini(
    conteudo: bytes,
    nome_arquivo: str,
    instrucao: str = "",
    provedor: str = "gemini",
) -> dict:
    """Envia o documento diretamente ao Gemini e devolve a análise estruturada."""

    provedor = (provedor or "gemini").strip().lower()
    if provedor != "gemini":
        raise NotImplementedError(
            f"O provedor '{provedor}' ainda não está integrado. Por enquanto, use Gemini."
        )

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "A variável GEMINI_API_KEY não está configurada no Render."
        )

    extensao = Path(nome_arquivo or "").suffix.lower()
    mime_type = _mime_por_extensao(extensao)

    if not mime_type:
        raise ValueError(
            "Formato ainda não compatível. Use PDF, PNG, JPG, JPEG, WEBP, BMP, GIF, TXT, CSV ou YAML."
        )

    instrucao = (instrucao or "").strip()
    prompt = PROMPT_BASE

    if instrucao:
        prompt += f"\n\nINSTRUÇÃO PERSONALIZADA DO USUÁRIO:\n{instrucao}"
    else:
        prompt += "\n\nFaça uma análise geral e completa do documento."

    if mime_type.startswith("text/"):
        try:
            texto = conteudo.decode("utf-8-sig")
        except UnicodeDecodeError:
            texto = conteudo.decode("latin-1")

        if len(texto) > 60000:
            texto = texto[:60000] + "\n\n[Conteúdo truncado pelo limite de análise.]"

        contents = [
            prompt,
            f"CONTEÚDO DO DOCUMENTO ({nome_arquivo}):\n\n{texto}",
        ]
    else:
        contents = [
            prompt,
            types.Part.from_bytes(
                data=conteudo,
                mime_type=mime_type,
            ),
        ]

    client = genai.Client(api_key=api_key)

    modelo_principal = os.getenv(
        "GEMINI_MODEL",
        "gemini-3.6-flash",
    ).strip()

    modelo_alternativo = os.getenv(
        "GEMINI_FALLBACK_MODEL",
        "",
    ).strip()

    modelos = [modelo_principal]

    if modelo_alternativo and modelo_alternativo != modelo_principal:
        modelos.append(modelo_alternativo)

    ultimo_erro = None
    response = None

    for modelo in modelos:
        try:
            response = _gerar_com_tentativas(
                client,
                modelo,
                contents,
            )
            break
        except Exception as erro:
            ultimo_erro = erro

            # Só tentar o modelo alternativo em falhas temporárias.
            if _codigo_erro(erro) not in (429, 500, 502, 503, 504):
                raise RuntimeError(
                    f"Falha na análise com Gemini: {erro}"
                ) from erro

    if response is None:
        raise RuntimeError(
            "Os modelos Gemini configurados estão temporariamente "
            "indisponíveis. Aguarde alguns instantes e tente novamente."
        ) from ultimo_erro

    resposta = (response.text or "").strip()

    if not resposta:
        raise RuntimeError(
            "O Gemini não retornou conteúdo para análise."
        )

    try:
        analise = json.loads(resposta)
    except json.JSONDecodeError as erro:
        raise RuntimeError(
            "O Gemini retornou uma resposta que não é um JSON válido."
        ) from erro

    campos_texto = [
        "tipo_documento",
        "categoria",
        "resumo",
        "informacoes_principais",
        "insights",
        "recomendacoes",
        "palavras_chave",
        "alertas",
    ]

    resultado = {
        campo: str(
            analise.get(campo) or "Não identificado no documento."
        )
        for campo in campos_texto
    }

    try:
        confianca = float(analise.get("confianca", 0))
    except (TypeError, ValueError):
        confianca = 0.0

    resultado["confianca"] = max(
        0.0,
        min(1.0, confianca),
    )

    return resultado