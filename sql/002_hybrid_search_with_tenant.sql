-- Service-role / backend hybrid search: same RRF idea as brief §4.3, but scoped by
-- explicit tenant_id (the stock hybrid_search() uses auth.uid()).
-- Idempotent: CREATE OR REPLACE + GRANT.

CREATE OR REPLACE FUNCTION public.hybrid_search_with_tenant(
  p_tenant_id uuid,
  query_text text,
  query_embedding vector(1536),
  match_count int DEFAULT 10,
  rrf_k int DEFAULT 60
)
RETURNS TABLE (
  chunk_id uuid,
  wiki_page_id uuid,
  chunk_text text,
  rrf_score float
)
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
  WITH semantic AS (
    SELECT dc.id, dc.wiki_page_id, dc.chunk_text,
      ROW_NUMBER() OVER (ORDER BY dc.embedding <=> query_embedding) AS rank
    FROM public.document_chunks dc
    WHERE dc.tenant_id = p_tenant_id
      AND dc.embedding IS NOT NULL
    ORDER BY dc.embedding <=> query_embedding
    LIMIT match_count * 2
  ),
  fulltext AS (
    SELECT dc.id, dc.wiki_page_id, dc.chunk_text,
      ROW_NUMBER() OVER (ORDER BY ts_rank_cd(dc.tsv, plainto_tsquery('simple', query_text)) DESC) AS rank
    FROM public.document_chunks dc
    WHERE dc.tenant_id = p_tenant_id
      AND dc.tsv @@ plainto_tsquery('simple', query_text)
    ORDER BY ts_rank_cd(dc.tsv, plainto_tsquery('simple', query_text)) DESC
    LIMIT match_count * 2
  ),
  combined AS (
    SELECT
      COALESCE(s.id, f.id) AS id,
      COALESCE(s.wiki_page_id, f.wiki_page_id) AS wiki_page_id,
      COALESCE(s.chunk_text, f.chunk_text) AS chunk_text,
      COALESCE(1.0::float / (rrf_k + s.rank), 0::float) + COALESCE(1.0::float / (rrf_k + f.rank), 0::float) AS score
    FROM semantic s
    FULL OUTER JOIN fulltext f ON s.id = f.id
  )
  SELECT c.id AS chunk_id, c.wiki_page_id, c.chunk_text, c.score::float AS rrf_score
  FROM combined c
  ORDER BY c.score DESC
  LIMIT match_count;
$$;

GRANT EXECUTE ON FUNCTION public.hybrid_search_with_tenant(uuid, text, vector(1536), int, int) TO service_role;
GRANT EXECUTE ON FUNCTION public.hybrid_search_with_tenant(uuid, text, vector(1536), int, int) TO authenticated;
