"""
Simple PDF text adapter using PyMuPDF.

USE THIS FOR: Simple text-heavy PDFs (articles, reports,
  Markdown-heavy documents, single-column text)
USE docling_adapter.py FOR: Industrial catalogs, datasheets,
  any PDF with multi-column tables, engineering spec sheets,
  parametric data tables.

See docs/04_DECISIONS.md D-75 for the routing decision.
"""

from __future__ import annotations

from pathlib import Path

import fitz  # PyMuPDF

from .base_adapter import BaseIngestAdapter
from .models import IngestResult


def _page_separator(page_index: int, page_count: int) -> str:
    return f"\n\n---\nPage {page_index + 1} / {page_count}\n---\n\n"


class PdfTextIngestAdapter(BaseIngestAdapter):
    """Extracts embedded text from digital PDFs via PyMuPDF."""

    def can_handle(self, path: Path) -> bool:
        return path.suffix.lower() == ".pdf"

    def extract(self, path: Path) -> IngestResult:
        doc = fitz.open(path)
        try:
            page_count = len(doc)
            parts: list[str] = []
            for i in range(page_count):
                if i > 0:
                    parts.append(_page_separator(i, page_count))
                page = doc.load_page(i)
                parts.append(page.get_text() or "")
            body = "".join(parts).strip()
        finally:
            doc.close()
        return IngestResult(
            body=body,
            frontmatter={},
            source_path=path.resolve(),
            doc_type="pdf",
        )


def create_pdf_text_adapter() -> PdfTextIngestAdapter:
    """Factory for optional PDF ingest in the playground."""
    return PdfTextIngestAdapter()
