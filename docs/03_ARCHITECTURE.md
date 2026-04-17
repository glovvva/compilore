# 03 — ARCHITECTURE
## Compilore: Stack, Schema, Module Map

**Last updated:** 2026-04-17

---

## Sacred Rules (Never Break These)

1. **Adapter Pattern always.** When adding new functionality, create a new isolated
   module/adapter. NEVER expand an existing monolithic script. The Core Engine is
   blind to industry-specific logic.

2. **Business logic in `src/modules/`, never in route handlers.** FastAPI routes
   are thin — they validate input and call modules. Zero business logic in `src/main.py`.

3. **Every Wiki write = atomic git commit.** No exceptions. This enables rollback,
   audit trail, and hallucination tracing via `git blame`.

4. **LangGraph for all agent orchestration.** No ad-hoc async chains. Deterministic
   state machines only. HITL via `interrupt_before` nodes.

5. **All prompts in `src/config/prompts/` as `.md` files.** Prompts are versioned
   alongside code. Never hardcode prompt strings in Python files.

6. **Lint loop is NEVER autonomous.** On-demand only. Autonomous background lint =
   "Agentic Loop of Death" = uncontrolled API spend.

---

## API Design Rules

API Design Rules (from GapRoll cross-project reference)

- Every JSON endpoint returns `APIResponse[T]` with `meta` (`request_id`, `timestamp`, `processing_time_ms`) and optional `ai_context` (`ai_generated`, `model_used`, `cost_usd`).
- `processing_time_ms` is injected automatically by HTTP middleware — never manually per route.
- Include semantic endpoint descriptions in OpenAPI (operation intent, side effects, and expected next action), not just type schemas.
- Include `X-Agent-ID` request header handling in middleware to distinguish agent callers from human UI calls.
- Long-running operations (compile, lint) should support async webhook flow: immediate `job_id` + callback to `callback_url` when complete.
- All JSON responses include `available_actions[]` for progressive agent orchestration.
- **Endpoint naming:** `POST /api/v1/{domain}/{action}`
  - `domain` = noun: `wiki`, `ingest`, `lint`
  - `action` = verb: `compile`, `query`, `ingest`, `run`, `stats`
- **BANNED:** `/api/process`, `/api/dashboard-data`, `/api/get-info`

---

## Phase 1 Tech Stack

| Layer | Technology | Notes |
|---|---|---|
| Backend | FastAPI (Python 3.12) | Pydantic v2 validation, async |
| Database | Supabase PostgreSQL 16 | RLS, JSONB, pgvector |
| Vector Search | pgvector extension | 1536 dims, cosine similarity |
| Full-text Search | PostgreSQL ts_rank_cd + GIN | BM25-approximate |
| Hybrid Search | RRF stored procedure | Both in single SQL query |
| Auth | Supabase Auth | JWT, email/password |
| File Storage | Supabase Storage | Raw uploads + compiled Markdown |
| Agent Framework | LangGraph | PostgresSaver checkpointer |
| LLM — Compile | Claude 3.7 Sonnet (API) | Best structured Markdown, 200K context |
| LLM — Query synthesis | Claude 3.7 Sonnet (API) → Gemma 4 27B/12B (local, planned) | See §LLM Routing |
| LLM — Gatekeeper | Claude Haiku 4.5 (API) → Gemma 4 27B/12B (local, planned) | Simple classification |
| Embeddings | OpenAI text-embedding-3-small | 1536 dims, ~$0.001/1M tokens |
| Automation | n8n (37.27.14.41) | Workflow triggers, cron jobs |
| Interface | Web UI (localhost:8001) → Hetzner deploy | Dark mode, monospace |
| Hosting | Hetzner + Coolify | EU data sovereignty, €12.90/mo |
| Monitoring | LangSmith | Token cost tracking per operation |
| Wiki Version Control | Git (nested repo in `wiki/`) | Every compilation = atomic commit |
| API Response | `APIResponse[T]` envelope (`src/lib/response.py`) | All JSON routes; middleware auto-injects `processing_time_ms` |

## Banned Technologies

| Banned | Reason | Alternative |
|---|---|---|
| AWS, Azure, GCP | US-centric, RODO exposure | Hetzner (EU) |
| Vercel | Expensive, vendor lock-in | Coolify on Hetzner |
| CrewAI, AutoGen | No HITL controls | LangGraph |
| MongoDB, Firebase | Schema chaos | PostgreSQL/Supabase |
| Pinecone, Weaviate | Extra infra, cost | pgvector |
| LangChain | Deprecated for agents | LangGraph + clean API calls |
| Stripe (PL B2B) | No JPK_FA | Fakturownia + P24 |

---

## LLM Routing Strategy

Not all operations require the same model. Routing reduces monthly cost ~70%.

| Operation | Current | Target (after Gemma 4 local setup) | Rationale |
|---|---|---|---|
| Compile | Claude Sonnet (API) | Claude Sonnet (API) — keep | One-time, quality permanent, ~$0.07/doc |
| Query synthesis | Claude Sonnet (API) | Gemma 4 27B/12B Dense (local, Ollama) | High frequency, $0 marginal cost |
| Gatekeeper | Claude Haiku 4.5 (API) | Gemma 4 27B/12B Dense (local, Ollama) | Simple classification, $0 |
| Orphan detection | RegEx | RegEx — keep | $0, deterministic |
| Contradiction check | Claude Sonnet (API) | Claude Sonnet (API) — keep | Complex reasoning, on-demand |

**Why Gemma 4 31B Dense specifically (not 26B A4B MoE):**
The 26B MoE systematically produces malformed YAML/JSON — trailing garbage tokens,
invalid escape sequences, broken schema. This is architectural, not fixable with
prompt engineering. The 31B Dense scores 78.7% on IFBench (vs Claude Sonnet 74.7%)
and shows 100% reliability in agentic simulation benchmarks.

**Gemma 4 on M4 Pro 24GB (developer machine):**
- Recommended: 12B Q4_K_M (~8GB RAM, ~25-35 t/s) — start here
- Upgrade path: 27B Q4_K_M (~16-17GB RAM, ~12-18 t/s) — if quality insufficient  
- Avoid: 31B Q4_K_M — too tight on 24GB, risk of OOM under load
- Runtime: Ollama + MLX backend (auto-detected on Apple Silicon)
- Thermal note: 14" chassis throttles under sustained load; batch lint ops stay on API

---

## Directory Structure

```
Compilore/
├── .cursor/
│   └── rules/
│       └── compilore.mdc           # Cursor Composer standing instructions
├── docs/                           # Project documentation (this folder)
│   ├── 01_PRODUCT.md
│   ├── 02_STRATEGY.md
│   ├── 03_ARCHITECTURE.md
│   ├── 04_DECISIONS.md
│   ├── 05_INGESTION.md
│   ├── 06_COSTS.md
│   ├── 07_SPRINTS.md
│   └── 08_RESEARCH.md
├── src/
│   ├── modules/
│   │   ├── ingest/
│   │   │   ├── base_adapter.py         # Abstract BaseAdapter interface
│   │   │   ├── markdown_adapter.py     # .md files
│   │   │   ├── text_adapter.py         # .txt files
│   │   │   ├── pdf_text_adapter.py     # Native-digital PDFs (PyMuPDF)
│   │   │   ├── url_adapter.py          # URL → trafilatura (Phase 1)
│   │   │   └── text_paste_adapter.py   # Direct text paste — MISSING, add Sprint 2
│   │   ├── compile/
│   │   │   ├── wiki_generator.py       # Claude → Markdown Wiki pages
│   │   │   ├── prompts.py              # Prompt loading utilities
│   │   │   ├── index_manager.py        # INDEX.md maintenance
│   │   │   └── confidence_decay.py     # Monthly: -5%/month, archive <0.30
│   │   ├── query/
│   │   │   ├── hybrid_search.py        # RRF fusion (pgvector + ts_rank_cd)
│   │   │   ├── synthesizer.py          # LLM answer generation with citations
│   │   │   ├── gatekeeper.py           # Novelty × Necessity × Grounding + pre-check
│   │   │   └── compounding.py          # Save approved answers to wiki/outputs/
│   │   ├── lint/
│   │   │   ├── orphan_detector.py      # RegEx broken [[wikilinks]], $0
│   │   │   ├── contradiction_checker.py # Claude-powered, on-demand only
│   │   │   ├── stale_detector.py       # Pages not updated > 30 days
│   │   │   └── deduplication.py        # cosine > 0.92 → suggest merge
│   │   └── adapters/
│   │       └── architect/              # PHASE 2 — entire directory deferred
│   │           ├── README.md           # "Phase 2: MPZP, Docling, VLM, PII"
│   │           ├── mpzp_parser.py      # Docling + encoding detection
│   │           ├── plan_ogolny_adapter.py # NEW: distinct from MPZP (reform 2026)
│   │           ├── page_padder.py      # pypdf 40pt margin fix
│   │           ├── table_merger.py     # Cross-page DataFrame concat
│   │           ├── pii_stripper.py     # spaCy NER + RegEx, runs BEFORE any API
│   │           └── building_law_kb.py  # Pre-loaded Prawo Budowlane
│   ├── lib/
│   │   ├── supabase.py                 # Supabase client config + helpers
│   │   ├── anthropic_client.py         # Claude API wrapper
│   │   ├── openai_client.py            # Embeddings wrapper
│   │   ├── response.py                 # APIResponse[T] envelope, ResponseMeta, AIContext, envelop() helper
│   │   └── token_tracker.py            # Cost + page ratio monitoring → wiki_log
│   ├── graphs/
│   │   ├── ingest_compile_graph.py     # Upload → Extract → Compile → Embed → Store → Git
│   │   ├── query_graph.py              # Question → Embed → Search → Synthesize → Gate → Save?
│   │   └── lint_graph.py               # On-demand audit with interrupt_before on contradictions
│   ├── config/
│   │   └── prompts/
│   │       ├── compile_wiki.md         # System prompt: document → Wiki pages
│   │       ├── query_synthesize.md     # System prompt: search results → answer with citations
│   │       ├── gatekeeper_evaluate.md  # System prompt: evaluate novelty × necessity × grounding
│   │       └── lint_contradiction.md   # System prompt: find contradictions → structured JSON
│   └── main.py                         # FastAPI app, thin routes only
├── sql/
│   ├── 001_initial_schema.sql          # Full schema: tables, indexes, RLS policies
│   ├── 002_hybrid_search_with_tenant.sql # SECURITY DEFINER hybrid_search function
│   └── 003_seed_tenant.sql             # Seed "bartek-playground" tenant
├── scripts/
│   └── validate_setup.py               # Health check: Supabase, pgvector, wiki/, APIs
├── wiki/                               # Git-versioned Wiki (nested repo)
│   ├── .git/
│   ├── index.md                        # Master index (flat until 2000 pages)
│   ├── log.md                          # Append-only operation chronology
│   ├── concepts/                       # Compiled knowledge hub pages
│   ├── entities/                       # People, organizations, tools
│   ├── sources/                        # One summary per source document
│   ├── outputs/                        # Gatekeeper-approved query answers
│   └── archive/                        # Confidence < 0.30 → moved here
├── tests/
├── .env.example
├── .env                                # Never committed
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## Database Schema (Supabase PostgreSQL 16)

### Extensions
```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

### Tables

**tenants** — multi-tenant ready for Phase 2
```sql
CREATE TABLE tenants (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**user_profiles**
```sql
CREATE TABLE user_profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id),
  tenant_id UUID REFERENCES tenants(id) NOT NULL,
  department_id UUID REFERENCES departments(id),
  locale TEXT NOT NULL DEFAULT 'pl',
  role TEXT DEFAULT 'user',
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**departments** — tenant-level knowledge boundary layer
```sql
CREATE TABLE departments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  slug TEXT NOT NULL,
  visibility TEXT NOT NULL DEFAULT 'private'
    CHECK (visibility IN ('private', 'tenant_wide')),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(tenant_id, slug)
);
```

**documents** — raw ingested sources
```sql
CREATE TABLE documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES tenants(id) NOT NULL,
  title TEXT NOT NULL,
  source_url TEXT,
  file_path TEXT,
  doc_type TEXT DEFAULT 'markdown',   -- markdown | text | pdf | url | paste
  status TEXT DEFAULT 'pending',       -- pending | ingested | compiled | error
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

**wiki_pages** — compiled by AI
```sql
CREATE TABLE wiki_pages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES tenants(id) NOT NULL,
  department_id UUID REFERENCES departments(id),
  slug TEXT NOT NULL,
  title TEXT NOT NULL,
  page_type TEXT NOT NULL,             -- concept | entity | source_summary | output | index
  content_markdown TEXT NOT NULL,
  frontmatter JSONB DEFAULT '{}',      -- includes git_commit_hash, sources[], related[], confidence, etc.
  source_documents UUID[] DEFAULT '{}',
  confidence NUMERIC(3,2) DEFAULT 0.90,
  status TEXT DEFAULT 'draft',         -- draft | review | final | deprecated
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(tenant_id, slug)
);
```
`department_id = NULL` means tenant-wide visibility. Non-NULL means department-scoped visibility.

**document_chunks** — for vector + full-text search
```sql
CREATE TABLE document_chunks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES tenants(id) NOT NULL,
  wiki_page_id UUID REFERENCES wiki_pages(id) ON DELETE CASCADE,
  document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
  chunk_text TEXT NOT NULL,
  chunk_index INT NOT NULL,
  embedding vector(1536),
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Full-text search
ALTER TABLE document_chunks ADD COLUMN tsv tsvector
  GENERATED ALWAYS AS (to_tsvector('simple', chunk_text)) STORED;
CREATE INDEX idx_chunks_tsv ON document_chunks USING GIN (tsv);

-- Vector index (HNSW)
CREATE INDEX idx_chunks_embedding ON document_chunks
  USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64);
```

**wiki_log** — operation log with costs
```sql
CREATE TABLE wiki_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES tenants(id) NOT NULL,
  operation TEXT NOT NULL,    -- ingest | compile | query | lint | gatekeeper | decay
  details JSONB NOT NULL,
  tokens_used INT DEFAULT 0,
  cost_usd NUMERIC(10,6) DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

`module` column (see `sql/004_add_module_column.sql`): identifies source module — `wiki_generator` \| `synthesizer` \| `hybrid_search` \| `gatekeeper` \| `confidence_decay` \| `lint_graph` \| `output_formatter` (and related adapters where applicable).

### RLS Policies (tenant isolation on all tables)
```sql
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE wiki_pages ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE wiki_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY "tenant_isolation" ON documents FOR ALL
  USING (tenant_id = (SELECT tenant_id FROM user_profiles WHERE id = auth.uid()));
-- Same pattern for all tables
```
Option B policy model for knowledge visibility:
- Default open within tenant (`department_id IS NULL` rows visible to all members of the tenant).
- Department-scoped pages (`department_id IS NOT NULL`) visible only to users who belong to that department.
- No hard tenant-internal silos and no per-page ACL at this phase.

### Hybrid Search Function (RRF)
```sql
CREATE OR REPLACE FUNCTION hybrid_search(
  query_text TEXT,
  query_embedding vector(1536),
  match_count INT DEFAULT 10,
  rrf_k INT DEFAULT 60,
  scope TEXT DEFAULT 'tenant'  -- 'department' | 'tenant' | 'global'
)
RETURNS TABLE (chunk_id UUID, wiki_page_id UUID, chunk_text TEXT, rrf_score FLOAT)
LANGUAGE sql STABLE SECURITY DEFINER
AS $$
  WITH semantic AS (
    SELECT id, wiki_page_id, chunk_text,
      ROW_NUMBER() OVER (ORDER BY embedding <=> query_embedding) AS rank
    FROM document_chunks
    WHERE tenant_id = (SELECT tenant_id FROM user_profiles WHERE id = auth.uid())
    ORDER BY embedding <=> query_embedding
    LIMIT match_count * 2
  ),
  fulltext AS (
    SELECT id, wiki_page_id, chunk_text,
      ROW_NUMBER() OVER (ORDER BY ts_rank_cd(tsv, plainto_tsquery('simple', query_text)) DESC) AS rank
    FROM document_chunks
    WHERE tenant_id = (SELECT tenant_id FROM user_profiles WHERE id = auth.uid())
      AND tsv @@ plainto_tsquery('simple', query_text)
    ORDER BY ts_rank_cd(tsv, plainto_tsquery('simple', query_text)) DESC
    LIMIT match_count * 2
  ),
  combined AS (
    SELECT
      COALESCE(s.id, f.id) AS id,
      COALESCE(s.wiki_page_id, f.wiki_page_id) AS wiki_page_id,
      COALESCE(s.chunk_text, f.chunk_text) AS chunk_text,
      COALESCE(1.0 / (rrf_k + s.rank), 0) + COALESCE(1.0 / (rrf_k + f.rank), 0) AS score
    FROM semantic s
    FULL OUTER JOIN fulltext f ON s.id = f.id
  )
  SELECT id, wiki_page_id, chunk_text, score
  FROM combined ORDER BY score DESC LIMIT match_count;
$$;
```
Scope semantics:
- `department`: search only department-scoped rows for caller's department (plus tenant-wide rows if desired by query module policy).
- `tenant`: search all tenant-visible rows (default).
- `global`: reserved for cross-tenant/public corpus (Phase 3+; not active in Phase 1).

---

## Phase 2 Architecture Additions (Deferred)

| Layer | Technology | Notes |
|---|---|---|
| PDF Extraction | Docling (TableFormerMode.ACCURATE) | Replaces PyMuPDF for complex PDFs |
| Async PDF | Kreuzberg (native async/await) | Non-blocking FastAPI PDF parsing |
| VLM Fallback | GPT-4o Vision | Scanned pages + maps only (~20-30% of MPZP) |
| Encoding Detection | Custom mojibake detector | Legacy Polish fonts |
| Page Padding | pypdf (40pt margin fix) | Edge table recovery |
| Cross-page Tables | Custom DataFrame merger | concat heuristic |
| PII Middleware | spaCy NER + RegEx | BEFORE any external API call |
| Map Parser | LayoutLMv3 + GPT-4o | Phase 2 |
| Frontend | Next.js 15 + Shadcn/UI | Bento grid, glassmorphism, response cards |
| Auth | Kinde | SSO/SAML for enterprise |
| Document sensitivity tiers | Routing middleware | 🟢 Public → API / 🟡 Sensitive → ZDR / 🔴 Confidential → local |

**Docling OOM prevention (Hetzner 8GB):**
`OMP_NUM_THREADS=1`, page-by-page processing, `gc.collect()` after each page,
OCR offload to VLM API for scans. n8n as queue (one job at a time, 120s timeout,
Coolify restart policy).

---

## Scheduled Maintenance

| Frequency | Operation | Cost | Owner |
|---|---|---|---|
| Event-driven | Re-compile when source document changes (frontmatter dependency tracking) | Per-update | ingest_compile_graph.py |
| Weekly | Lint: orphan links, broken wikilinks (RegEx, $0) | $0 | n8n cron → lint_graph.py |
| Monthly | Confidence decay (-5%) + semantic dedup (cosine > 0.92 → merge) | ~$2–5/tenant | n8n cron → confidence_decay.py |
| Quarterly | Full audit vs source truth + human review of stale pages | ~$10–20/tenant | Manual trigger |

---

## Decision Traceability

- Department isolation model in this document maps to `D-59` in `docs/04_DECISIONS.md`.
- i18n infrastructure-first model in this document maps to `D-60` in `docs/04_DECISIONS.md`.
