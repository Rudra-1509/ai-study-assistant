FROM python:3.10-slim

# Install system dependencies (Tesseract) with minimal extras
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

# Use backend as the working directory so imports like `api.main` resolve
WORKDIR /app/backend

# Copy only the backend folder to keep image smaller and avoid copying models
COPY backend/ .

# Install Python dependencies from backend requirements
RUN pip install --no-cache-dir -r requirements.txt

# Runtime envs
ENV PORT=10000
ENV PYTHONUNBUFFERED=1

# For low-memory environments keep a single worker
# Pre-download the SentenceTransformer model at image build time to avoid
# large downloads and memory spikes during the first request at runtime.
RUN python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt')"
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "10000", "--workers", "1"]