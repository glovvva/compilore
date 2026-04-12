"""Fetch ``wiki_pages`` metadata for search hits (slug, title, page_type, confidence)."""

from __future__ import annotations

from typing import Any

from src.lib.supabase import create_supabase_client


def fetch_wiki_pages_by_ids(tenant_id: str, wiki_page_ids: list[str]) -> list[dict[str, Any]]:
    """Return rows with slug, title, page_type, confidence, id; preserve input order by first-seen id."""
    ids = [x for x in dict.fromkeys(wiki_page_ids) if x]
    if not ids:
        return []
    client = create_supabase_client()
    res = (
        client.table("wiki_pages")
        .select("id,slug,title,page_type,confidence")
        .eq("tenant_id", tenant_id)
        .in_("id", ids)
        .execute()
    )
    rows = getattr(res, "data", None) or []
    by_id = {str(r["id"]): r for r in rows if r.get("id")}
    ordered: list[dict[str, Any]] = []
    seen: set[str] = set()
    for wid in ids:
        if wid in seen:
            continue
        seen.add(wid)
        row = by_id.get(wid)
        if row:
            ordered.append(
                {
                    "id": str(row["id"]),
                    "slug": str(row.get("slug") or ""),
                    "title": str(row.get("title") or ""),
                    "page_type": str(row.get("page_type") or ""),
                    "confidence": float(row.get("confidence") or 0.0),
                },
            )
    return ordered
