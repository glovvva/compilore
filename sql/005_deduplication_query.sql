-- Duplicate page candidates via chunk-0 cosine similarity (same tenant).
-- Idempotent: CREATE OR REPLACE + GRANT.

CREATE OR REPLACE FUNCTION public.find_duplicate_pages(p_tenant_id uuid)
RETURNS TABLE (
  page_a_slug text,
  page_a_title text,
  page_b_slug text,
  page_b_title text,
  similarity float
)
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
  SELECT
    wa.slug AS page_a_slug,
    wa.title AS page_a_title,
    wb.slug AS page_b_slug,
    wb.title AS page_b_title,
    (1.0::float - (a.embedding <=> b.embedding))::float AS similarity
  FROM public.document_chunks a
  INNER JOIN public.document_chunks b
    ON a.tenant_id = b.tenant_id
    AND a.wiki_page_id < b.wiki_page_id
    AND a.chunk_index = 0
    AND b.chunk_index = 0
  INNER JOIN public.wiki_pages wa
    ON wa.id = a.wiki_page_id AND wa.tenant_id = a.tenant_id
  INNER JOIN public.wiki_pages wb
    ON wb.id = b.wiki_page_id AND wb.tenant_id = b.tenant_id
  WHERE a.tenant_id = p_tenant_id
    AND a.embedding IS NOT NULL
    AND b.embedding IS NOT NULL
    AND (1.0::float - (a.embedding <=> b.embedding)) > 0.92
  ORDER BY similarity DESC;
$$;

GRANT EXECUTE ON FUNCTION public.find_duplicate_pages(uuid) TO service_role;
