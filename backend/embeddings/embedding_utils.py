"""
embedding_utils.py

Small helper layer that lets header <-> chunk relevance scoring use the
project's EXISTING embedding infrastructure (bert_embedder.embed_text)
instead of the old hardcoded SEMANTIC_HINTS synonym dictionary.

Why embeddings instead of a hardcoded synonym dictionary:
A header like "Career and Transfers" and a chunk like "He signed a
four-year contract and made his debut for the club" share almost no
literal words, but they are clearly about the same thing. A hand-written
synonym list can never cover every domain (sports bios, physics,
history, ...) - someone has to think of every word in advance. An
embedding model already places semantically related text close together
in vector space for ANY topic, without anyone enumerating it by hand.

This module intentionally does NOT introduce a vector database or a RAG
pipeline. It's a thin wrapper: embed one header, compare it against
chunk embeddings that already exist in memory, done.
"""

from __future__ import annotations

import asyncio
from typing import Optional, Sequence

import numpy as np

from .bert_embedder import embed_text


def cosine_similarity(vec_a: Sequence[float], vec_b: Sequence[float]) -> float:
    """
    Cosine similarity between two embedding vectors, safe against zero
    vectors (which would otherwise raise a divide-by-zero).

    embed_text() already L2-normalizes output when EMBEDDING_PROVIDER=local
    (normalize_embeddings=True), but we do NOT assume the Jina API response
    is normalized - so we normalize defensively here rather than trusting
    the provider.
    """
    a = np.asarray(vec_a, dtype=float)
    b = np.asarray(vec_b, dtype=float)

    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    similarity = float(np.dot(a, b) / (norm_a * norm_b))

    # Clip negatives to 0: a header and a chunk being "semantically
    # opposite" shouldn't actively subtract from relevance in the hybrid
    # score, it should just contribute nothing.
    return max(0.0, similarity)


async def embed_header_safe(header_text: str) -> Optional[list[float]]:
    """
    Embed a single section header using the SAME embed_text() pipeline
    already used for chunks, so header and chunk vectors live in the same
    space regardless of which provider (local sentence-transformers or
    Jina) is configured via EMBEDDING_PROVIDER.

    embed_text() is a blocking call (CPU model inference locally, or a
    blocking `requests.post` for Jina). It's run in a worker thread via
    asyncio.to_thread so a slow/hanging embedding call doesn't stall the
    event loop while other topics/sections are being processed
    concurrently elsewhere in the pipeline.

    Returns None on ANY failure (missing API key, network error, timeout,
    malformed provider response, etc.) so callers can fall back to pure
    lexical/keyword scoring instead of crashing the whole study-guide run.
    """
    if not header_text or not header_text.strip():
        return None

    try:
        embeddings = await asyncio.to_thread(embed_text, [header_text])
        return embeddings[0]
    except Exception:
        # Any embedding-provider failure degrades gracefully to
        # lexical/keyword-only scoring downstream - it must never take
        # down study-guide generation.
        return None