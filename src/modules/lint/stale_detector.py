"""
stale_detector.py — Flags Wiki pages that have not been updated recently.

Part of the Lint loop (Loop 4). Date-comparison only, $0 cost.
Default threshold: 30 days. Pages below threshold are flagged as stale
but NOT automatically modified. Human decides action via HITL.
"""

from __future__ import annotations

from datetime import datetime, timezone

from src.lib.supabase import create_supabase_client, ensure_tenant_exists
from src.modules.lint.models import StaleResult


def detect_stale_pages(tenant_id: str, *, threshold_days: int = 30) -> list[StaleResult]:
    client = create_supabase_client()
    ensure_tenant_exists(client, tenant_id)
    res = (
        client.table("wiki_pages")
        .select("slug,title,page_type,updated_at,confidence,tenant_id")
        .eq("tenant_id", tenant_id)
        .execute()
    )
    rows = getattr(res, "data", None) or []
    now = datetime.now(timezone.utc)
    out: list[StaleResult] = []

    for row in rows:
        ptype = str(row.get("page_type") or "").lower()
        if ptype == "index":
            continue
        raw_updated = row.get("updated_at")
        if not raw_updated:
            continue
        try:
            if isinstance(raw_updated, str):
                u = datetime.fromisoformat(raw_updated.replace("Z", "+00:00"))
            else:
                u = raw_updated
            if u.tzinfo is None:
                u = u.replace(tzinfo=timezone.utc)
        except (TypeError, ValueError):
            continue
        days = (now - u).days
        if days > threshold_days:
            conf = float(row.get("confidence") or 0.0)
            out.append(
                StaleResult(
                    slug=str(row.get("slug") or ""),
                    title=str(row.get("title") or ""),
                    days_since_update=days,
                    confidence=conf,
                    page_type=ptype,
                ),
            )
    return sorted(out, key=lambda s: s.days_since_update, reverse=True)


class StaleDetector:
    def run(self, tenant_id: str, *, threshold_days: int = 30) -> list[StaleResult]:
        return detect_stale_pages(tenant_id, threshold_days=threshold_days)
