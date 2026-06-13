import os
from typing import List

import requests

DEFAULT_LOCAL_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "local").lower() #local or jina
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", DEFAULT_LOCAL_MODEL)

JINA_EMBEDDING_MODEL = os.getenv("JINA_EMBEDDING_MODEL", "jina-embeddings-v3")
JINA_API_KEY = os.getenv("JINA_API_KEY", "")
JINA_EMBEDDING_URL = os.getenv("JINA_EMBEDDING_URL", "https://api.jina.ai/v1/embeddings")
EMBEDDING_BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "8"))  #local
EMBEDDING_REQUEST_BATCH = int(os.getenv("EMBEDDING_REQUEST_BATCH", "8"))  #jina

_model = None


def get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(EMBEDDING_MODEL, device="cpu")
    return _model


def _validate_chunks(chunks: List[str]) -> None:
    if not isinstance(chunks, list) or not chunks:
        raise ValueError("Input must be a non-empty list of strings.")

    for chunk in chunks:
        if not isinstance(chunk, str) or not chunk.strip():
            raise ValueError("Each chunk must be a non-empty string.")


def _encode_local(chunks: List[str]) -> List[List[float]]:
    model = get_model()
    embeddings = model.encode(
        chunks,
        batch_size=EMBEDDING_BATCH_SIZE,
        show_progress_bar=False,
        device="cpu",
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    return embeddings.tolist()


def _encode_jina(chunks: List[str]) -> List[List[float]]:
    if not JINA_API_KEY:
        raise ValueError("JINA_API_KEY must be set when EMBEDDING_PROVIDER=jina")

    url = JINA_EMBEDDING_URL
    headers = {
        "Authorization": f"Bearer {JINA_API_KEY}",
        "Content-Type": "application/json",
    }

    all_embeddings: List[List[float]] = []
    print(f"Using Jina embeddings for {len(chunks)} total chunks")
    for start in range(0, len(chunks), EMBEDDING_REQUEST_BATCH):
        batch = chunks[start : start + EMBEDDING_REQUEST_BATCH]

        # Typical Jina embedding endpoints accept a JSON payload with an
        # `input` or `text` field; include the model identifier as available.
        payload = {
            "input": batch,
            "model": JINA_EMBEDDING_MODEL
                   }
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        print("Jina status:", response.status_code)
        response.raise_for_status()
        data = response.json()

        # Support several reasonable response formats returned by hosted
        # embedding services (list[list], list[dict{embedding}], dict{data})
        embeddings = None
        if isinstance(data, list):
            if data and isinstance(data[0], dict) and "embedding" in data[0]:
                embeddings = [item["embedding"] for item in data]
            elif data and isinstance(data[0], list):
                embeddings = data

        elif isinstance(data, dict):
            # e.g. {"data": [{"embedding": [...]}, ...]} or {"embeddings": [...]} 
            if "data" in data and isinstance(data["data"], list):
                first = data["data"][0]
                if isinstance(first, dict) and "embedding" in first:
                    embeddings = [item["embedding"] for item in data["data"]]
            if embeddings is None and "embeddings" in data and isinstance(data["embeddings"], list):
                embeddings = data["embeddings"]

        if embeddings is None:
            raise ValueError(f"Unexpected response from Jina embedding API: {data}")

        all_embeddings.extend(embeddings)

    return all_embeddings


def embed_text(chunks: List[str]) -> List[list]:
    """
    Convert list of text chunks into normalized embeddings.
    Returns: List of embedding vectors (each is a list[float])
    """
    _validate_chunks(chunks)

    if EMBEDDING_PROVIDER == "jina":
        return _encode_jina(chunks)

    return _encode_local(chunks)
