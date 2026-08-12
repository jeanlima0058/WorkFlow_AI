# WorkFlow AI

Sistema web para gerenciamento, processamento e análise inteligente de documentos utilizando Inteligência Artificial.

## Status do Projeto

Em desenvolvimento — Sprint 2 (MVP).

O projeto está sendo desenvolvido de forma modular, permitindo a expansão das funcionalidades de processamento de documentos, OCR e Inteligência Artificial.

---

## Objetivo

O WorkFlow AI tem como objetivo automatizar o fluxo de recebimento, processamento e análise de documentos.

O fluxo principal planejado é:

Usuário
↓
Autenticação
↓
Upload do documento
↓
Armazenamento
↓
OCR
↓
Extração do texto
↓
Inteligência Artificial
↓
Classificação e extração de informações
↓
Armazenamento dos resultados
↓
Apresentação ao usuário

---

## Tecnologias

### Backend

- Python
- FastAPI
- Uvicorn
- SQLAlchemy
- Pydantic

### Banco de Dados

- MySQL
- XAMPP
- phpMyAdmin
- PyMySQL

### Inteligência Artificial

A camada de Inteligência Artificial será implementada posteriormente, sendo responsável pela análise, classificação e extração de informações dos documentos.

### OCR

O módulo OCR será responsável pela extração de texto de documentos e imagens.

---

## Estrutura do Projeto

```text
WorkFlow_AI/
│
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── document.py
│   │   ├── ocr_result.py
│   │   └── ai_result.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── document.py
│   │   └── auth.py
│   │
│   ├── routes/
│   ├── services/
│   ├── utils/
│   ├── ai/
│   ├── ocr/
│   ├── storage/
│   └── reports/
│
├── uploads/
├── tests/
├── .gitignore
├── requirements.txt
└── README.md