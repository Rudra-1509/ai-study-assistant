# ============================
# Stage 1 — Dependency Builder
# ============================
FROM python:3.10-slim AS builder

WORKDIR /app

# System deps required for scientific Python
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements to leverage Docker cache
COPY requirements.txt .

# Build wheels (faster + deterministic)
RUN pip install --upgrade pip \
    && pip wheel --no-cache-dir --no-deps \
       -r requirements.txt \
       -w /wheels


# ============================
# Stage 2 — Runtime Image
# ============================
FROM python:3.10-slim

WORKDIR /app

# Minimal runtime libraries
RUN apt-get update && apt-get install -y \
    libstdc++6 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels from builder
COPY --from=builder /wheels /wheels

# Install Python deps
RUN pip install --no-cache /wheels/*

# Copy backend source code
COPY . .

# Runtime optimizations
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    OMP_NUM_THREADS=4 \
    MKL_NUM_THREADS=4 \
    TOKENIZERS_PARALLELISM=false

# API port
EXPOSE 8000

# -------- Choose ONE --------
# FastAPI (recommended)
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Plain Python alternative
# CMD ["python", "app.py"]
