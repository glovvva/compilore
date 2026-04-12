"""Read persisted lint reports from ``wiki_log``."""

from __future__ import annotations

from typing import Any

from src.lib.supabase import create_supabase_client, ensure_tenant_exists


def fetch_last_lint_report(tenant_id: str) -> dict[str, Any] | None:
    """Return the most recent ``lint_run`` row payload, or ``None``."""
    client = create_supabase_client()
    ensure_tenant_exists(client, tenant_id)
    res = (
        client.table("wiki_log")
        .select("details, created_at")
        .eq("tenant_id", tenant_id)
        .eq("operation", "lint_run")
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    rows = getattr(res, "data", None) or []
    if not rows:
        return None
    row = rows[0]
    return {
        "report": row.get("details") or {},
        "created_at": row.get("created_at"),
    }
