# Technical Advisor Adapter (Phase 2 Stub)

This directory is reserved for the Technical Advisor ICP adapter stack.

## Scope
- **Phase 1 (current):** Uses existing `pdf_text_adapter.py` plus
  `src/config/prompts/compile_technical_catalog.md`.
- **Phase 2 (planned):** Add Docling-based extraction for manufacturer catalogs,
  especially table-heavy PDFs and technical specification matrices.

## Why this exists
Industrial catalogs are often table-dense. PyMuPDF text extraction can lose table
structure, making parameter parsing noisy. Docling integration is the planned
upgrade path for higher-fidelity extraction.

## Current limitation
- Some PDF tables may not extract cleanly in Phase 1.
- Prompt-based normalization mitigates this, but cannot fully restore missing table
  structure when source extraction is lossy.
