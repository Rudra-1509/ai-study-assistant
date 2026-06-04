from sentence_transformers import SentenceTransformer
from typing import List

# Lightweight embedding model (fast + production-safe)
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Load model once at startup
model = SentenceTransformer(MODEL_NAME)


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

    # Encode in batch (MUCH faster than loop)
    embeddings = model.encode(
        chunks,
        batch_size=32,
        show_progress_bar=False,
        normalize_embeddings=True  # L2 normalization included
    )

    return embeddings.tolist()