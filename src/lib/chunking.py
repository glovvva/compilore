"""Token-based text chunking for embeddings (approximate, OpenAI-style)."""

from __future__ import annotations

import tiktoken


def chunk_text_by_tokens(
    text: str,
    *,
    max_tokens: int = 500,
    overlap_tokens: int = 50,
    encoding_name: str = "cl100k_base",
) -> list[str]:
    """Split ``text`` into chunks of up to ``max_tokens`` with ``overlap_tokens`` overlap."""
    if max_tokens <= 0:
        msg = "max_tokens must be positive"
        raise ValueError(msg)
    if overlap_tokens < 0 or overlap_tokens >= max_tokens:
        msg = "overlap_tokens must be in [0, max_tokens)"
        raise ValueError(msg)

    stripped = text.strip()
    if not stripped:
        return []

    enc = tiktoken.get_encoding(encoding_name)
    ids = enc.encode(stripped)
    if not ids:
        return []

    chunks: list[str] = []
    start = 0
    n = len(ids)
    while start < n:
        end = min(start + max_tokens, n)
        chunk_ids = ids[start:end]
        chunks.append(enc.decode(chunk_ids))
        if end >= n:
            break
        start = max(0, end - overlap_tokens)
        if start >= n:
            break
    return chunks
