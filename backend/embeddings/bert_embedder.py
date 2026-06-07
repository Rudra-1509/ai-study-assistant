from sentence_transformers import SentenceTransformer
from typing import List

# Lightweight embedding model (fast + production-safe)
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_model: SentenceTransformer | None = None

def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def embed_text(chunks: List[str]) -> List[list]:
    """
    Convert list of text chunks into normalized embeddings.
    Returns: List of embedding vectors (each is a list[float])
    """

    if not isinstance(chunks, list) or not chunks:
        raise ValueError("Input must be a non-empty list of strings.")

    for chunk in chunks:
        if not isinstance(chunk, str) or not chunk.strip():
            raise ValueError("Each chunk must be a non-empty string.")

    model = get_model()
    # Encode in batch (MUCH faster than loop)
    embeddings = model.encode(
        chunks,
        batch_size=32,
        show_progress_bar=False,
        normalize_embeddings=True  # L2 normalization included
    )

    return embeddings.tolist()