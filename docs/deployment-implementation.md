# Deployment Implementation Plan

## Overview
This project contains a React frontend and a Python FastAPI backend with AI functionality. The backend now uses:

- **LLM Inference**: Cloudflare Workers AI API (recommended)
- **Embeddings**: Jina remote API (production-ready, no local ML overhead)
- **Local Models**: Optional fallback (not recommended for PaaS)

## Architecture & Dependencies

The backend architecture is now lightweight and cloud-friendly:

1. **LLM**: Cloudflare Workers AI provides inference without GPU requirements.
2. **Embeddings**: Jina API handles all embedding computation remotely, eliminating the need for `sentence-transformers` and `torch` in production.
3. **Core Pipeline**: Text ingestion, OCR, chunking, topic clustering, keyword extraction, and explanation generation all work without heavy local ML libraries.

### Previous Pain Points (Resolved)

- ❌ **Local GGUF model** (`ctransformers`) — now offloaded to Cloudflare
- ❌ **Local SentenceTransformers** — now offloaded to Jina
- ❌ **Heavy TensorFlow/PyTorch** — no longer needed on the server
- ❌ **Memory exhaustion on PaaS** — production deployments now succeed

## Recommended Deployment Strategy

### Production: Cloudflare LLM + Jina Embeddings (Proven)

1. Set `LLM_PROVIDER=cloudflare` in environment variables.
2. Configure Cloudflare credentials:
   - `CLOUDFLARE_ACCOUNT_ID`
   - `CLOUDFLARE_API_TOKEN`
   - `CLOUDFLARE_MODEL=@cf/meta/llama-3.1-8b-instruct-fp8`
3. Set `EMBEDDING_PROVIDER=remote` in environment variables.
4. Configure Jina credentials:
   - `JINA_API_KEY` (your Jina API token)
   - `JINA_EMBEDDING_URL=https://api.jina.ai/v1/embeddings` (or your custom Jina endpoint)
5. Deploy the backend as a normal FastAPI service on any PaaS (Render, Railway, Cloud Run, etc.).
6. Deploy the frontend as a static site (Vercel, Netlify, Cloudflare Pages).

**Benefits:**
- No GPU required
- No local model downloads
- Minimal memory footprint
- Scales horizontally
- Text/PDF/image requests complete successfully

## Practical Deployment Steps

### Frontend

1. `cd frontend`
2. `npm install`
3. `npm run build`
4. Deploy the output from `dist/` to Vercel, Netlify, or Cloudflare Pages

### Backend

1. Create `backend/.env` with all required credentials:
   ```env
   LLM_PROVIDER=cloudflare
   CLOUDFLARE_ACCOUNT_ID=<your_account_id>
   CLOUDFLARE_API_TOKEN=<your_api_token>
   CLOUDFLARE_MODEL=@cf/meta/llama-3.1-8b-instruct-fp8
   
   EMBEDDING_PROVIDER=remote
   JINA_API_KEY=<your_jina_api_key>
   JINA_EMBEDDING_URL=https://api.jina.ai/v1/embeddings
   ```

2. `pip install -r backend/requirements.txt` (lightweight, no ML frameworks)
3. `python backend/app.py` (or use the start command for your PaaS)

### On Render

1. Push the repo to GitHub
2. Create a new Render Web Service
3. Set the build command: `pip install -r backend/requirements.txt`
4. Set the start command: `python -m uvicorn api.main:app --host 0.0.0.0 --port $PORT`
5. Add the environment variables from step 1 in Render's dashboard
6. Deploy

### Docker (Optional)

If you need to containerize:

1. `cd backend`
2. `docker compose build --no-cache`
3. `docker compose up`

Make sure all environment variables are passed to the container.

## Why This Works

- **Cloudflare Workers AI**: Free tier, no GPU, instant inference
- **Jina Embeddings**: Proven in production, handles all embedding workloads
- **Lightweight Backend**: Only `fastapi`, `requests`, `scikit-learn`, `nltk`, `fitz`, `pytesseract` — no TensorFlow/PyTorch
- **Horizontal Scaling**: No state; can run multiple instances

## Testing Locally

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env with your credentials
echo 'LLM_PROVIDER=cloudflare' > .env
echo 'CLOUDFLARE_ACCOUNT_ID=...' >> .env
# ... add other env vars ...

python app.py
```

Then test with:
```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -F input_type=text \
  -F content="Your study material here"
```

## Troubleshooting

### Text/PDF requests fail or timeout

- Check `JINA_API_KEY` is set correctly
- Verify `EMBEDDING_PROVIDER=remote`
- Check Jina API quota and rate limits

### Cloudflare LLM errors

- Verify `CLOUDFLARE_ACCOUNT_ID` and `CLOUDFLARE_API_TOKEN`
- Check the model name in `CLOUDFLARE_MODEL`

### CORS errors (frontend can't reach backend)

- Update `backend/api/main.py` `allow_origins` to include your deployed frontend URL
- Example: `allow_origins=["https://your-app.vercel.app"]`

## Conclusion

The application is now production-ready with Cloudflare and Jina. No local GPU, no memory exhaustion, no process restarts. Deploy with confidence.
