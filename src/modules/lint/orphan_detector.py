"""
orphan_detector.py — Detects broken [[wikilinks]] in the Wiki.

Part of the Lint loop (Loop 4). RegEx-based, $0 cost, fully deterministic.
Scans all wiki_pages in Supabase, extracts [[wikilink]] references,
checks each against existing slugs. Returns list of broken links per page.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone

from src.lib.supabase import create_supabase_client, ensure_tenant_exists
from src.modules.lint.models import OrphanResult

WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")


def _target_slug(raw: str) -> str:
    """Strip optional [[page|label]] display form."""
    return raw.split("|", 1)[0].strip()


class OrphanDetector:
    """RegEx orphan [[wikilink]] detection for a tenant."""

    def run(self, tenant_id: str) -> list[OrphanResult]:
        return detect_orphans(tenant_id)


def detect_orphans(tenant_id: str) -> list[OrphanResult]:
    client = create_supabase_client()
    ensure_tenant_exists(client, tenant_id)
    res = (
        client.table("wiki_pages")
        .select("slug,title,content_markdown,tenant_id")
        .eq("tenant_id", tenant_id)
        .execute()
    )
    rows = getattr(res, "data", None) or []
    all_slugs = {str(r["slug"]) for r in rows if r.get("slug")}
    now = datetime.now(timezone.utc)
    out: list[OrphanResult] = []

    for row in rows:
        slug = str(row.get("slug") or "")
        title = str(row.get("title") or slug)
        body = str(row.get("content_markdown") or "")
        seen_targets: set[str] = set()
        broken: list[str] = []
        for m in WIKILINK_RE.finditer(body):
            target = _target_slug(m.group(1))
            if not target or target in seen_targets:
                continue
            seen_targets.add(target)
            if target not in all_slugs:
                broken.append(target)
        if broken:
            out.append(
                OrphanResult(
                    page_slug=slug,
                    page_title=title,
                    broken_links=sorted(set(broken)),
                    checked_at=now,
                ),
            )
    return out
