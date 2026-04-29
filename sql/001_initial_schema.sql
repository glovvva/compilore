-- Compilore initial schema (COMPILORE_PROJECT_BRIEF_v2.md §4.3)
-- Idempotent: safe to re-run in Supabase SQL editor.

-- -----------------------------------------------------------------------------
-- Extensions
-- -----------------------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- -----------------------------------------------------------------------------
-- Tables
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.tenants (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.user_profiles (
  id UUID PRIMARY KEY REFERENCES auth.users (id) ON DELETE CASCADE,
  tenant_id UUID NOT NULL REFERENCES public.tenants (id),
  role TEXT DEFAULT 'user',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES public.tenants (id),
  title TEXT NOT NULL,
  source_url TEXT,
  file_path TEXT,
  doc_type TEXT DEFAULT 'markdown',
  status TEXT DEFAULT 'pending',
  authority_tier INT DEFAULT 3 CHECK (authority_tier BETWEEN 1 AND 4),
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.wiki_pages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES public.tenants (id),
  slug TEXT NOT NULL,
  title TEXT NOT NULL,
  page_type TEXT NOT NULL,
  content_markdown TEXT NOT NULL,
  frontmatter JSONB DEFAULT '{}',
  source_documents UUID[] DEFAULT '{}',
  confidence NUMERIC(3,2) DEFAULT 0.90,
  status TEXT DEFAULT 'draft',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (tenant_id, slug)
);

CREATE TABLE IF NOT EXISTS public.document_chunks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES public.tenants (id),
  wiki_page_id UUID REFERENCES public.wiki_pages (id) ON DELETE CASCADE,
  document_id UUID REFERENCES public.documents (id) ON DELETE CASCADE,
  chunk_text TEXT NOT NULL,
  chunk_index INT NOT NULL,
  embedding vector(1536),
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  tsv tsvector GENERATED ALWAYS AS (to_tsvector('simple', chunk_text)) STORED
);

CREATE TABLE IF NOT EXISTS public.wiki_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES public.tenants (id),
  operation TEXT NOT NULL,
  details JSONB NOT NULL,
  tokens_used INT DEFAULT 0,
  cost_usd NUMERIC(10,6) DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- Indexes
-- -----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_chunks_tsv ON public.document_chunks USING GIN (tsv);

CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON public.document_chunks
  USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64);

-- -----------------------------------------------------------------------------
-- Row level security (brief §4.3)
-- -----------------------------------------------------------------------------
ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.wiki_pages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.document_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.wiki_log ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS tenant_isolation ON public.documents;
CREATE POLICY tenant_isolation ON public.documents
  FOR ALL
  USING (tenant_id = (SELECT tenant_id FROM public.user_profiles WHERE id = auth.uid()))
  WITH CHECK (tenant_id = (SELECT tenant_id FROM public.user_profiles WHERE id = auth.uid()));

DROP POLICY IF EXISTS tenant_isolation ON public.wiki_pages;
CREATE POLICY tenant_isolation ON public.wiki_pages
  FOR ALL
  USING (tenant_id = (SELECT tenant_id FROM public.user_profiles WHERE id = auth.uid()))
  WITH CHECK (tenant_id = (SELECT tenant_id FROM public.user_profiles WHERE id = auth.uid()));

DROP POLICY IF EXISTS tenant_isolation ON public.document_chunks;
CREATE POLICY tenant_isolation ON public.document_chunks
  FOR ALL
  USING (tenant_id = (SELECT tenant_id FROM public.user_profiles WHERE id = auth.uid()))
  WITH CHECK (tenant_id = (SELECT tenant_id FROM public.user_profiles WHERE id = auth.uid()));

DROP POLICY IF EXISTS tenant_isolation ON public.wiki_log;
CREATE POLICY tenant_isolation ON public.wiki_log
  FOR ALL
  USING (tenant_id = (SELECT tenant_id FROM public.user_profiles WHERE id = auth.uid()))
  WITH CHECK (tenant_id = (SELECT tenant_id FROM public.user_profiles WHERE id = auth.uid()));

-- -----------------------------------------------------------------------------
-- Hybrid search (JWT / auth.uid() — brief §4.3)
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION public.hybrid_search(
  query_text TEXT,
  query_embedding vector(1536),
  match_count INT DEFAULT 10,
  rrf_k INT DEFAULT 60
)
RETURNS TABLE (
  chunk_id UUID,
  wiki_page_id UUID,
  chunk_text TEXT,
  rrf_score FLOAT
)
LANGUAGE sql
STABLE
SET search_path = public
AS $$
  WITH semantic AS (
    SELECT dc.id, dc.wiki_page_id, dc.chunk_text,
      COALESCE(d.authority_tier, 3) AS authority_tier,
      NULLIF(wp.frontmatter->>'last_verified', '') AS last_verified_raw,
      ROW_NUMBER() OVER (ORDER BY dc.embedding <=> query_embedding) AS rank
    FROM public.document_chunks dc
    LEFT JOIN public.documents d ON d.id = dc.document_id
    LEFT JOIN public.wiki_pages wp ON wp.id = dc.wiki_page_id
    WHERE dc.tenant_id = (SELECT up.tenant_id FROM public.user_profiles up WHERE up.id = auth.uid())
      AND dc.embedding IS NOT NULL
    ORDER BY dc.embedding <=> query_embedding
    LIMIT match_count * 2
  ),
  fulltext AS (
    SELECT dc.id, dc.wiki_page_id, dc.chunk_text,
      COALESCE(d.authority_tier, 3) AS authority_tier,
      NULLIF(wp.frontmatter->>'last_verified', '') AS last_verified_raw,
      ROW_NUMBER() OVER (ORDER BY ts_rank_cd(dc.tsv, plainto_tsquery('simple', query_text)) DESC) AS rank
    FROM public.document_chunks dc
    LEFT JOIN public.documents d ON d.id = dc.document_id
    LEFT JOIN public.wiki_pages wp ON wp.id = dc.wiki_page_id
    WHERE dc.tenant_id = (SELECT up.tenant_id FROM public.user_profiles up WHERE up.id = auth.uid())
      AND dc.tsv @@ plainto_tsquery('simple', query_text)
    ORDER BY ts_rank_cd(dc.tsv, plainto_tsquery('simple', query_text)) DESC
    LIMIT match_count * 2
  ),
  combined AS (
    SELECT
      COALESCE(s.id, f.id) AS id,
      COALESCE(s.wiki_page_id, f.wiki_page_id) AS wiki_page_id,
      COALESCE(s.chunk_text, f.chunk_text) AS chunk_text,
      COALESCE(s.authority_tier, f.authority_tier, 3) AS authority_tier,
      COALESCE(s.last_verified_raw, f.last_verified_raw) AS last_verified_raw,
      -- Scaffold only: keep score neutral until authority/recency business rules ship.
      1.0::float AS authority_multiplier,
      1.0::float AS recency_multiplier,
      (
        COALESCE(1.0::float / (rrf_k + s.rank), 0::float)
        + COALESCE(1.0::float / (rrf_k + f.rank), 0::float)
      ) * 1.0::float * 1.0::float AS score
    FROM semantic s
    FULL OUTER JOIN fulltext f ON s.id = f.id
  )
  SELECT c.id AS chunk_id, c.wiki_page_id, c.chunk_text, c.score::float AS rrf_score
  FROM combined c
  ORDER BY c.score DESC
  LIMIT match_count;
$$;

GRANT EXECUTE ON FUNCTION public.hybrid_search(TEXT, vector(1536), INT, INT) TO authenticated;
GRANT EXECUTE ON FUNCTION public.hybrid_search(TEXT, vector(1536), INT, INT) TO service_role;
