/**
 * Mock wiki graph for the workspace UI (no API yet).
 * Mirrors future CONCEPTS / ENTITIES / SOURCES / OUTPUTS sections.
 */

export type WikiSection = "concepts" | "entities" | "sources" | "outputs";

export interface MockWikiPage {
  id: string;
  slug: string;
  title: string;
  section: WikiSection;
  confidence: number;
  excerpt: string;
  frontmatter: Record<string, string>;
  bodyMarkdown: string;
  relatedSlugs: string[];
  sourceRefs?: string[];
}

export interface MockWikiStats {
  totalPages: number;
  lastCompileAt: string;
  costThisMonthUsd: number;
  concepts: number;
  entities: number;
  sources: number;
  outputs: number;
}

export interface MockQueryResponse {
  queryType: "synthesis" | "factual" | "comparison";
  confidence: number;
  costUsd: number;
  bodyMarkdown: string;
  sourceSlugs: string[];
  gatekeeper?: "saved" | "discarded";
  gatekeeperDetail?: string;
}

export const MOCK_WIKI_STATS: MockWikiStats = {
  totalPages: 47,
  lastCompileAt: "2026-04-10T14:22:00Z",
  costThisMonthUsd: 2.41,
  concepts: 18,
  entities: 9,
  sources: 14,
  outputs: 6,
};

export const MOCK_WIKI_PAGES: MockWikiPage[] = [
  {
    id: "1",
    slug: "compounding-loop",
    title: "Compounding loop",
    section: "concepts",
    confidence: 0.88,
    excerpt:
      "The compounding loop ties ingest → compile → query → lint so each pass improves the wiki. Gatekeeper decides whether synthesized answers become durable outputs…",
    frontmatter: { type: "concept", tier: "core" },
    bodyMarkdown:
      "The **compounding loop** connects [[ingest-pipeline]] to [[query-graph]]. See also [[gatekeeper]].",
    relatedSlugs: ["ingest-pipeline", "query-graph", "gatekeeper"],
  },
  {
    id: "2",
    slug: "ingest-pipeline",
    title: "Ingest pipeline",
    section: "concepts",
    confidence: 0.72,
    excerpt:
      "Documents flow through adapters (PDF, URL, paste) into normalized markdown, then embedding and Supabase chunk storage before git commits…",
    frontmatter: { type: "concept" },
    bodyMarkdown: "Handles uploads and URLs before [[compile-stage]].",
    relatedSlugs: ["compile-stage"],
  },
  {
    id: "3",
    slug: "query-graph",
    title: "Query graph",
    section: "concepts",
    confidence: 0.91,
    excerpt:
      "Hybrid search over tenant-scoped chunks, synthesis with Sonnet, Haiku gatekeeper for novelty and cost control…",
    frontmatter: { type: "concept", tier: "core" },
    bodyMarkdown: "Uses [[hybrid-search]] and [[synthesizer]].",
    relatedSlugs: ["hybrid-search", "synthesizer"],
  },
  {
    id: "4",
    slug: "gatekeeper",
    title: "Gatekeeper",
    section: "concepts",
    confidence: 0.65,
    excerpt:
      "Lightweight model evaluates whether an answer should be persisted under wiki/outputs/ or discarded as non-novel…",
    frontmatter: { type: "concept" },
    bodyMarkdown: "Filters noise before git writes.",
    relatedSlugs: ["compounding-loop"],
  },
  {
    id: "5",
    slug: "jane-doe",
    title: "Jane Doe",
    section: "entities",
    confidence: 0.52,
    excerpt: "Stakeholder referenced in source PDFs; low extraction confidence pending manual review.",
    frontmatter: { entity: "person" },
    bodyMarkdown: "Mentioned in [[quarterly-report-2025]].",
    relatedSlugs: ["quarterly-report-2025"],
  },
  {
    id: "6",
    slug: "quarterly-report-2025",
    title: "Q3 2025 report.pdf",
    section: "sources",
    confidence: 0.79,
    excerpt: "Primary financial narrative; pages 12–18 discuss runway and hiring plan.",
    frontmatter: { source: "pdf", pages: "48" },
    bodyMarkdown: "Imported via PDF adapter.",
    relatedSlugs: ["jane-doe"],
    sourceRefs: ["p.12–18"],
  },
  {
    id: "7",
    slug: "architecture-overview",
    title: "Architecture overview",
    section: "outputs",
    confidence: 0.84,
    excerpt:
      "Compiled synthesis saved to wiki/outputs/ describing four-loop architecture and deployment on Hetzner + Coolify.",
    frontmatter: { output: "synthesis", saved: "true" },
    bodyMarkdown: "Saved output cross-linking [[compounding-loop]].",
    relatedSlugs: ["compounding-loop"],
  },
];

export const MOCK_EXCERPTS_BY_SLUG: Record<string, string> = Object.fromEntries(
  MOCK_WIKI_PAGES.map((p) => [p.slug, p.excerpt]),
);

export const MOCK_QUERY_RESULT: MockQueryResponse = {
  queryType: "synthesis",
  confidence: 0.86,
  costUsd: 0.018,
  bodyMarkdown:
    "Compilore routes documents through [[ingest-pipeline]], then [[query-graph]] answers use [[hybrid-search]] with tenant isolation. Novel answers may land in [[architecture-overview]].",
  sourceSlugs: ["ingest-pipeline", "query-graph", "hybrid-search"],
  gatekeeper: "saved",
  gatekeeperDetail: "wiki/outputs/architecture-overview.md",
};

/** Slug missing from graph — still render chip + tooltip fallback */
MOCK_EXCERPTS_BY_SLUG["hybrid-search"] =
  "RPC `hybrid_search_with_tenant` combines BM25-like text with vector similarity under RLS; service role supplies explicit tenant id.";
MOCK_EXCERPTS_BY_SLUG["synthesizer"] =
  "Claude Sonnet composes grounded answers from retrieved chunks; citations map to source slugs.";
MOCK_EXCERPTS_BY_SLUG["compile-stage"] =
  "Claude compile pass turns raw markdown into structured wiki pages with frontmatter.";

export function confidenceDotClass(c: number): string {
  if (c > 0.7) return "bg-[var(--accent-green)]";
  if (c >= 0.4) return "bg-[oklch(0.78_0.14_85)]";
  return "bg-[var(--accent-red)]";
}
