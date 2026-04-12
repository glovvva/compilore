-- Add optional module provenance for wiki_log and documents (GapRoll-style tracing).
-- Idempotent: IF NOT EXISTS. Run in Supabase SQL editor (alongside other 004_* migrations as needed).

ALTER TABLE wiki_log ADD COLUMN IF NOT EXISTS module TEXT;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS module TEXT;

COMMENT ON COLUMN wiki_log.module IS 'Source module: wiki_generator | gatekeeper | hybrid_search | synthesizer | confidence_decay | orphan_detector';
COMMENT ON COLUMN documents.module IS 'Ingestion adapter: markdown_adapter | text_adapter | pdf_text_adapter | url_adapter | text_paste_adapter';
