"""
Docling PDF Adapter — Phase 2 pull-forward for B2B industrial catalogs.

Replaces PyMuPDF for complex PDFs containing engineering tables,
parametric specifications, and multi-column layouts.

WHY THIS EXISTS (context for future engineers):
Standard PyMuPDF + chunking splits table headers from values.
A column header "Max Torque (Nm)" gets separated from its value "25"
by the chunk boundary. The vector DB stores them independently.
When a technical advisor queries "what is the max torque of KOLVER
ESD model", the system retrieves the header but not the value,
causing the LLM to hallucinate or return "not found".

Docling TableFormer ACCURATE mode preserves table structure as
Markdown tables, keeping headers and values co-located in the
same chunk. This is the correct solution for industrial catalogs.

MEMORY CONSTRAINTS (Hetzner 8GB VPS):
- Set OMP_NUM_THREADS=1 to prevent CPU thread explosion
- Process page-by-page, not full document at once
- Call gc.collect() after each page
- If OOM occurs: fall back to pdf_text_adapter.py (PyMuPDF)
  and log warning to wiki_log

SCOPE:
- Use for: manufacturer catalogs, datasheets, technical specs,
  calibration documents, ISO certificates with tables
- Do NOT use for: simple text PDFs, Markdown, plain text
  (those use markdown_adapter.py / text_adapter.py)
"""

from pathlib import Path
from typing import Generator
import gc
import logging
import os

logger = logging.getLogger(__name__)

# Memory safety for Hetzner 8GB VPS
os.environ.setdefault("OMP_NUM_THREADS", "1")


class DoclingAdapter:
    """
    Extracts structured text from complex PDFs using Docling.

    Preserves table structure as Markdown tables.
    Falls back to PyMuPDF on OOM or Docling unavailability.

    Usage:
        adapter = DoclingAdapter()
        chunks = list(adapter.extract(Path("catalog.pdf")))
    """

    def __init__(self, mode: str = "ACCURATE"):
        """
        Args:
            mode: TableFormer mode.
                  "ACCURATE" = best table extraction, slower.
                  "FAST" = faster, less accurate for complex tables.
                  Use ACCURATE for industrial catalogs.
        """
        self.mode = mode
        self._docling_available = self._check_docling()

    def _check_docling(self) -> bool:
        try:
            import docling  # noqa: F401

            return True
        except ImportError:
            logger.warning(
                "Docling not installed. "
                "Falling back to PyMuPDF for all PDFs. "
                "Run: pip install docling"
            )
            return False

    def extract(self, pdf_path: Path) -> Generator[dict, None, None]:
        """
        Extract text chunks from PDF, preserving table structure.

        Yields dicts with:
            - text: str (Markdown-formatted, tables as | col | col |)
            - page_number: int
            - chunk_type: "table" | "text" | "heading"
            - source_path: str

        Falls back to PyMuPDF if Docling unavailable or OOM.
        """
        if not self._docling_available:
            yield from self._pymupdf_fallback(pdf_path)
            return

        try:
            yield from self._docling_extract(pdf_path)
        except MemoryError:
            logger.error(
                f"OOM processing {pdf_path} with Docling. "
                "Falling back to PyMuPDF."
            )
            gc.collect()
            yield from self._pymupdf_fallback(pdf_path)
        except Exception as e:
            logger.error(
                f"Docling failed on {pdf_path}: {e}. "
                "Falling back to PyMuPDF."
            )
            yield from self._pymupdf_fallback(pdf_path)

    def _docling_extract(
        self, pdf_path: Path
    ) -> Generator[dict, None, None]:
        """
        Core Docling extraction with TableFormer.
        Processes page-by-page to manage memory.
        """
        from docling.document_converter import DocumentConverter
        from docling.datamodel.pipeline_options import (
            PdfPipelineOptions,
            TableFormerMode,
        )
        from docling.datamodel.base_models import InputFormat
        from docling.document_converter import PdfFormatOption

        mode_enum = (
            TableFormerMode.ACCURATE
            if self.mode == "ACCURATE"
            else TableFormerMode.FAST
        )

        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_table_structure = True
        pipeline_options.table_structure_options.mode = mode_enum
        pipeline_options.table_structure_options.do_cell_matching = True

        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_options=pipeline_options
                )
            }
        )

        result = converter.convert(str(pdf_path))
        doc = result.document

        for page_no, page in enumerate(doc.pages, start=1):
            try:
                # Extract tables first (highest value for B2B catalogs)
                for table in page.tables:
                    md_table = table.export_to_markdown()
                    if md_table.strip():
                        yield {
                            "text": md_table,
                            "page_number": page_no,
                            "chunk_type": "table",
                            "source_path": str(pdf_path),
                        }

                # Extract text blocks
                for block in page.body:
                    text = block.text.strip() if hasattr(
                        block, "text"
                    ) else ""
                    if len(text) > 50:  # skip noise
                        yield {
                            "text": text,
                            "page_number": page_no,
                            "chunk_type": "text",
                            "source_path": str(pdf_path),
                        }

            except Exception as e:
                logger.warning(
                    f"Page {page_no} extraction failed: {e}. Skipping."
                )
            finally:
                gc.collect()

    def _pymupdf_fallback(
        self, pdf_path: Path
    ) -> Generator[dict, None, None]:
        """
        PyMuPDF fallback. Used when Docling unavailable or OOM.
        WARNING: Does NOT preserve table structure.
        Tables will be extracted as flat text — headers may be
        separated from values by chunk boundaries.
        Log this as a quality warning for B2B catalog processing.
        """
        import fitz  # PyMuPDF

        logger.warning(
            f"Using PyMuPDF fallback for {pdf_path}. "
            "Table structure NOT preserved. "
            "Parametric queries may return incorrect values."
        )

        doc = fitz.open(str(pdf_path))
        for page_no, page in enumerate(doc, start=1):
            text = page.get_text()
            if text.strip():
                yield {
                    "text": text,
                    "page_number": page_no,
                    "chunk_type": "text",
                    "source_path": str(pdf_path),
                }
            gc.collect()
        doc.close()
