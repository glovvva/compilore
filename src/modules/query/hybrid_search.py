"""Hybrid search for the **Query** loop.

Uses pgvector + PostgreSQL full-text via RRF (brief §4.3). The stock
``hybrid_search()`` SQL relies on ``auth.uid()``; the backend uses
``hybrid_search_with_tenant`` (see ``sql/hybrid_search_with_tenant.sql``) with
the service role.
"""

from __future__ import annotations

from typing import Any, Optional

from src.lib.openai_client import create_embedding
from src.lib.supabase import create_supabase_client, schedule_insert_wiki_log_row
from src.modules.query.models import ChunkResult

RPC_NAME = "hybrid_search_with_tenant"
PRECHECK_RPC = "gatekeeper_precheck_top_similarity"


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
            schedule_insert_wiki_log_row(
                tenant_id=tenant_id,
                operation="query",
                module="hybrid_search",
                details={
                    "query_preview": query[:100],
                    "results_returned": len(out),
                },
                tokens_used=0,
                cost_usd=0.0,
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


def gatekeeper_answer_precheck(
    tenant_id: str,
    answer_markdown: str,
    *,
    similarity_threshold: float = 0.85,
) -> tuple[str, str, float] | None:
    """
    Embed the synthesized answer and find the single most similar chunk (cosine).

    Returns ``(slug, page_type, cosine_similarity)`` when the top hit exceeds
    ``similarity_threshold`` and ``page_type`` is ``concept`` or ``output``;
    otherwise ``None``. Used by the Gatekeeper (D-16) before novelty evaluation.
    """
    text = (answer_markdown or "").strip()
    if not text:
        return None

    emb = create_embedding(text)
    client = create_supabase_client()

    last_err: Optional[Exception] = None
    for embedding_param in (emb, _vector_literal(emb)):
        payload: dict[str, Any] = {
            "p_tenant_id": tenant_id,
            "query_embedding": embedding_param,
        }
        try:
            res = client.rpc(PRECHECK_RPC, payload).execute()
            data = getattr(res, "data", None) or []
            if not data:
                return None
            row = data[0]
            slug = str(row.get("slug") or "")
            page_type = str(row.get("page_type") or "").lower()
            sim = float(row.get("cosine_similarity") or 0.0)
            if sim <= similarity_threshold:
                return None
            if page_type not in ("concept", "output"):
                return None
            if not slug:
                return None
            return slug, page_type, sim
        except Exception as exc:
            last_err = exc
            continue

    msg = (
        f"{PRECHECK_RPC} failed ({last_err!s}). "
        "Apply sql/004_gatekeeper_precheck_similarity.sql in Supabase if you have not already."
    )
    raise RuntimeError(msg) from last_err
