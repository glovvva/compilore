"""INDEX maintenance for the **Compile** loop.

Appends human-readable entries to ``index.md`` after each compile so the master
index stays navigable without scanning the tree.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from src.modules.compile.models import WikiPage
from src.modules.compile.wiki_storage import wiki_page_relative_path


def append_compiled_pages_to_index(wiki_root: Path, pages: list[WikiPage], *, document_title: str) -> None:
    """Append a dated block linking compiled pages (relative paths)."""
    index_path = wiki_root / "index.md"
    if not index_path.is_file():
        index_path.write_text(
            "---\ntitle: Compilore Wiki Index\ntype: index\n---\n\n# Compilore Wiki\n\n",
            encoding="utf-8",
        )

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "",
        f"### Compiled — {document_title} ({now})",
        "",
    ]
    for p in pages:
        rel = wiki_page_relative_path(p)
        lines.append(f"- [{p.title}]({rel}) — `{p.page_type}` / `{p.slug}`")
    lines.append("")

    with index_path.open("a", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
