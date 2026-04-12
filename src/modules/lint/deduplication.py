"""
deduplication.py — Detects semantically duplicate Wiki pages.

Part of the Lint loop (Loop 4). Uses pgvector cosine similarity.
Pages with similarity > 0.92 are flagged as merge candidates.
NEVER merges autonomously — always returns candidates for human review.
Cost: one vector comparison query per run (~$0).
"""

from __future__ import annotations

from typing import Any

from src.lib.supabase import create_supabase_client, ensure_tenant_exists
from src.modules.lint.models import DuplicateCandidate

RPC_NAME = "find_duplicate_pages"


def find_duplicate_candidates(tenant_id: str) -> list[DuplicateCandidate]:
    client = create_supabase_client()
    ensure_tenant_exists(client, tenant_id)
    try:
        res = client.rpc(RPC_NAME, {"p_tenant_id": tenant_id}).execute()
    except Exception as exc:
        msg = (
            f"{RPC_NAME} failed ({exc!s}). "
            "Apply sql/005_deduplication_query.sql in Supabase if you have not already."
        )
        raise RuntimeError(msg) from exc

    rows: list[dict[str, Any]] = getattr(res, "data", None) or []
    out: list[DuplicateCandidate] = []
    for row in rows:
        sim = float(row.get("similarity") or 0.0)
        action = "merge" if sim > 0.95 else "review"
        out.append(
            DuplicateCandidate(
                page_a_slug=str(row.get("page_a_slug") or ""),
                page_a_title=str(row.get("page_a_title") or ""),
                page_b_slug=str(row.get("page_b_slug") or ""),
                page_b_title=str(row.get("page_b_title") or ""),
                similarity_score=sim,
                suggested_action=action,
            ),
        )
    return out


class DeduplicationAnalyzer:
    def run(self, tenant_id: str) -> list[DuplicateCandidate]:
        return find_duplicate_candidates(tenant_id)
