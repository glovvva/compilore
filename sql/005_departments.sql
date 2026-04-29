-- Department table
CREATE TABLE departments (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  name text NOT NULL,
  slug text NOT NULL,
  visibility text NOT NULL DEFAULT 'private'
    CHECK (visibility IN ('private', 'tenant_wide')),
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE(tenant_id, slug)
);

-- Add department_id to wiki_pages (NULL = tenant-wide)
ALTER TABLE wiki_pages
  ADD COLUMN department_id uuid REFERENCES departments(id) ON DELETE SET NULL;

-- Add department_id to documents
ALTER TABLE documents
  ADD COLUMN department_id uuid REFERENCES departments(id) ON DELETE SET NULL;

-- RLS: enable on departments
ALTER TABLE departments ENABLE ROW LEVEL SECURITY;

-- Policy: user can see departments in their tenant
DROP POLICY IF EXISTS "tenant_departments" ON departments;
CREATE POLICY "tenant_departments" ON departments
  FOR ALL USING (
    tenant_id = (
      SELECT tenant_id FROM user_profiles WHERE id = auth.uid()
    )
  );

-- Policy: wiki_pages visibility
-- Private department pages: only department members
-- tenant_wide or NULL: all tenant members
DROP POLICY IF EXISTS tenant_isolation ON wiki_pages;
DROP POLICY IF EXISTS "wiki_pages_department_access" ON wiki_pages;
CREATE POLICY "wiki_pages_department_access" ON wiki_pages
  FOR ALL USING (
    tenant_id = (SELECT tenant_id FROM user_profiles WHERE id = auth.uid())
    AND (
      department_id IS NULL
      OR EXISTS (
        SELECT 1 FROM departments d
        WHERE d.id = department_id
        AND d.visibility = 'tenant_wide'
      )
      OR department_id IN (
        SELECT department_id FROM user_profiles WHERE id = auth.uid()
      )
    )
  );

-- Add department_id to user_profiles for membership
ALTER TABLE user_profiles
  ADD COLUMN department_id uuid REFERENCES departments(id) ON DELETE SET NULL;
