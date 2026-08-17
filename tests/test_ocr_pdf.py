from app.ocr.ocr_service import extrair_texto_pdf


caminho = "uploads/teste_ocr.pdf"

texto = extrair_texto_pdf(caminho)

print("===== TEXTO EXTRAÍDO DO PDF =====")
print(texto)