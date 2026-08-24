import yaml
import json


def extrair_yaml(caminho_arquivo: str) -> str:

    with open(
        caminho_arquivo,
        "r",
        encoding="utf-8"
    ) as arquivo:

        dados = yaml.safe_load(arquivo)

    if dados is None:
        return ""

    return json.dumps(
        dados,
        ensure_ascii=False,
        indent=2,
        default=str
    )