def extrair_texto_txt(caminho_arquivo: str) -> str:
    encodings = [
        "utf-8",
        "utf-8-sig",
        "latin-1",
        "cp1252"
    ]

    for encoding in encodings:
        try:
            with open(
                caminho_arquivo,
                "r",
                encoding=encoding
            ) as arquivo:

                texto = arquivo.read()

                return texto.strip()

        except UnicodeDecodeError:
            continue

    raise ValueError(
        "Não foi possível identificar a codificação do arquivo TXT"
    )