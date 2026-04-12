-- D-16: Gatekeeper pre-check — top chunk cosine similarity vs synthesized answer embedding.
-- Idempotent: CREATE OR REPLACE + GRANT.
-- Apply in Supabase SQL editor if not already present.

CREATE OR REPLACE FUNCTION public.gatekeeper_precheck_top_similarity(
  p_tenant_id uuid,
  query_embedding vector(1536)
)
RETURNS TABLE (
  wiki_page_id uuid,
  slug text,
  page_type text,
  cosine_similarity float
)
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
  SELECT
    dc.wiki_page_id,
    wp.slug,
    wp.page_type,
    (1.0::float - (dc.embedding <=> query_embedding))::float AS cosine_similarity
  FROM public.document_chunks dc
  INNER JOIN public.wiki_pages wp
    ON wp.id = dc.wiki_page_id AND wp.tenant_id = dc.tenant_id
  WHERE dc.tenant_id = p_tenant_id
    AND dc.embedding IS NOT NULL
  ORDER BY dc.embedding <=> query_embedding
  LIMIT 1;
$$;

GRANT EXECUTE ON FUNCTION public.gatekeeper_precheck_top_similarity(uuid, vector(1536)) TO service_role;
