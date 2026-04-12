"""
confidence_decay.py — Applies monthly confidence decay to Wiki pages.

Part of the Lint loop (Loop 4). Scheduled via n8n cron (monthly).
Decay rate: -5% per month (multiply confidence by 0.95).
Archive threshold: confidence < 0.30 → move to wiki/archive/,
  update status to 'deprecated', exclude from INDEX.md and retrieval.

Cost: $0 (pure SQL + git operations). Safe to run on schedule.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from git import Repo
from git.exc import GitCommandError

from src.graphs.ingest_compile_graph import resolve_wiki_root
from src.lib.supabase import create_supabase_client, ensure_tenant_exists, insert_wiki_log_row
from src.modules.compile.models import WikiPage
from src.modules.compile.wiki_storage import render_page_markdown, wiki_page_relative_path
from src.modules.lint.models import DecayReport


def _safe_slug_filename(slug: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9._-]+", "-", slug.strip().lower()).strip("-")
    return cleaned or "untitled"


def _archive_relative_path(slug: str) -> str:
    return f"archive/{_safe_slug_filename(slug)}.md"


def _strip_slug_from_index(index_text: str, slug: str) -> str:
    lines = index_text.splitlines()
    kept: list[str] = []
    needle = f"`{slug}`"
    for line in lines:
        if needle in line and "/" in line:
            continue
        kept.append(line)
    return "\n".join(kept) + ("\n" if kept else "")


def run_confidence_decay(tenant_id: str) -> DecayReport:
    client = create_supabase_client()
    ensure_tenant_exists(client, tenant_id)
    wiki_root = resolve_wiki_root()
    repo = Repo(wiki_root)

    res = (
        client.table("wiki_pages")
        .select("*")
        .eq("tenant_id", tenant_id)
        .neq("status", "deprecated")
        .execute()
    )
    rows = getattr(res, "data", None) or []
    now_iso = datetime.now(timezone.utc).isoformat()
    archived_slugs: list[str] = []
    decayed = 0
    errors: list[str] = []
    decay_sync_paths: list[str] = []

    index_path = wiki_root / "index.md"
    index_text = index_path.read_text(encoding="utf-8") if index_path.is_file() else ""

    for row in rows:
        wid = str(row.get("id") or "")
        slug = str(row.get("slug") or "")
        if not wid or not slug:
            continue
        try:
            conf = float(row.get("confidence") or 0.0)
        except (TypeError, ValueError):
            conf = 0.0
        new_conf = round(conf * 0.95, 4)
        ptype = str(row.get("page_type") or "concept")
        title = str(row.get("title") or slug)
        body = str(row.get("content_markdown") or "")
        fm_raw = row.get("frontmatter") or {}
        fm: dict[str, Any] = dict(fm_raw) if isinstance(fm_raw, dict) else {}

        page = WikiPage(
            slug=slug,
            title=title,
            page_type=ptype,
            content_markdown=body,
            frontmatter=fm,
        )

        if new_conf < 0.30:
            fm["status"] = "deprecated"
            fm["confidence"] = new_conf
            fm["date_modified"] = now_iso[:10]
            deprecation_note = (
                f"\n\n---\n\n_Deprecated: confidence decay below 0.30 ({new_conf:.2f}) "
                f"— archived {now_iso[:10]}._\n"
            )
            page_arch = WikiPage(
                slug=slug,
                title=title,
                page_type=ptype,
                content_markdown=body + deprecation_note,
                frontmatter=fm,
            )
            old_rel = wiki_page_relative_path(page)
            arch_rel = _archive_relative_path(slug)
            old_path = wiki_root / old_rel
            arch_path = wiki_root / arch_rel
            arch_path.parent.mkdir(parents=True, exist_ok=True)
            arch_path.write_text(render_page_markdown(page_arch), encoding="utf-8")
            if old_path.is_file() and old_path.resolve() != arch_path.resolve():
                old_path.unlink()

            index_text = _strip_slug_from_index(index_text, slug)
            index_path.parent.mkdir(parents=True, exist_ok=True)
            index_path.write_text(index_text, encoding="utf-8")

            client.table("wiki_pages").update(
                {
                    "confidence": new_conf,
                    "status": "deprecated",
                    "content_markdown": page_arch.content_markdown,
                    "frontmatter": fm,
                    "updated_at": now_iso,
                },
            ).eq("id", wid).execute()

            repo.git.add(arch_rel, "index.md")
            try:
                repo.git.rm("-f", "--ignore-unmatch", "--", old_rel)
            except GitCommandError:
                pass
            try:
                repo.index.commit(
                    f"chore: archive {slug} (confidence decayed to {new_conf:.2f})",
                )
            except GitCommandError as exc:
                err = str(exc).lower()
                if "nothing to commit" not in err and "no changes" not in err:
                    errors.append(str(exc))

            archived_slugs.append(slug)
            decayed += 1
        else:
            fm["confidence"] = new_conf
            fm["date_modified"] = now_iso[:10]
            client.table("wiki_pages").update(
                {
                    "confidence": new_conf,
                    "frontmatter": fm,
                    "updated_at": now_iso,
                },
            ).eq("id", wid).execute()
            disk = wiki_root / wiki_page_relative_path(page)
            if disk.is_file():
                updated = WikiPage(
                    slug=slug,
                    title=title,
                    page_type=ptype,
                    content_markdown=body,
                    frontmatter=fm,
                )
                disk.write_text(render_page_markdown(updated), encoding="utf-8")
                decay_sync_paths.append(wiki_page_relative_path(updated))

    decay_sync_paths = sorted(set(decay_sync_paths))
    if decay_sync_paths:
        for rel in decay_sync_paths:
            if (wiki_root / rel).is_file():
                repo.index.add([rel])
        try:
            repo.index.commit("chore: sync wiki frontmatter after confidence decay")
        except GitCommandError as exc:
            err = str(exc).lower()
            if "nothing to commit" not in err and "no changes" not in err:
                errors.append(str(exc))

    try:
        insert_wiki_log_row(
            client,
            tenant_id=tenant_id,
            operation="decay",
            details={
                "pages_decayed": decayed,
                "pages_archived": len(archived_slugs),
                "archived_slugs": archived_slugs,
            },
            module="confidence_decay",
        )
    except Exception as exc:
        errors.append(f"wiki_log decay insert: {exc}")

    return DecayReport(
        tenant_id=tenant_id,
        ran_at=now_iso,
        pages_decayed=decayed,
        pages_archived=len(archived_slugs),
        archived_slugs=archived_slugs,
        errors=errors,
    )
