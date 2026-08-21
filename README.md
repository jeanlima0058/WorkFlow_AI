# WorkFlow AI

## Sobre o Projeto

O **WorkFlow AI** é um sistema desenvolvido para receber, armazenar, processar e extrair conteúdos de documentos enviados pelos usuários.

O projeto utiliza uma API desenvolvida em **FastAPI**, banco de dados **MySQL** e uma arquitetura preparada para diferentes tipos de arquivos.

O conteúdo extraído dos documentos é armazenado no banco de dados e será utilizado futuramente por uma camada de **Inteligência Artificial**, responsável por analisar e interpretar as informações dos arquivos.

---

# Funcionalidades Implementadas

Atualmente, o sistema possui as seguintes funcionalidades:

- Cadastro de usuários
- Autenticação de usuários
- Login com geração de token JWT
- Proteção de rotas autenticadas
- Identificação do usuário logado
- Upload de documentos
- Armazenamento físico dos arquivos
- Registro dos documentos no banco de dados
- Listagem de documentos por usuário
- Visualização de documento específico
- Exclusão de documentos
- Exclusão física do arquivo armazenado
- Processamento de documentos
- Extração de texto
- Armazenamento do resultado do processamento
- Controle de status dos documentos
- Suporte a diferentes formatos de arquivos

---

# Formatos Atualmente Suportados

## PDF

Arquivos PDF podem ser processados para extração de conteúdo.

Quando necessário, o sistema utiliza OCR para identificar textos presentes no documento.

## Imagens

Atualmente são suportadas imagens nos formatos:

- `.png`
- `.jpg`
- `.jpeg`

As imagens são processadas utilizando OCR através do **Tesseract**.

## Arquivos TXT

Arquivos `.txt` são processados através da leitura direta do conteúdo.

Para evitar problemas de codificação, o sistema tenta diferentes encodings:

- UTF-8
- UTF-8-SIG
- Latin-1
- CP1252

---

# Fluxo de Processamento

O fluxo atual do sistema funciona da seguinte forma:

```text
Usuário
   │
   ▼
Autenticação
   │
   ▼
Upload do Documento
   │
   ▼
Armazenamento do Arquivo
   │
   ▼
Registro no Banco de Dados
   │
   ▼
Processamento do Documento
   │
   ├── PDF
   │
   ├── Imagem
   │
   └── TXT
   │
   ▼
Extração do Conteúdo
   │
   ▼
Armazenamento em OCR Results
   │
   ▼
Futura Análise por Inteligência Artificial





Arquitetura do Projeto

WorkFlow_AI/
│
├── app/
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── document.py
│   │   ├── ocr_result.py
│   │   └── ai_result.py
│   │
│   ├── schemas/
│   │   ├── user.py
│   │   ├── auth.py
│   │   └── document.py
│   │
│   ├── routes/
│   │   ├── auth.py
│   │   ├── documents.py
│   │   └── ocr.py
│   │
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── document_service.py
│   │   ├── document_processor.py
│   │   └── text_extractor.py
│   │
│   ├── ocr/
│   │   └── ocr_service.py
│   │
│   ├── utils/
│   │   └── security.py
│   │
│   ├── database.py
│   └── main.py
│
├── frontend/
│
├── uploads/
│
├── tests/
│
├── requirements.txt
└── README.md