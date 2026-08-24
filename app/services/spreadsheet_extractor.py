import pandas as pd
import os


def extrair_planilha(caminho_arquivo: str) -> str:
    extensao = os.path.splitext(caminho_arquivo)[1].lower()

    textos = []

    if extensao == ".csv":
        try:
            dataframe = pd.read_csv(caminho_arquivo)
        except UnicodeDecodeError:
            dataframe = pd.read_csv(
                caminho_arquivo,
                encoding="latin-1"
            )

        textos.append(
            f"ARQUIVO CSV: {os.path.basename(caminho_arquivo)}"
        )

        textos.append(
            f"COLUNAS: {', '.join(map(str, dataframe.columns))}"
        )

        textos.append(
            f"TOTAL DE LINHAS: {len(dataframe)}"
        )

        textos.append("DADOS:")

        textos.append(
            dataframe.to_string(index=False)
        )

    elif extensao in [".xls", ".xlsx", ".xlsm"]:

        planilhas = pd.read_excel(
            caminho_arquivo,
            sheet_name=None
        )

        textos.append(
            f"ARQUIVO EXCEL: {os.path.basename(caminho_arquivo)}"
        )

        textos.append(
            f"TOTAL DE PLANILHAS: {len(planilhas)}"
        )

        for nome_planilha, dataframe in planilhas.items():

            textos.append(
                f"\n--- PLANILHA: {nome_planilha} ---"
            )

            textos.append(
                f"COLUNAS: {', '.join(map(str, dataframe.columns))}"
            )

            textos.append(
                f"TOTAL DE LINHAS: {len(dataframe)}"
            )

            textos.append("DADOS:")

            textos.append(
                dataframe.to_string(index=False)
            )

    else:
        raise ValueError(
            "Formato de planilha não suportado"
        )

    return "\n".join(textos)