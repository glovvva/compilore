"""Shared ingest types for the **Ingest** loop."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal


@dataclass(frozen=True)
class IngestResult:
    """Normalized document payload passed from Ingest adapters to **Compile**.

    ``body`` is the main text (Markdown body for ``.md``, full file for ``.txt``).
    ``frontmatter`` is YAML metadata for Markdown, URL metadata for ``url``, or
    empty for plain text / PDF.
    """

    body: str
    frontmatter: dict[str, Any]
    source_path: Path
    doc_type: Literal["markdown", "text", "pdf", "url", "paste"]

    def display_title(self) -> str:
        """Prefer frontmatter ``title`` (markdown / url), then filename stem."""
        if self.frontmatter:
            raw = self.frontmatter.get("title")
            if isinstance(raw, str) and raw.strip():
                return raw.strip()
        return self.source_path.stem


def ingest_result_to_mapping(result: IngestResult) -> dict[str, Any]:
    """Serialize for LangGraph state (JSON-friendly)."""
    return {
        "body": result.body,
        "frontmatter": result.frontmatter,
        "source_path": str(result.source_path.resolve()),
        "doc_type": result.doc_type,
    }


def ingest_result_from_mapping(data: dict[str, Any]) -> IngestResult:
    """Restore ``IngestResult`` from graph state."""
    return IngestResult(
        body=data["body"],
        frontmatter=dict(data.get("frontmatter") or {}),
        source_path=Path(data["source_path"]),
        doc_type=data["doc_type"],
    )
