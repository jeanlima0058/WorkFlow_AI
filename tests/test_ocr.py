from app.ocr.ocr_service import extrair_texto_imagem


caminho = "uploads/teste_ocr.png"

texto = extrair_texto_imagem(caminho)

print("===== TEXTO EXTRAÍDO =====")
print(texto)