# Deployment Implementation Plan

## Overview
This project contains a React frontend and a Python FastAPI backend with AI functionality. The backend currently supports two LLM modes:

- `local` using a GGUF model via `ctransformers`
- `cloudflare` using Cloudflare Workers AI API

The current dependency profile is resource-heavy because the backend installs large ML libraries and downloads local model weights.

## Key Findings

1. `backend/llm/factory.py` defaults to `local`.
   - This uses `backend/llm/local.py` and a local Mistral 7B GGUF model.
   - Local model inference is very resource intensive and is the main source of Docker/deployment failure.

2. `backend/embeddings/bert_embedder.py` loads a TensorFlow-based Sentence Transformers model:
   - `sentence-transformers/all-MiniLM-L6-v2`
   - This brings in `tensorflow`, `transformers`, and related ML packages.
   - It adds additional build size and runtime memory cost.

3. The backend Dockerfile installs system packages plus Python wheels, but the heavy ML dependency set is still the dominant problem.

## Recommended Deployment Strategy

### Option 1: Preferred — Cloudflare-based backend

1. Set `LLM_PROVIDER=cloudflare` in environment variables.
2. Configure Cloudflare credentials:
   - `CLOUDFLARE_ACCOUNT_ID`
   - `CLOUDFLARE_API_TOKEN`
   - `CLOUDFLARE_MODEL=@cf/meta/llama-3-8b-instruct`
3. Deploy the backend as a normal FastAPI service.
4. Deploy the frontend as a static site (Vercel, Netlify, or any static web host).

Benefits:
- Avoids local 7B model inference costs
- No need for GPU or huge local memory for LLM
- Simplifies deployment to cloud or PaaS

### Option 2: Docker deployment with reduced local inference

1. Keep the backend Dockerfile, but ensure the backend uses Cloudflare.
2. Build the image on a machine with sufficient resources if local laptop is too weak.
3. Use Docker only for packaging, not for model training.

Notes:
- If the container build still fails, the issue is likely wheel compilation for TensorFlow/torch.
- Build on a stronger VM and then push the finished image to your target environment.

## Optional Improvement: Remote embeddings

The backend still performs local embedding computation through TensorFlow. For the lightest deployment, consider replacing this with a remote embedding API.

If remote embeddings are used:
- Remove TensorFlow and `sentence-transformers` from production requirements
- Keep backend focused on text ingestion, OCR, chunking, and Cloudflare LLM calls

## Practical Deployment Steps

### Frontend

1. `cd frontend`
2. `npm install`
3. `npm run build`
4. Deploy the output from `dist/` to a static host

### Backend

1. Create `backend/.env` with Cloudflare credentials
2. `pip install -r backend/requirements.txt`
3. `python backend/app.py`

### Docker (optional)

1. Set `LLM_PROVIDER=cloudflare`
2. `docker compose build --no-cache`
3. `docker compose up`

## Conclusion

The safest deployment path is to use Cloudflare for inference and avoid local `local` mode by default. Docker can still work, but only after removing the local GGUF model dependency from the active production path or building the image on a suitably powerful machine.
