import os
import json
from datetime import datetime, timezone

from dotenv import load_dotenv
from google import genai

from app.firebase_config import db


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

def analisar_documento(document_id: str):
    # ==================================================
    # BUSCA O DOCUMENTO NO FIRESTORE
    # ==================================================

    documento_ref = db.collection("documents").document(document_id)
    documento_snapshot = documento_ref.get()

    if not documento_snapshot.exists:
        return {
            "sucesso": False,
            "mensagem": "Documento não encontrado"
        }

    documento = documento_snapshot.to_dict()


    # ==================================================
    # BUSCA O RESULTADO DO PROCESSAMENTO/OCR NO FIRESTORE
    # ==================================================

    ocr_query = (
        db.collection("ocr_results")
        .where("documento_id", "==", document_id)
        .limit(1)
        .stream()
    )

    ocr_snapshot = next(ocr_query, None)

    if not ocr_snapshot:
        return {
            "sucesso": False,
            "mensagem": "O documento ainda não foi processado"
        }

    resultado_ocr = ocr_snapshot.to_dict()


    # ==================================================
    # VERIFICA SE EXISTE CONTEÚDO PARA ANALISAR
    # ==================================================

    if not resultado_ocr.get("texto_extraido"):
        return {
            "sucesso": False,
            "mensagem": "Não foi possível obter conteúdo para análise"
        }

    # Texto extraído do documento
    texto = resultado_ocr["texto_extraido"]


    # ==================================================
    # ANÁLISE COM GEMINI
    # ==================================================

    try:

        # Limita inicialmente a quantidade de caracteres
        # enviados para a IA.
        texto_para_analise = texto[:20000]


        # Prompt enviado para o Gemini
        prompt = f"""
Você é uma inteligência artificial especializada em análise inteligente de documentos.

Sua tarefa é ler o conteúdo completo do documento e transformar as informações encontradas em uma análise clara, objetiva e útil para o usuário.

O objetivo NÃO é apenas resumir o texto.

Você deve:
- identificar o tipo do documento;
- identificar sua categoria;
- produzir um resumo executivo;
- extrair os dados mais importantes;
- identificar padrões e informações relevantes;
- produzir insights baseados nos dados;
- apresentar recomendações quando forem justificadas;
- identificar riscos, problemas ou inconsistências;
- preservar os dados originais;
- não inventar informações.

REGRAS FUNDAMENTAIS:

1. Utilize SOMENTE informações presentes no documento.

2. NÃO invente nomes, valores, datas, números, resultados ou acontecimentos.

3. NÃO transforme uma possibilidade em um fato.

Exemplo:

Se o documento disser:
"Os resultados podem estar relacionados ao aumento de preços."

Você deve escrever:
"Possível relação entre os resultados e o aumento de preços, conforme indicado no documento."

NÃO escreva:
"O aumento de preços causou os resultados."

4. Diferencie:
- fatos encontrados no documento;
- interpretações baseadas nos dados;
- possibilidades mencionadas pelo documento;
- recomendações sugeridas pela análise.

5. Quando houver valores, percentuais, datas ou quantidades, preserve os valores encontrados no documento.

6. Quando for possível realizar uma comparação matemática utilizando dados presentes no documento, faça a comparação.

7. Não crie informações apenas para preencher os campos.

8. Se não houver informação suficiente para determinado campo, informe:
"Não identificado no documento."

RETORNE EXCLUSIVAMENTE UM JSON VÁLIDO.

NÃO utilize Markdown.

NÃO utilize ```json.

NÃO escreva explicações antes ou depois do JSON.

UTILIZE EXATAMENTE ESTA ESTRUTURA:

{{
    "tipo_documento": "tipo identificado",
    "categoria": "categoria ou área do documento",

    "resumo": "resumo executivo do documento, permitindo compreender seu conteúdo principal sem precisar ler o documento inteiro",

    "informacoes_principais": "principais dados objetivos encontrados no documento, incluindo nomes, datas, valores, quantidades, períodos, resultados, indicadores, produtos, serviços, responsáveis e outros dados relevantes",

    "insights": "interpretações e conclusões relevantes obtidas a partir das informações do documento. Utilize dados do documento para justificar os insights",

    "recomendacoes": "ações ou recomendações que podem ser consideradas com base nas informações e insights. Não invente recomendações que dependam de informações ausentes",

    "palavras_chave": "palavras-chave mais importantes separadas por vírgula",

    "alertas": "problemas, riscos, inconsistências ou pontos de atenção identificados. Se não houver nenhum, informe: Nenhum alerta identificado",

    "confianca": 0.0
}}

ORIENTAÇÕES ESPECÍFICAS:

RELATÓRIO DE VENDAS:
Analise:
- período;
- faturamento;
- meta;
- atingimento da meta;
- crescimento ou queda;
- comparação com períodos anteriores;
- quantidade vendida;
- produtos ou serviços;
- melhor desempenho;
- pior desempenho;
- maiores crescimentos;
- maiores quedas;
- concentração de receita;
- oportunidades;
- pontos de atenção.

RELATÓRIO FINANCEIRO:
Analise:
- período;
- receitas;
- despesas;
- saldo;
- resultado;
- indicadores;
- variações;
- maiores despesas;
- maiores receitas;
- pontos de atenção.

CONTRATO:
Analise:
- partes envolvidas;
- objeto;
- vigência;
- valores;
- obrigações;
- responsabilidades;
- prazos;
- multas;
- condições;
- riscos;
- pontos que merecem atenção.

CURRÍCULO:
Analise:
- nome;
- formação;
- experiência;
- cargos;
- habilidades;
- tecnologias;
- idiomas;
- certificações;
- tempo de experiência.

NOTA FISCAL:
Analise:
- número;
- data;
- fornecedor;
- cliente;
- produtos;
- serviços;
- quantidades;
- valores;
- impostos;
- valor total.

ORÇAMENTO OU PROPOSTA:
Analise:
- empresa;
- cliente;
- produtos;
- serviços;
- quantidades;
- valores;
- descontos;
- prazos;
- validade;
- condições de pagamento;
- observações.

ATA DE REUNIÃO:
Analise:
- data;
- participantes;
- assuntos discutidos;
- decisões;
- responsáveis;
- tarefas;
- prazos;
- pendências.

DOCUMENTOS TÉCNICOS:
Analise:
- objetivo;
- especificações;
- componentes;
- requisitos;
- parâmetros;
- resultados;
- problemas;
- limitações;
- conclusões.

PARA OUTROS DOCUMENTOS:

Identifique automaticamente os dados mais importantes de acordo com o conteúdo encontrado.

ANÁLISE DOS INSIGHTS:

Os insights devem responder perguntas como:

- O que mais chama atenção neste documento?
- Qual foi o principal resultado?
- Existe alguma tendência?
- Existe alguma concentração?
- Existe alguma queda ou crescimento relevante?
- Existe algum desempenho acima ou abaixo do esperado?
- Existe alguma relação importante entre os dados?
- Qual informação pode ajudar na tomada de decisão?

Não crie insights sem evidência no documento.

ANÁLISE DAS RECOMENDAÇÕES:

As recomendações devem ser práticas e estar relacionadas aos problemas ou oportunidades encontrados.

Se não houver informação suficiente para recomendar uma ação específica:

"Não foi possível identificar uma recomendação específica com base no documento."

ANÁLISE DOS ALERTAS:

Inclua somente problemas, riscos ou inconsistências sustentados pelas informações do documento.

Não transforme hipóteses em fatos.

CONFIANÇA:

O campo "confianca" deve ser um número entre 0.0 e 1.0.

Utilize confiança maior quando:
- o documento estiver claro;
- os dados estiverem completos;
- o tipo do documento for evidente;
- as informações forem consistentes.

Utilize confiança menor quando:
- o OCR estiver incompleto;
- existirem informações ambíguas;
- houver partes ilegíveis;
- não for possível identificar claramente o tipo do documento.

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
            ),

            "insights": analise.get(
                "insights",
                "Não identificado no documento"
            ),

            "recomendacoes": analise.get(
                "recomendacoes",
                "Não foi possível identificar uma recomendação específica com base no documento."
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
    # SALVA OU ATUALIZA A ANÁLISE NO FIRESTORE
    # ==================================================

    analise_ref = (
        db.collection("ai_results")
        .where("documento_id", "==", document_id)
        .limit(1)
        .stream()
    )

    analise_existente = next(analise_ref, None)
    agora = datetime.now(timezone.utc)

    dados_analise = {
        "documento_id": document_id,
        "tipo_documento": analise_formatada["tipo_documento"],
        "categoria": analise_formatada["categoria"],
        "resumo": analise_formatada["resumo"],
        "informacoes_principais": analise_formatada[
            "informacoes_principais"
        ],
        "insights": analise_formatada["insights"],
        "recomendacoes": analise_formatada["recomendacoes"],
        "palavras_chave": analise_formatada["palavras_chave"],
        "alertas": analise_formatada["alertas"],
        "confianca": analise_formatada["confianca"],
        "status": "CONCLUIDO",
        "data_processamento": agora
    }

    if analise_existente:
        resultado_ref = analise_existente.reference
        resultado_ref.update(dados_analise)
        resultado_id = analise_existente.id
    else:
        resultado_ref = db.collection("ai_results").document()
        dados_analise["id"] = resultado_ref.id
        resultado_ref.set(dados_analise)
        resultado_id = resultado_ref.id


    # ==================================================
    # ATUALIZA O STATUS DO DOCUMENTO NO FIRESTORE
    # ==================================================

    documento_ref.update({
        "status": "ANALISADO"
    })


    # ==================================================
    # RETORNO FINAL DA ANÁLISE
    # ==================================================

    return {
        "sucesso": True,
        "mensagem": "Documento analisado com sucesso pelo Gemini",
        "resultado": {
            "id": resultado_id,
            **dados_analise
        }
    }