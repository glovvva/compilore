"""
text_paste_adapter.py — Direct text paste ingestion adapter.

Part of the Ingest loop (Loop 1) in Karpathy's 4-loop architecture.
Handles raw text submitted directly by the user (snippets, meeting notes,
emails, any text already in clipboard). Simplest possible adapter — no
extraction needed, text arrives ready for Compile loop.
"""

from __future__ import annotations

from pathlib import Path

from .models import IngestResult

# Synthetic path for IngestResult (no on-disk file for paste).
_PASTE_SOURCE_PATH = Path("-paste-")


def paste_to_ingest_result(content: str, title: str = "Pasted Text") -> IngestResult:
    """
    Accept raw text string and return IngestResult ready for compilation.

    Args:
        content: Raw text content pasted by the user.
        title: Optional title for the document. Defaults to 'Pasted Text'.

    Returns:
        IngestResult with cleaned text ready for Compile loop.
    """
    cleaned = content.strip()
    if not cleaned:
        msg = "Pasted content is empty."
        raise ValueError(msg)

    t = (title or "Pasted Text").strip() or "Pasted Text"
    return IngestResult(
        body=cleaned,
        frontmatter={
            "title": t,
            "char_count": len(cleaned),
            "word_count": len(cleaned.split()),
        },
        source_path=_PASTE_SOURCE_PATH,
        doc_type="paste",
    )
