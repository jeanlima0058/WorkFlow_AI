# WorkFlow AI

## Sobre o Projeto

O WorkFlow AI é uma API desenvolvida para realizar o gerenciamento, processamento e preparação de documentos para análise por Inteligência Artificial.

O sistema permite que usuários façam upload de diferentes tipos de arquivos, armazena os documentos no servidor e no banco de dados e processa o conteúdo utilizando diferentes estratégias de extração.

Arquivos de imagem e documentos digitalizados podem passar por OCR, enquanto arquivos de texto, planilhas e arquivos estruturados são processados por extratores específicos.

O conteúdo extraído é armazenado no banco de dados e preparado para uma futura etapa de análise por Inteligência Artificial.

---

## Funcionalidades Implementadas

Atualmente, o sistema possui as seguintes funcionalidades:

- Cadastro de usuários;
- Login com autenticação JWT;
- Proteção de rotas por token;
- Consulta do usuário autenticado;
- Upload de documentos;
- Armazenamento de arquivos no servidor;
- Registro dos documentos no banco de dados;
- Listagem dos documentos do usuário;
- Consulta de documento específico;
- Exclusão do documento do banco e do armazenamento;
- Processamento de documentos;
- Extração de texto por OCR;
- Consulta de resultados já processados;
- Processamento de múltiplos formatos de arquivo.

---

## Formatos Suportados

O WorkFlow AI atualmente suporta os seguintes formatos:

| Formato | Extensões | Processamento |
|---|---|---|
| PDF | `.pdf` | OCR |
| Imagem | `.png`, `.jpg`, `.jpeg` | OCR |
| Texto | `.txt` | Leitura direta |
| CSV | `.csv` | Leitura tabular |
| Excel | `.xls`, `.xlsx`, `.xlsm` | Leitura de planilha |
| YAML | `.yaml`, `.yml` | Leitura estruturada |

### Processamento de Planilhas

Arquivos CSV e Excel têm seus dados convertidos para um formato textual estruturado.

O sistema identifica informações como:

- Nome das planilhas;
- Colunas;
- Quantidade de linhas;
- Dados presentes nas tabelas.

Arquivos Excel com múltiplas planilhas também são processados.

### Processamento de YAML

Arquivos YAML são convertidos para uma estrutura textual baseada em JSON, facilitando o processamento e a futura análise por Inteligência Artificial.

### Arquivos XLSM

Arquivos `.xlsm` têm os dados das planilhas processados.

As macros VBA não são executadas pelo sistema.

---

## Arquitetura do Sistema

```text
Usuário
   ↓
Autenticação
   ↓
Upload do Arquivo
   ↓
Armazenamento
   ↓
Banco de Dados
   ↓
Document Processor
   ↓
Identificação do Tipo de Arquivo
   ↓
┌─────────────┬─────────────────────────┐
│ PDF         │ OCR                     │
│ Imagem      │ OCR                     │
│ TXT         │ Leitura direta          │
│ CSV         │ Leitura tabular         │
│ XLS/XLSX    │ Leitura de planilha     │
│ XLSM        │ Leitura de planilha     │
│ YAML/YML    │ Leitura estruturada     │
└─────────────┴─────────────────────────┘
   ↓
Conteúdo Extraído
   ↓
OCR Results
   ↓
Preparação para Análise por IA




WorkFlow_AI/
│
├── app/
│   ├── models/
│   │   ├── user.py
│   │   ├── document.py
│   │   └── ocr_result.py
│   │
│   ├── routes/
│   │   ├── auth.py
│   │   ├── documents.py
│   │   └── ocr.py
│   │
│   ├── schemas/
│   │   ├── user.py
│   │   ├── auth.py
│   │   └── document.py
│   │
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── document_service.py
│   │   ├── document_processor.py
│   │   ├── text_extractor.py
│   │   ├── spreadsheet_extractor.py
│   │   └── yaml_extractor.py
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
├── tests/
├── requirements.txt
└── README.md