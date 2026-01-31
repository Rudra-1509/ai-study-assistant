# ============================
# Stage 1 — Dependency Builder
# ============================
FROM python:3.10-slim AS builder

WORKDIR /app

# Build tools for Python wheels
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip wheel --no-cache-dir --no-deps \
       -r requirements.txt \
       -w /wheels


# ============================
# Stage 2 — Runtime Image
# ============================
FROM python:3.10-slim

WORKDIR /app

# Reduce ML log noise
ENV TF_CPP_MIN_LOG_LEVEL=2 \
    TOKENIZERS_PARALLELISM=false \
    OMP_NUM_THREADS=4 \
    MKL_NUM_THREADS=4 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# REQUIRED SYSTEM DEPENDENCIES
RUN apt-get update && apt-get install -y \
    libstdc++6 \
    curl \
    tesseract-ocr \
    libtesseract-dev \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY --from=builder /wheels /wheels
RUN pip install --no-cache /wheels/*

# ✅ NLTK DATA (FIX)
RUN python - <<EOF
import nltk
nltk.download('stopwords')
nltk.download('punkt')
EOF

# App source
COPY . .

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
