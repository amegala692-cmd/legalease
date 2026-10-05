# LegalEase — AI-Powered Legal Document Generator

LegalEase is a full-stack reference implementation based on the supplied project document. It uses a **Streamlit frontend**, **FastAPI backend**, and **Google Gemini** generation service, with editable previews and **TXT / DOCX / PDF** export.

The supplied specification calls for Gemini 1.5 Pro and the legacy `google-generativeai` SDK. This implementation keeps the Gemini architecture but uses Google's current **Google GenAI SDK (`google-genai`)** and makes the model configurable through `GEMINI_MODEL`, defaulting to `gemini-3.8-flash`.

## Features

- Legal document drafting from document type, parties, terms, dates, jurisdiction, language, and extra instructions.
- Built-in templates for employment, NDA, lease, service, freelance, general, and custom documents.
- Editable document preview in Streamlit.
- Plain-language explanation endpoint for generated drafts.
- Branded export to TXT, DOCX, and PDF.
- Logo upload and footer branding for DOCX/PDF exports.
- Automatic key-terms table in DOCX.
- Demo mode so the UI can be tested without a Gemini key.
- FastAPI Swagger/OpenAPI docs.
- Basic automated tests for health, generation, and exports.
- Dockerfile and Procfile included.

## Project structure

```text
LegalEase_project/
├── backend/
│   ├── ai_core/
│   │   └── gemini_generator.py
│   ├── utils/
│   │   ├── demo_documents.py
│   │   ├── exporters.py
│   │   └── text_utils.py
│   ├── config.py
│   ├── main.py
│   ├── routes.py
│   └── schemas.py
├── frontend/
│   └── app.py
├── tests/
│   └── test_api.py
├── assets/
├── .env.example
├── .gitignore
├── Dockerfile
├── Procfile
├── requirements.txt
└── README.md
```

## 1. Prerequisites

Python 3.10+ is recommended.

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Windows PowerShell

```powershell
py -m venv .venv
.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
```

## 2. Configure Gemini

Copy `.env.example` to `.env` and replace `your_api_key_here` with your Gemini API key.

```bash
cp .env.example .env
```

A key is optional while `ALLOW_DEMO_MODE=true`; the application will use a deterministic demo generator so you can test the UI and export workflow.

## 3. Start the FastAPI backend

From the project root:

```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/docs` for interactive API documentation.

## 4. Start the Streamlit frontend

In a second terminal, with the virtual environment active:

```bash
streamlit run frontend/app.py
```

Then open the URL Streamlit prints, usually `http://localhost:8501`.

## 5. Test the workflow

1. Choose a document type.
2. Enter parties, terms, and effective date.
3. Add optional jurisdiction and instructions.
4. Click **Generate Document**.
5. Edit the generated text in the preview pane.
6. Use **Explain in Plain Language** for a simplified explanation.
7. Prepare and download TXT, DOCX, or PDF.
8. Optionally upload a logo from the sidebar for branded DOCX/PDF output.

## API examples

### Generate

```bash
curl -X POST http://127.0.0.1:8000/generate \\
  -H "Content-Type: application/json" \\
  -d '{
    "document_type":"Non-Disclosure Agreement (NDA)",
    "parties":"Jane Doe (Disclosing Party), TechNova Inc. (Receiving Party)",
    "terms":"Confidentiality must be maintained at all times; Either party may terminate with 15 days notice",
    "effective_date":"October 1, 2026",
    "jurisdiction":"Tamil Nadu, India",
    "language":"English",
    "tone":"Formal and professional",
    "additional_instructions":"Include a signature section."
  }'
```

### Export

The export endpoint accepts a `format` field with `txt`, `docx`, or `pdf`.

## Notes on the supplied specification

The PDF describes a Streamlit + FastAPI + Gemini architecture, the `/generate` POST endpoint, editable output, and TXT/DOCX/PDF export with logo/footer support. This implementation follows those core requirements and adds test coverage, demo mode, a plain-language explanation endpoint, and container/deployment files. fileciteturn0file0L34-L52 fileciteturn0file0L158-L179 fileciteturn0file0L228-L242

## Legal disclaimer

LegalEase is an AI-assisted drafting tool. It does not replace a qualified lawyer and does not guarantee that a generated document is complete, accurate, or enforceable in a particular jurisdiction. Review all generated content, dates, amounts, parties, governing-law provisions, and required formalities before signing or using a document.
