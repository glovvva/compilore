"""Hybrid search for the **Query** loop.

Uses pgvector + PostgreSQL full-text via RRF (brief §4.3). The stock
``hybrid_search()`` SQL relies on ``auth.uid()``; the backend uses
``hybrid_search_with_tenant`` (see ``sql/hybrid_search_with_tenant.sql``) with
the service role. Authority-tier and recency scoring are scaffolded in SQL but
left behavior-neutral until their business rules are activated.
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from src.lib.openai_client import create_embedding
from src.lib.supabase import create_supabase_client, schedule_insert_wiki_log_row
from src.modules.query.models import ChunkResult

RPC_NAME = "hybrid_search_with_tenant"
PRECHECK_RPC = "gatekeeper_precheck_top_similarity"
SearchResult = ChunkResult


def _vector_literal(embedding: list[float]) -> str:
    """Serialize embedding for PostgREST/pgvector when JSON array is rejected."""
    return "[" + ",".join(f"{x:.8f}" for x in embedding) + "]"


def _scope_filter_wiki_page_ids(
    tenant_id: str,
    wiki_page_ids: list[str],
    *,
    scope: Literal["department", "tenant", "global"],
    department_id: Optional[str],
) -> set[str]:
    """Return allowed wiki page ids under the requested access scope."""
    if scope == "global" or not wiki_page_ids:
        return set(wiki_page_ids)

    client = create_supabase_client()
    pages_res = (
        client.table("wiki_pages")
        .select("id, department_id")
        .eq("tenant_id", tenant_id)
        .in_("id", wiki_page_ids)
        .execute()
    )
    pages = getattr(pages_res, "data", None) or []
    page_dept: dict[str, Optional[str]] = {
        str(row.get("id")): str(row.get("department_id")) if row.get("department_id") else None
        for row in pages
    }

    if scope == "department":
        if not department_id:
            return set()
        return {pid for pid, dep in page_dept.items() if dep == department_id}

    # scope == "tenant"
    dept_ids = [dep for dep in page_dept.values() if dep is not None]
    tenant_wide_departments: set[str] = set()
    if dept_ids:
        dep_res = (
            client.table("departments")
            .select("id")
            .eq("tenant_id", tenant_id)
            .eq("visibility", "tenant_wide")
            .in_("id", dept_ids)
            .execute()
        )
        tenant_wide_departments = {
            str(row.get("id")) for row in (getattr(dep_res, "data", None) or []) if row.get("id")
        }

    return {
        pid
        for pid, dep in page_dept.items()
        if dep is None or (dep in tenant_wide_departments)
    }


async def hybrid_search(
    query: str,
    tenant_id: str,
    match_count: int = 10,
    scope: Literal["department", "tenant", "global"] = "tenant",
    department_id: Optional[str] = None,
    *,
    query_embedding: Optional[list[float]] = None,
) -> list[SearchResult]:
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
            wiki_page_ids = [str(row.get("wiki_page_id")) for row in data if row.get("wiki_page_id")]
            allowed_ids = _scope_filter_wiki_page_ids(
                tenant_id,
                wiki_page_ids,
                scope=scope,
                department_id=department_id,
            )
            out: list[ChunkResult] = []
            for row in data:
                page_id = str(row["wiki_page_id"])
                if page_id not in allowed_ids:
                    continue
                out.append(
                    ChunkResult(
                        chunk_id=str(row["chunk_id"]),
                        wiki_page_id=page_id,
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
