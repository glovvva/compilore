-- Add organization_id to all tenant tables
-- Phase 1: bartek-playground gets its own org_id
-- Phase 2: hermes-pilot gets its own org_id
-- This prevents cross-org data leakage in team model

ALTER TABLE documents 
  ADD COLUMN IF NOT EXISTS organization_id UUID NOT NULL 
  DEFAULT 'a6d3721a-0000-0000-0000-000000000001'::uuid;

ALTER TABLE wiki_pages 
  ADD COLUMN IF NOT EXISTS organization_id UUID NOT NULL 
  DEFAULT 'a6d3721a-0000-0000-0000-000000000001'::uuid;

ALTER TABLE document_chunks 
  ADD COLUMN IF NOT EXISTS organization_id UUID NOT NULL 
  DEFAULT 'a6d3721a-0000-0000-0000-000000000001'::uuid;

ALTER TABLE wiki_log 
  ADD COLUMN IF NOT EXISTS organization_id UUID NOT NULL 
  DEFAULT 'a6d3721a-0000-0000-0000-000000000001'::uuid;

-- Create organizations table
CREATE TABLE IF NOT EXISTS organizations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  slug TEXT NOT NULL UNIQUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Seed existing orgs
INSERT INTO organizations (id, name, slug) VALUES
  ('a6d3721a-0000-0000-0000-000000000001', 
   'Bartek Playground', 'bartek-playground'),
  ('a6d3721a-0000-0000-0000-000000000002', 
   'HermesTools Pilot', 'hermes-pilot')
ON CONFLICT (slug) DO NOTHING;

-- Create org_members table (user → org mapping)
CREATE TABLE IF NOT EXISTS org_members (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  organization_id UUID NOT NULL REFERENCES organizations(id) 
    ON DELETE CASCADE,
  role TEXT NOT NULL DEFAULT 'member' 
    CHECK (role IN ('owner', 'admin', 'member')),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, organization_id)
);

-- Update RLS policies to filter by organization_id
-- Drop old per-user policies
DROP POLICY IF EXISTS "tenant_isolation" ON documents;
DROP POLICY IF EXISTS "tenant_isolation" ON wiki_pages;
DROP POLICY IF EXISTS "tenant_isolation" ON document_chunks;
DROP POLICY IF EXISTS "tenant_isolation" ON wiki_log;

-- New org-scoped policies
CREATE POLICY "org_isolation" ON documents FOR ALL
  USING (organization_id IN (
    SELECT organization_id FROM org_members 
    WHERE user_id = auth.uid()
  ));

CREATE POLICY "org_isolation" ON wiki_pages FOR ALL
  USING (organization_id IN (
    SELECT organization_id FROM org_members 
    WHERE user_id = auth.uid()
  ));

CREATE POLICY "org_isolation" ON document_chunks FOR ALL
  USING (organization_id IN (
    SELECT organization_id FROM org_members 
    WHERE user_id = auth.uid()
  ));

CREATE POLICY "org_isolation" ON wiki_log FOR ALL
  USING (organization_id IN (
    SELECT organization_id FROM org_members 
    WHERE user_id = auth.uid()
  ));

-- Update hybrid_search function to respect org boundary
CREATE OR REPLACE FUNCTION hybrid_search(
  query_text TEXT,
  query_embedding vector(1536),
  match_count INT DEFAULT 10,
  rrf_k INT DEFAULT 60,
  p_organization_id UUID DEFAULT NULL
)
RETURNS TABLE (
  chunk_id UUID, 
  wiki_page_id UUID, 
  chunk_text TEXT, 
  rrf_score FLOAT
)
LANGUAGE sql STABLE SECURITY DEFINER
AS $$
  WITH org_id AS (
    SELECT COALESCE(
      p_organization_id,
      (SELECT organization_id FROM org_members 
       WHERE user_id = auth.uid() LIMIT 1)
    ) AS id
  ),
  semantic AS (
    SELECT dc.id, dc.wiki_page_id, dc.chunk_text,
      ROW_NUMBER() OVER (
        ORDER BY dc.embedding <=> query_embedding
      ) AS rank
    FROM document_chunks dc, org_id
    WHERE dc.organization_id = org_id.id
    ORDER BY dc.embedding <=> query_embedding
    LIMIT match_count * 2
  ),
  fulltext AS (
    SELECT dc.id, dc.wiki_page_id, dc.chunk_text,
      ROW_NUMBER() OVER (
        ORDER BY ts_rank_cd(
          dc.tsv, plainto_tsquery('simple', query_text)
        ) DESC
      ) AS rank
    FROM document_chunks dc, org_id
    WHERE dc.organization_id = org_id.id
      AND dc.tsv @@ plainto_tsquery('simple', query_text)
    ORDER BY ts_rank_cd(
      dc.tsv, plainto_tsquery('simple', query_text)
    ) DESC
    LIMIT match_count * 2
  ),
  combined AS (
    SELECT
      COALESCE(s.id, f.id) AS id,
      COALESCE(s.wiki_page_id, f.wiki_page_id) AS wiki_page_id,
      COALESCE(s.chunk_text, f.chunk_text) AS chunk_text,
      COALESCE(1.0 / (rrf_k + s.rank), 0) + 
      COALESCE(1.0 / (rrf_k + f.rank), 0) AS score
    FROM semantic s
    FULL OUTER JOIN fulltext f ON s.id = f.id
  )
  SELECT id, wiki_page_id, chunk_text, score
  FROM combined 
  ORDER BY score DESC 
  LIMIT match_count;
$$;

-- Add GIN index on organization_id for query performance
CREATE INDEX IF NOT EXISTS idx_documents_org_id 
  ON documents(organization_id);
CREATE INDEX IF NOT EXISTS idx_wiki_pages_org_id 
  ON wiki_pages(organization_id);
CREATE INDEX IF NOT EXISTS idx_chunks_org_id 
  ON document_chunks(organization_id);
