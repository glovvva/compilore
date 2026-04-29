export type WikiPageType = "concept" | "entity" | "source_summary" | "output" | "index";

/** Row shape for wiki list API (ingest/compile loop output in Supabase). */
export interface WikiPage {
  id: string;
  slug: string;
  title: string;
  page_type: WikiPageType;
  confidence: number;
  updated_at: string;
  related: string[];
  frontmatter?: Record<string, unknown>;
}

/** Full page for inspector (includes body from `content_markdown`). */
export interface WikiPageDetail extends WikiPage {
  content_markdown: string;
  frontmatter: Record<string, unknown>;
  source_documents: string[] | null;
  status: string | null;
  tenant_id: string;
  created_at: string;
}
