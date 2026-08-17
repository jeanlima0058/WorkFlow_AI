# DocFlow AI

Sistema para gerenciamento e processamento inteligente de documentos, desenvolvido com FastAPI, MySQL e recursos de Inteligência Artificial.

O projeto tem como objetivo permitir o envio, gerenciamento e processamento de documentos, utilizando OCR para extração de texto e, posteriormente, recursos de IA para análise das informações extraídas.

---

## Tecnologias utilizadas

### Back-end

- Python
- FastAPI
- SQLAlchemy
- MySQL
- PyMySQL
- Pydantic
- JWT
- Passlib
- Bcrypt

### OCR

- Tesseract OCR
- Pytesseract
- Pillow
- PyMuPDF

### Front-end

- HTML
- CSS
- JavaScript

### Versionamento

- Git
- Gitea

---

## Estrutura do projeto

```text
WorkFlow_AI/
│
├── app/
│   ├── models/
│   │   ├── ai_result.py
│   │   ├── document.py
│   │   ├── ocr_result.py
│   │   └── user.py
│   │
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── document.py
│   │   └── user.py
│   │
│   ├── routes/
│   │   ├── auth.py
│   │   └── documents.py
│   │
│   ├── services/
│   │   ├── auth_service.py
│   │   └── document_service.py
│   │
│   ├── utils/
│   │   └── security.py
│   │
│   ├── ocr/
│   │   └── ocr_service.py
│   │
│   ├── database.py
│   └── main.py
│
├── frontend/
│
├── tests/
│   ├── test_ocr.py
│   └── test_ocr_pdf.py
│
├── uploads/
│
├── requirements.txt
└── README.md