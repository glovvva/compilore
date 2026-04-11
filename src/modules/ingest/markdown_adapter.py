"""Markdown ingest adapter for the **Ingest** loop (Phase 1 primary).

Reads ``.md`` sources: YAML frontmatter and body feed the **Compile** loop's
wiki generator. Uses ``python-frontmatter`` for parsing.
"""

from __future__ import annotations

from pathlib import Path

import frontmatter

from .base_adapter import BaseIngestAdapter
from .models import IngestResult


class MarkdownIngestAdapter(BaseIngestAdapter):
    """Reads Markdown files with optional YAML frontmatter."""

    def can_handle(self, path: Path) -> bool:
        return path.suffix.lower() == ".md"

    def extract(self, path: Path) -> IngestResult:
        raw = path.read_text(encoding="utf-8")
        post = frontmatter.loads(raw)
        metadata = dict(post.metadata) if post.metadata else {}
        return IngestResult(
            body=post.content or "",
            frontmatter=metadata,
            source_path=path.resolve(),
            doc_type="markdown",
        )


def create_markdown_adapter() -> MarkdownIngestAdapter:
    """Factory for dependency injection / graph nodes."""
    return MarkdownIngestAdapter()
