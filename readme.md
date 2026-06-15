# AI Study Assistant

AI Study Assistant is a full-stack study-notes generator that turns pasted text, PDFs, or images into structured, revision-friendly explanations. It extracts source material, cleans and chunks it, groups chunks into topics, estimates difficulty, and asks an LLM to write focused Markdown study notes for each topic.

The project is intentionally built as a learning pipeline instead of a simple “send everything to an LLM” wrapper. Each stage has a clear responsibility: ingestion, preprocessing, embeddings, topic grouping, keyword extraction, difficulty estimation, generation, and lightweight evaluation logging.
## 🚀 Live Demo

**Try it now:** https://ai-study-assistant-delta-lake.vercel.app/

### Demo Video

> 📹 **Demo video coming soon!** Check back for a walkthrough of the features and pipeline.

---
## Features

- **Three input modes**: paste raw text, upload a PDF, or upload an image.
- **PDF text extraction with OCR fallback**: readable PDF text is extracted directly, while low-text pages are rendered and passed through Tesseract OCR.
- **Image OCR**: PNG/JPG/JPEG files are converted to grayscale and processed with Tesseract.
- **Semantic chunking pipeline**: cleaned input is split into manageable chunks (800 characters) before embedding and clustering.
- **Topic discovery**: chunks are embedded via Jina API (cloud-based, no local ML overhead) and clustered with KMeans.
- **Keyword extraction**: topic-level keywords are selected with stopword filtering and word-frequency ranking.
- **Difficulty estimation**: each topic is labeled as `easy`, `medium`, or `hard` using a heuristic formula based on keyword length, chunk length, and topic breadth.
- **Study-guide generation**: the backend generates topic outlines, section content, and conclusions using a pluggable LLM client.
- **Frontend input locking**: users can only submit one active input type at a time.
- **Markdown output rendering**: generated explanations are rendered as readable study notes in the browser.
- **Run logging**: each analysis logs summary evaluation metrics (keyword coverage, word count validation) to a JSONL log file.
- **Cloud-native architecture**: uses Jina for embeddings and Cloudflare Workers AI for LLM inference—no heavy ML libraries required locally.

## Tech Stack

### Frontend

- React 19
- TypeScript
- Vite
- Tailwind CSS v4
- React Router
- React Markdown
- shadcn-style UI primitives with Radix utilities

### Backend

- FastAPI
- Python
- Uvicorn
- PyMuPDF (`fitz`) for PDF parsing
- Tesseract OCR via `pytesseract`
- Jina API for remote embeddings (production-ready)
- scikit-learn KMeans for topic clustering
- NLTK stopwords for keyword extraction
- Cloudflare Workers AI for LLM inference
- Docker support for the backend

## Repository Structure

```text
.
├── readme.md                       # Main project documentation
├── Dockerfile                      # Backend container image
├── startup.bat                     # Development launcher (starts backend + frontend)
├── implementation.md               # Architecture and implementation details with Mermaid diagrams
├── deployment-implementation.md    # Deployment notes
├── samples/                        # Example PDF, image, and text inputs
├── models/                         # Local LLM models (Mistral GGUF for optional local inference)
├── backend/
│   ├── app.py                      # Uvicorn entry point
│   ├── controller.py               # End-to-end backend pipeline orchestration (8 stages)
│   ├── requirements.txt            # Python dependencies
│   ├── run_logs.jsonl              # Evaluation metrics log file
│   ├── api/main.py                 # FastAPI app, CORS, lifespan, and /analyze endpoint
│   ├── ingestion/                  # Text, PDF (with OCR fallback), and image loaders
│   ├── preprocessing/              # Text cleaning (lowercasing, punctuation) and chunking (800 chars)
│   ├── embeddings/                 # Jina API integration for cloud-based embeddings
│   ├── understanding/              # KMeans clustering, keyword extraction, difficulty scoring
│   ├── generation/                 # LLM prompt orchestration and post-processing (deduplication)
│   ├── llm/                        # LLM factory pattern (Cloudflare and local GGUF clients)
│   └── evaluation/                 # Output metrics logging and run summary computation
└── frontend/
    ├── package.json                # Frontend dependencies and scripts
    ├── vite.config.ts              # Vite configuration and path aliases
    ├── index.html                  # HTML shell
    ├── tsconfig.json               # TypeScript configuration
    └── src/
        ├── main.tsx                # React bootstrap
        ├── App.tsx                 # Router configuration (Home and Output routes)
        ├── pages/                  # Home (upload UI) and Output (results display)
        ├── components/             # Upload UI, Header, TitleBar, and shadcn/Radix UI primitives
        ├── api/                    # HTTP client for /analyze endpoint
        ├── hooks/                  # useAnalyze hook for state management
        ├── types/                  # TypeScript types (Difficulty, StudyResponse, etc.)
        └── styles/                 # Global CSS and Tailwind configuration
```

## How It Works

1. The user selects one input mode in the React UI: text, PDF, or image.
2. The frontend sends a `multipart/form-data` request to `POST /analyze`.
3. FastAPI validates the input and extracts text using the correct loader.
4. The controller cleans and chunks the text (800 character chunks, lowercase normalization).
5. Chunks are embedded using **Jina API** (remote, scalable, no local ML overhead).
6. KMeans groups chunks into one or more topic clusters based on semantic similarity.
7. Keywords are extracted for each topic using frequency-based ranking with NLTK stopword filtering.
8. A heuristic difficulty estimator labels each topic as `easy`, `medium`, or `hard` using a scoring formula.
9. The generation layer builds a topic outline, creates section-specific context, calls **Cloudflare Workers AI** (Llama 3.1 8B Instruct), deduplicates repeated facts, and adds a conclusion.
10. Evaluation metrics are computed (keyword coverage, word count validation, length appropriateness) and logged to JSONL.
11. The frontend navigates to the output page and renders each topic as Markdown study notes with difficulty badges and keywords.

For diagrams and deeper implementation notes, see [`implementation.md`](./implementation.md).

### Difficulty Estimation Formula

Each topic is scored using a heuristic formula:

```
Score = (avg_keyword_length / 10) + (avg_chunk_length / 100) + (num_chunks / 5)

Difficulty Classification:
- Easy:    Score < 1.5
- Medium:  1.5 ≤ Score ≤ 3.0
- Hard:    Score > 3.0
```

This accounts for vocabulary complexity, content depth, and topic breadth.

## Prerequisites

- Python 3.10+
- Node.js 20+ recommended
- npm
- Tesseract OCR installed and available on your system `PATH`
- Cloudflare Workers AI credentials for LLM inference
- Jina API credentials for remote embeddings

### Installing Tesseract OCR

Image upload and OCR fallback for scanned PDFs depend on Tesseract.

- **Windows**: install a recent Tesseract build and add it to `PATH`.
- **macOS**: `brew install tesseract`
- **Linux/Debian/Ubuntu**: `sudo apt-get install tesseract-ocr`

## Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env`:

```env
# LLM provider: cloudflare (recommended) or local
LLM_PROVIDER=cloudflare

# Cloudflare Workers AI
CLOUDFLARE_ACCOUNT_ID=your_account_id_here
CLOUDFLARE_API_TOKEN=your_api_token_here
CLOUDFLARE_MODEL=@cf/meta/llama-3.1-8b-instruct-fp8

# Embeddings: use Jina remote API (recommended)
EMBEDDING_PROVIDER=remote
JINA_API_KEY=your_jina_api_key_here
JINA_EMBEDDING_URL=https://api.jina.ai/v1/embeddings

# App settings
ENV=development
```

Run the backend:

```bash
cd backend
python app.py
```

The API runs at `http://127.0.0.1:8000` by default.

### Backend API

#### `GET /health`

Returns a simple health payload:

```json
{ "status": "ok" }
```

#### `POST /analyze`

Consumes `multipart/form-data`. The backend enforces a **limit of 3 concurrent LLM calls** via a semaphore to respect API rate limits.

| Field | Required | Description |
| --- | --- | --- |
| `input_type` | Yes | One of `text`, `pdf`, or `image`. |
| `content` | Required for text | Raw text to analyze. |
| `file` | Required for PDF/image | Uploaded PDF or image file. |

**Response shape:**

```json
{
  "0": {
    "difficulty": "medium",
    "keywords": ["revolution", "france", "assembly"],
    "explanation": "## Section title\nGenerated study notes in Markdown format..."
  },
  "1": {
    "difficulty": "hard",
    "keywords": ["enlightenment", "political", "philosophy"],
    "explanation": "## Another topic\nMore Markdown content..."
  }
}
```

Topics are keyed by numeric cluster ID. Each contains difficulty level, extracted keywords, and LLM-generated Markdown explanation.

## Frontend Setup

```bash
cd frontend
npm install
```

Create `frontend/.env`:

```env
VITE_API_URL=http://127.0.0.1:8000
```

Run the frontend:

```bash
cd frontend
npm run dev
```

Open `http://localhost:5173` in your browser.

## Running Both Apps

The quickest way is to use the provided `startup.bat` script (Windows):

```bash
./startup.bat
```

This launches both the backend (in reload mode) and frontend dev server in separate terminals.

Alternatively, use two terminals manually:

```bash
# Terminal 1
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python app.py
```

```bash
# Terminal 2
cd frontend
npm run dev
```

Open `http://localhost:5173` in your browser.

## Docker Backend Option

The backend includes Docker assets. From the `backend` directory:

```bash
cd backend
docker compose up --build
```

Make sure required environment variables are available to the container.

## Configuration Notes

- The frontend reads the backend base URL from `VITE_API_URL`.
- The backend allows CORS from `http://localhost:5173`, `http://127.0.0.1:5173`, and production domains (Vercel-hosted frontends).
- The default LLM provider is `cloudflare` (recommended for production quality).
- The local provider expects a GGUF model under `models/mistral` with the configured file name.
- `backend/evaluation/logger.py` writes run summaries to `run_logs.jsonl` relative to the process working directory.
- Concurrent LLM calls are limited to 3 via a semaphore to respect API rate limits.
- The live demo is deployed on Vercel and connects to a cloud-hosted backend.

## Known Limitations

- The text cleaner currently lowercases all source text, which can simplify matching but loses original capitalization.
- Keyword extraction is frequency-based and may miss multi-word concepts.
- Topic labels are numeric cluster IDs, not human-readable titles.
- The local LLM client has a different method signature from the Cloudflare client, so the Cloudflare provider is the safer default for the current async generation path.
- OCR quality depends on Tesseract installation, image clarity, and PDF scan quality.
- Generated explanations depend on model behavior and should be reviewed before using as authoritative study material.

## Development Scripts

Frontend scripts:

```bash
cd frontend
npm run dev      # Start Vite dev server
npm run build    # Type-check and build production assets
npm run lint     # Run ESLint
npm run preview  # Preview production build
```

Backend startup:

```bash
cd backend
python app.py
```

## Project Status

✅ **Production Ready** - Deployed live at https://ai-study-assistant-delta-lake.vercel.app/

- Core text/PDF/image ingestion, backend topic pipeline, LLM generation, and frontend rendering are fully implemented
- Cloud-native architecture with Jina embeddings and Cloudflare Workers AI
- Comprehensive evaluation and logging pipeline
- Future improvements could include flashcards, Q&A mode, source citations, better topic titles, and richer evaluation metrics

## Author

Rudra Mondal

- GitHub: <https://github.com/Rudra-1509>
