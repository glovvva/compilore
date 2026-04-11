"""Hybrid search for the **Query** loop.

Uses pgvector + PostgreSQL full-text via RRF (brief §4.3). The stock
``hybrid_search()`` SQL relies on ``auth.uid()``; the backend uses
``hybrid_search_with_tenant`` (see ``sql/hybrid_search_with_tenant.sql``) with
the service role.
"""

from __future__ import annotations

from typing import Any, Optional

from src.lib.openai_client import create_embedding
from src.lib.supabase import create_supabase_client
from src.modules.query.models import ChunkResult

RPC_NAME = "hybrid_search_with_tenant"


def _vector_literal(embedding: list[float]) -> str:
    """Serialize embedding for PostgREST/pgvector when JSON array is rejected."""
    return "[" + ",".join(f"{x:.8f}" for x in embedding) + "]"


def hybrid_search(
    query: str,
    tenant_id: str,
    match_count: int = 10,
    *,
    query_embedding: Optional[list[float]] = None,
) -> list[ChunkResult]:
    """Embed ``query`` (unless ``query_embedding`` is provided) and run hybrid RPC."""
    emb = query_embedding if query_embedding is not None else create_embedding(query)
    client = create_supabase_client()

    base_payload: dict[str, Any] = {
        "p_tenant_id": tenant_id,
        "query_text": query,
        "match_count": match_count,
    }

    last_err: Optional[Exception] = None
    for embedding_param in (emb, _vector_literal(emb)):
        payload = {**base_payload, "query_embedding": embedding_param}
        try:
            res = client.rpc(RPC_NAME, payload).execute()
            data = getattr(res, "data", None) or []
            out: list[ChunkResult] = []
            for row in data:
                out.append(
                    ChunkResult(
                        chunk_id=str(row["chunk_id"]),
                        wiki_page_id=str(row["wiki_page_id"]),
                        chunk_text=str(row.get("chunk_text") or ""),
                        rrf_score=float(row.get("rrf_score") or 0.0),
                    )
                )
            return out
        except Exception as exc:
            last_err = exc
            continue

    msg = (
        f"{RPC_NAME} failed ({last_err!s}). "
        "Apply sql/hybrid_search_with_tenant.sql in Supabase if you have not already."
    )
    raise RuntimeError(msg) from last_err
