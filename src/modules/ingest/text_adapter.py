"""Plain-text ingest adapter for the **Ingest** loop.

Handles ``.txt`` as UTF-8 text with no frontmatter. Output matches ``IngestResult``
so **Compile** treats it like Markdown minus YAML metadata.
"""

from __future__ import annotations

from pathlib import Path

from .base_adapter import BaseIngestAdapter
from .models import IngestResult


class TextIngestAdapter(BaseIngestAdapter):
    """Reads plain text files."""

    def can_handle(self, path: Path) -> bool:
        return path.suffix.lower() == ".txt"

    def extract(self, path: Path) -> IngestResult:
        body = path.read_text(encoding="utf-8")
        return IngestResult(
            body=body,
            frontmatter={},
            source_path=path.resolve(),
            doc_type="text",
        )


def create_text_adapter() -> TextIngestAdapter:
    """Factory for wiring into LangGraph ingest nodes."""
    return TextIngestAdapter()
