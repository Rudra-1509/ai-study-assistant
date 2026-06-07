# AI Study Assistant

AI Study Assistant is a full-stack study-notes generator that turns pasted text, PDFs, or images into structured, revision-friendly explanations. It extracts source material, cleans and chunks it, groups chunks into topics, estimates difficulty, and asks an LLM to write focused Markdown study notes for each topic.

The project is intentionally built as a learning pipeline instead of a simple “send everything to an LLM” wrapper. Each stage has a clear responsibility: ingestion, preprocessing, embeddings, topic grouping, keyword extraction, difficulty estimation, generation, and lightweight evaluation logging.

## Features

- **Three input modes**: paste raw text, upload a PDF, or upload an image.
- **PDF text extraction with OCR fallback**: readable PDF text is extracted directly, while low-text pages are rendered and passed through Tesseract OCR.
- **Image OCR**: PNG/JPG/JPEG files are converted to grayscale and processed with Tesseract.
- **Semantic chunking pipeline**: cleaned input is split into manageable chunks before embedding and clustering.
- **Topic discovery**: chunks are embedded with SentenceTransformers and clustered with KMeans.
- **Keyword extraction**: topic-level keywords are selected with stopword filtering and word-frequency ranking.
- **Difficulty estimation**: each topic is labeled as `easy`, `medium`, or `hard` using keyword complexity, average chunk length, and topic breadth.
- **Study-guide generation**: the backend generates topic outlines, section content, and conclusions using a pluggable LLM client.
- **Frontend input locking**: users can only submit one active input type at a time.
- **Markdown output rendering**: generated explanations are rendered as readable study notes in the browser.
- **Run logging**: each analysis logs summary evaluation metrics to a JSONL log file.

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
- SentenceTransformers (`all-MiniLM-L6-v2`) for embeddings
- scikit-learn KMeans for topic clustering
- NLTK stopwords for keyword extraction
- Cloudflare Workers AI by default, with a local GGUF client option
- Docker support for the backend

## Repository Structure

```text
.
├── readme.md                       # Main project documentation
├── implementation.md               # Architecture and implementation details with Mermaid diagrams
├── deployment-implementation.md    # Deployment notes
├── samples/                        # Example PDF, image, and text inputs
├── backend/
│   ├── app.py                      # Uvicorn entry point
│   ├── controller.py               # End-to-end backend pipeline orchestration
│   ├── requirements.txt            # Python dependencies
│   ├── Dockerfile                  # Backend container image
│   ├── docker-compose.yml          # Backend compose setup
│   ├── api/main.py                 # FastAPI app, CORS, lifespan, and /analyze endpoint
│   ├── ingestion/                  # Text, PDF, and image loaders
│   ├── preprocessing/              # Text cleaning and chunking
│   ├── embeddings/                 # SentenceTransformer embedding layer
│   ├── understanding/              # Clustering, keywords, and difficulty scoring
│   ├── generation/                 # LLM prompt orchestration and post-processing
│   ├── llm/                        # LLM abstraction, Cloudflare client, local client, factory
│   └── evaluation/                 # Output metrics and run logging
└── frontend/
    ├── package.json                # Frontend dependencies and scripts
    ├── vite.config.ts              # Vite configuration and path aliases
    ├── index.html                  # HTML shell
    └── src/
        ├── main.tsx                # React bootstrap
        ├── App.tsx                 # Router configuration
        ├── pages/                  # Home and Output pages
        ├── components/             # Upload UI, header, title bar, UI primitives
        ├── api/                    # API client
        ├── hooks/                  # Analysis hook
        ├── types/                  # Shared frontend types
        └── styles/                 # Global styles
```

## How It Works

1. The user selects one input mode in the React UI: text, PDF, or image.
2. The frontend sends a `multipart/form-data` request to `POST /analyze`.
3. FastAPI validates the input and extracts text using the correct loader.
4. The controller cleans and chunks the text.
5. Chunks are embedded with `sentence-transformers/all-MiniLM-L6-v2`.
6. KMeans groups chunks into one or more topic clusters.
7. Keywords are extracted for each topic.
8. A heuristic difficulty estimator labels each topic.
9. The generation layer builds a topic outline, creates section-specific context, calls the LLM, deduplicates repeated facts, and adds a conclusion.
10. Evaluation metrics are computed and logged.
11. The frontend navigates to the output page and renders each topic as Markdown study notes.

For diagrams and deeper implementation notes, see [`implementation.md`](./implementation.md).

## Prerequisites

- Python 3.10+
- Node.js 20+ recommended
- npm
- Tesseract OCR installed and available on your system `PATH`
- Cloudflare Workers AI credentials, unless you switch to the local LLM provider

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
# LLM provider: cloudflare or local
LLM_PROVIDER=cloudflare

# Cloudflare Workers AI
CLOUDFLARE_ACCOUNT_ID=your_account_id_here
CLOUDFLARE_API_TOKEN=your_api_token_here
CLOUDFLARE_MODEL=@cf/meta/llama-3.1-8b-instruct-fp8

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

Consumes `multipart/form-data`.

| Field | Required | Description |
| --- | --- | --- |
| `input_type` | Yes | One of `text`, `pdf`, or `image`. |
| `content` | Required for text | Raw text to analyze. |
| `file` | Required for PDF/image | Uploaded PDF or image file. |

Response shape:

```json
{
  "0": {
    "difficulty": "medium",
    "keywords": ["revolution", "france", "assembly"],
    "explanation": "## Section title\nGenerated study notes..."
  }
}
```

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

Use two terminals:

```bash
# Terminal 1
cd backend
source venv/bin/activate
python app.py
```

```bash
# Terminal 2
cd frontend
npm run dev
```

## Docker Backend Option

The backend includes Docker assets. From the `backend` directory:

```bash
cd backend
docker compose up --build
```

Make sure required environment variables are available to the container.

## Configuration Notes

- The frontend reads the backend base URL from `VITE_API_URL`.
- The backend allows CORS from `http://localhost:5173` and `http://127.0.0.1:5173`.
- The default LLM provider is `cloudflare`.
- The local provider expects a GGUF model under `models/mistral` with the configured file name.
- `backend/evaluation/logger.py` writes run summaries to `run_logs.jsonl` relative to the process working directory.

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

Core text/PDF/image ingestion, backend topic pipeline, LLM generation, and frontend rendering are implemented. Future improvements could include flashcards, Q&A mode, source citations, better topic titles, richer evaluation, and a production deployment configuration.

## Author

Rudra Mondal

- GitHub: <https://github.com/Rudra-1509>
