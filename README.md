# Docflow AI

# DocFlow AI

## Automação Inteligente de Recepção e Processamento de Documentos

O **DocFlow AI** é uma API desenvolvida para automatizar a recepção, armazenamento, processamento e análise inteligente de documentos.

O sistema recebe diferentes tipos de arquivos, identifica o conteúdo disponível, realiza a extração de informações por meio de OCR ou processadores específicos e prepara os dados para análise por Inteligência Artificial.

O projeto está sendo desenvolvido como uma esteira de processamento de documentos, permitindo que um arquivo passe por diferentes etapas até que seu conteúdo esteja disponível para análise e futura automação.

---

# Funcionalidades

Atualmente, o sistema possui as seguintes funcionalidades:

- Autenticação de usuários;
- Upload de documentos;
- Armazenamento dos arquivos no servidor;
- Registro dos documentos no banco de dados;
- Listagem de documentos por usuário;
- Consulta de documentos específicos;
- Exclusão de documentos e arquivos físicos;
- Processamento de documentos;
- Extração de texto utilizando OCR;
- Processamento de diferentes tipos de arquivos;
- Armazenamento do resultado do OCR;
- Consulta do conteúdo extraído;
- Estrutura inicial para análise por Inteligência Artificial;
- Armazenamento do resultado da análise de IA.

---

# Fluxo do Sistema

```text
Usuário
   │
   ▼
Upload do Arquivo
   │
   ▼
Banco de Dados
   │
   ▼
Armazenamento do Arquivo
   │
   ▼
Processamento do Documento
   │
   ├── PDF
   ├── Imagem
   ├── TXT
   ├── CSV
   ├── XLS / XLSX / XLSM
   ├── YAML / YML
   └── Outros formatos suportados
   │
   ▼
Extração do Conteúdo
   │
   ▼
OCRResult
   │
   ▼
Análise por IA
   │
   ▼
AIResult
   │
   ▼
Classificação e Informações Estruturadas



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
│   ├── routes/
│   │   ├── auth.py
│   │   ├── documents.py
│   │   ├── ocr.py
│   │   └── ai.py
│   │
│   ├── schemas/
│   │   ├── document.py
│   │   └── ai_result.py
│   │
│   ├── services/
│   │   ├── document_service.py
│   │   ├── document_processor.py
│   │   └── ai_service.py
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
├── uploads/
│
├── tests/
│
├── requirements.txt
├── README.md