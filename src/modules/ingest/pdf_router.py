"""
PDF Adapter Router — selects correct PDF extraction adapter based on file.

Routing logic:
- Default: DoclingAdapter (TableFormer ACCURATE)
  Handles: industrial catalogs, datasheets, spec sheets with tables
- Fallback: pdf_text_adapter (PyMuPDF)
  Used when: Docling fails, OOM, or FORCE_PYMUPDF=true in env

The router is the ONLY place that decides which adapter processes a PDF.
Never call DoclingAdapter or pdf_text_adapter directly from route handlers.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def extract_pdf(pdf_path: Path) -> List[Dict[str, Any]]:
    """
    Route PDF to correct adapter and return list of chunks.

    Each chunk: {
        "text": str,
        "page_number": int,
        "chunk_type": "table" | "text",
        "source_path": str,
        "adapter_used": "docling" | "pymupdf"
    }
    """
    force_pymupdf = os.getenv("FORCE_PYMUPDF", "false").lower() == "true"

    if force_pymupdf:
        logger.info(f"FORCE_PYMUPDF=true, using PyMuPDF for {pdf_path.name}")
        return _pymupdf_extract(pdf_path)

    try:
        from src.modules.ingest.docling_adapter import DoclingAdapter

        adapter = DoclingAdapter(mode="ACCURATE")
        chunks = list(adapter.extract(pdf_path))

        if not chunks:
            logger.warning(
                f"Docling returned 0 chunks for {pdf_path.name}. "
                "Falling back to PyMuPDF."
            )
            return _pymupdf_extract(pdf_path)

        # Tag chunks with adapter info (preserve pymupdf if Docling fell back internally)
        for chunk in chunks:
            chunk.setdefault("adapter_used", "docling")

        logger.info(
            f"Docling extracted {len(chunks)} chunks from "
            f"{pdf_path.name} "
            f"({sum(1 for c in chunks if c['chunk_type']=='table')} tables)"
        )
        return chunks

    except MemoryError:
        logger.error(
            f"OOM running Docling on {pdf_path.name}. "
            "Falling back to PyMuPDF."
        )
        return _pymupdf_extract(pdf_path)
    except Exception as e:
        logger.error(
            f"Docling failed on {pdf_path.name}: {e}. "
            "Falling back to PyMuPDF."
        )
        return _pymupdf_extract(pdf_path)


def _pymupdf_extract(pdf_path: Path) -> List[Dict[str, Any]]:
    """PyMuPDF fallback. No table structure preservation."""
    import fitz

    logger.warning(
        f"Using PyMuPDF for {pdf_path.name}. "
        "Table structure NOT preserved."
    )

    chunks = []
    doc = fitz.open(str(pdf_path))
    for page_no, page in enumerate(doc, start=1):
        text = page.get_text()
        if text.strip():
            chunks.append(
                {
                    "text": text,
                    "page_number": page_no,
                    "chunk_type": "text",
                    "source_path": str(pdf_path),
                    "adapter_used": "pymupdf",
                }
            )
    doc.close()
    return chunks
