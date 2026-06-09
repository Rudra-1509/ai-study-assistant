import os
from typing import List

import requests

DEFAULT_LOCAL_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_REMOTE_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "local").lower() #local or remote
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", DEFAULT_LOCAL_MODEL)
HUGGINGFACE_EMBEDDING_MODEL = os.getenv("HUGGINGFACE_EMBEDDING_MODEL", DEFAULT_REMOTE_MODEL)
HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN", "")
EMBEDDING_BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "8"))  #local
EMBEDDING_REQUEST_BATCH = int(os.getenv("EMBEDDING_REQUEST_BATCH", "16"))  #remote

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


def _encode_remote(chunks: List[str]) -> List[List[float]]:
    if not HUGGINGFACE_API_TOKEN:
        raise ValueError(
            "HUGGINGFACE_API_TOKEN must be set when EMBEDDING_PROVIDER=remote"
        )

    url = f"https://api-inference.huggingface.co/embeddings/{HUGGINGFACE_EMBEDDING_MODEL}"
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}",
        "Content-Type": "application/json",
    }

    all_embeddings: List[List[float]] = []
    for start in range(0, len(chunks), EMBEDDING_REQUEST_BATCH):
        batch = chunks[start : start + EMBEDDING_REQUEST_BATCH]
        response = requests.post(
            url,
            headers=headers,
            json={"inputs": batch},
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()

        if isinstance(data, dict) and data.get("error"):
            raise ValueError(f"Remote embedding error: {data['error']}")

        if isinstance(data, list) and data and isinstance(data[0], dict):
            embeddings = [item["embedding"] for item in data]
        elif isinstance(data, list) and data and isinstance(data[0], list):
            embeddings = data
        else:
            raise ValueError("Unexpected response from remote embedding API")

        all_embeddings.extend(embeddings)

    return all_embeddings


def embed_text(chunks: List[str]) -> List[list]:
    """
    Convert list of text chunks into normalized embeddings.
    Returns: List of embedding vectors (each is a list[float])
    """
    _validate_chunks(chunks)

    if EMBEDDING_PROVIDER == "remote":
        return _encode_remote(chunks)

    return _encode_local(chunks)
