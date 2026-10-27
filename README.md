# Financial Research Copilot

An AI-powered financial research application that allows users to upload financial reports, ask questions about their contents, and receive answers grounded in retrieved document evidence.

The project combines document processing, semantic search, keyword-based retrieval, reranking, and large language model generation to make financial reports easier to analyze.

## Features

- **Financial document upload:** Upload financial reports for processing.
- **Document question answering:** Ask natural-language questions about uploaded reports.
- **Hybrid retrieval:** Combine semantic search with BM25 keyword retrieval.
- **Reranking:** Improve the relevance of retrieved passages before generating an answer.
- **Evidence-grounded responses:** Generate answers using retrieved report content and display source-page references.
- **Insufficient-evidence handling:** Avoid presenting unsupported information as fact when the documents do not contain enough evidence.
- **Web interface:** Interact with the application through a React frontend.

## Tech Stack

| Component | Technology |
|---|---|
| Frontend | React, Vite, JavaScript |
| Backend | Python, FastAPI |
| Semantic search | FAISS, Sentence Transformers |
| Keyword retrieval | BM25 |
| Reranking | Cross-Encoder |
| Answer generation | Google Gemini API |
| Version control | Git, GitHub |

## Architecture

```text
User
  |
  v
React + Vite Frontend
  |
  v
FastAPI Backend
  |
  v
Document Processing
  |
  v
Text Chunks + Metadata + Vector Index
  |
  v
Hybrid Retrieval
(Semantic Search + BM25)
  |
  v
Cross-Encoder Reranking
  |
  v
Gemini Answer Generation
  |
  v
Answer + Source References
```

## Project Structure

```text
financial-research-copilot/
├── frontend/       # React + Vite application
├── src/            # Python backend and retrieval pipeline
├── data/           # Local documents and generated indexes
├── .gitignore
└── README.md
```

Generated files, uploaded reports, local environment files, and Python virtual environments are excluded from Git through `.gitignore`.

## Getting Started

### Prerequisites

- Python 3.12 or a compatible Python version
- Node.js and npm
- A Google Gemini API key

### 1. Clone the repository

```bash
git clone https://github.com/Gourav-Patel6611/financial-research-copilot.git
cd financial-research-copilot
```

### 2. Set up the Python environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the Python dependencies using the project's dependency file, if available.

> If the repository does not yet include a backend dependency file, one needs to be created before a fresh installation can be completed.

### 3. Configure environment variables

Create a `.env` file in the project root and configure your Gemini API key and model:

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=your_supported_gemini_model
```

Replace the placeholders with your own values. Never commit `.env` or expose your API key publicly.

### 4. Start the backend

From the project root, with the virtual environment activated:

```powershell
uvicorn src.api:app --reload
```

The backend API is available at:

- API: `http://127.0.0.1:8000`
- Interactive API documentation: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/api/health`

### 5. Start the frontend

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite, usually `http://localhost:5173`.

Keep both the backend and frontend running while using the application.

## Example Use Case

Upload a company's annual report and ask a question such as:

> What was the company's revenue from operations in FY2024–25, and how did it compare with the previous financial year?

The application retrieves relevant passages, generates an answer based on the available evidence, and provides source-page references for verification.

## Current Scope

This project focuses on document-grounded financial research. Its answers depend on the quality of the uploaded documents, text extraction, retrieval results, and generated responses.

Always verify important financial figures against the original report before relying on them for financial or investment decisions.

## Future Improvements

- Improve retrieval speed and model-loading efficiency.
- Add automated tests for document processing, retrieval, and API endpoints.
- Improve error handling and observability.
- Add deployment and production configuration.
- Expand document management and evaluation capabilities.

## Author

Developed as a portfolio project exploring full-stack development, information retrieval, and AI-powered document analysis.

## License

No license has been specified yet. Unless a license is added, the repository should not be assumed to grant others permission to reuse, modify, or redistribute its code.
