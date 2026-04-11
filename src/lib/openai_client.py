"""OpenAI API wrapper for Compilore (embeddings).

``text-embedding-3-small`` (1536 dimensions) for chunk embeddings and hybrid
search, per the brief.
"""

from __future__ import annotations

import os
from typing import Any

from openai import OpenAI

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536


def create_openai_client(api_key: str | None = None) -> OpenAI:
    """Return a configured OpenAI client."""
    key = (api_key or os.environ.get("OPENAI_API_KEY") or "").strip()
    if not key:
        msg = "OPENAI_API_KEY is not set"
        raise RuntimeError(msg)
    return OpenAI(api_key=key)


def create_embedding(text: str, *, client: OpenAI | None = None) -> list[float]:
    """Embed ``text`` with ``text-embedding-3-small`` (1536 dimensions)."""
    c = client or create_openai_client()
    cleaned = text.replace("\n", " ").strip()
    if not cleaned:
        cleaned = " "

    resp = c.embeddings.create(
        model=EMBEDDING_MODEL,
        input=cleaned,
    )
    vec = resp.data[0].embedding
    if len(vec) != EMBEDDING_DIMENSIONS:
        msg = (
            f"Expected {EMBEDDING_DIMENSIONS}-dim embedding for hybrid search, got {len(vec)}. "
            "Use text-embedding-3-small (1536)."
        )
        raise RuntimeError(msg)
    return list(vec)
