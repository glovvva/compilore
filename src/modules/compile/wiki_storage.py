"""Write ``WikiPage`` bodies to the Git-versioned ``wiki/`` tree."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from src.modules.compile.models import WikiPage


def _safe_slug_filename(slug: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9._-]+", "-", slug.strip().lower()).strip("-")
    return cleaned or "untitled"


def wiki_page_relative_path(page: WikiPage) -> str:
    """Relative path from wiki root for this page type."""
    name = f"{_safe_slug_filename(page.slug)}.md"
    if page.page_type == "concept":
        return f"concepts/{name}"
    if page.page_type == "entity":
        return f"entities/{name}"
    if page.page_type == "source_summary":
        return f"sources/{name}"
    if page.page_type == "output":
        return f"outputs/{name}"
    if page.page_type == "index":
        # Never clobber root ``index.md``; treat rare index-type pages as concepts.
        return f"concepts/{name}"
    msg = f"Unknown page_type: {page.page_type}"
    raise ValueError(msg)


def render_page_markdown(page: WikiPage) -> str:
    """Full file contents: YAML frontmatter + body (brief §4.4 style)."""
    fm = page.frontmatter.copy() if page.frontmatter else {}
    if "title" not in fm:
        fm["title"] = page.title
    if "type" not in fm:
        fm["type"] = page.page_type
    header = yaml.safe_dump(
        fm,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
    ).rstrip()
    body = page.content_markdown.strip()
    return f"---\n{header}\n---\n\n{body}\n"


def write_wiki_page_files(wiki_root: Path, pages: list[WikiPage]) -> list[str]:
    """Write each page under ``wiki_root``; return relative paths for Git staging."""
    written: list[str] = []
    for page in pages:
        rel = wiki_page_relative_path(page)
        out = wiki_root / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render_page_markdown(page), encoding="utf-8")
        written.append(rel)
    return written
