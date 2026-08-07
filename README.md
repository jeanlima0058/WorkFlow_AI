# WorkFlow AI

Sistema web para automação e processamento inteligente de documentos utilizando Inteligência Artificial.

## Sobre o projeto

O WorkFlow AI tem como objetivo automatizar o processo de recebimento, organização, processamento e análise de documentos.

A aplicação será desenvolvida para reduzir tarefas manuais, melhorar a organização dos documentos e utilizar recursos de Inteligência Artificial para auxiliar na classificação e extração de informações.

## Objetivos

- Automatizar o recebimento de documentos;
- Organizar documentos de forma estruturada;
- Realizar processamento automático de arquivos;
- Utilizar OCR para extração de texto;
- Utilizar Inteligência Artificial para classificação e análise;
- Armazenar informações em banco de dados;
- Disponibilizar informações por meio de uma API;
- Gerar indicadores e relatórios.

## Tecnologias

### Backend

- Python
- FastAPI
- Uvicorn
- SQLAlchemy
- PostgreSQL

### Inteligência Artificial

- OpenAI API
- Bibliotecas de processamento de documentos
- OCR

### Frontend

- React
- JavaScript / TypeScript

## Estrutura do projeto

```text
WorkFlow_AI/
│
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   │
│   ├── models/
│   ├── schemas/
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
├── .env
├── .gitignore
├── requirements.txt
└── README.md