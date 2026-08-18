## OCR

O sistema possui um módulo de OCR responsável por extrair texto de documentos enviados pelo usuário.

### Tecnologias utilizadas

- Tesseract OCR
- Pytesseract
- PyMuPDF
- Pillow

### Funcionamento

O fluxo de processamento é:

1. Usuário envia um documento;
2. O documento é armazenado;
3. A API identifica o tipo de arquivo;
4. O OCR processa o documento;
5. O texto é extraído;
6. O resultado é armazenado na tabela `ocr_results`;
7. O status do documento é atualizado.

O sistema atualmente suporta:

- PDF
- PNG
- JPG
- JPEG

### Endpoint

O processamento pode ser executado pela documentação Swagger:

`POST /ocr/process/{document_id}`

Exemplo de resposta:

```json
{
  "message": "OCR processado com sucesso",
  "documento_id": 1,
  "status": "CONCLUIDO",
  "texto_extraido": "Texto extraído do documento..."
}