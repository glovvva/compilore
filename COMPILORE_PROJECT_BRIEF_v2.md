# COMPILORE — Project Brief & Technical Blueprint v2.0
## Agentic Knowledge Compiler | Personal Playground → B2B SaaS

**Created:** 2026-04-09
**Updated:** 2026-04-09 (post Deep Research: legal, VLM feasibility, scaling, Docling)
**Author:** Bartek (Founder)
**Status:** Pre-development — Sprint 0

---

## 1. PRODUCT VISION

### 1.1 What Is Compilore?

Compilore is an **Agentic Knowledge Compiler** — a system that transforms unstructured documents into a living, self-maintaining knowledge base (Wiki) that gets smarter with every interaction.

**It is NOT a chatbot-over-PDFs (standard RAG).** Standard RAG has "amnesia" — it re-discovers knowledge from scratch every query. Compilore **compiles** knowledge once into structured Markdown pages with cross-references, and **compounds** with every new document and every question asked.

### 1.2 Origin & Inspiration

Based on Andrej Karpathy's "LLM Knowledge Base" concept (April 2026) and @hooeem's implementation guide. Core insight: AI should be a **knowledge compiler** (like a research librarian maintaining a Wiki), not a **search engine with amnesia**.

### 1.3 The 4 Loops (Core Architecture)

| Loop | What It Does | When It Runs |
|------|-------------|--------------|
| **Ingest** | Reads uploaded documents. Extracts text. | On document upload |
| **Compile** | LLM creates/updates interconnected Markdown Wiki — concept pages, entity pages, master INDEX.md with cross-references. | After Ingest |
| **Query** | User asks question → hybrid search (vectors + full-text) finds relevant Wiki pages → LLM synthesizes answer with citations → **Gatekeeper** decides if answer is worth saving back to Wiki. | On user query |
| **Lint** | Audits Wiki for contradictions, orphan pages, stale content, broken links. | On-demand only (NEVER autonomous background) |

### 1.4 Two-Phase Strategy

**Phase 1 — Personal Playground (NOW)**
Build for myself. Text/Markdown documents only (articles, strategy notes, research, transcripts). Validate the 4-loop architecture on my own knowledge management. Interface: Viktor/Slack.

**Phase 2 — Architect SaaS (AFTER validation)**
Adapt for Polish architectural firms. Add Docling PDF parser, MPZP-specific adapters, VLM fallback for scans/maps, PII middleware, web UI. Only after Phase 1 proves the core loops work.

### 1.5 Target Market (Phase 2)

**Beachhead:** Polish architectural firms (biura projektowe).
- ~14,300 licensed architects in Poland; ~580,000 in Europe
- 46% = small independent practices (ideal SaaS customers)
- Blue Ocean: 95% of AI tools for architects = 3D rendering. Text-based legal analysis = zero competition
- Distribution: biura rachunkowe from GapRoll network as referral partners

---

## 2. STRATEGIC DECISIONS (LOCKED)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Separate project** | New repo, new Supabase, own domain | Clean separation from GapRoll |
| **Auth (Phase 1)** | Supabase Auth | Simplicity for playground |
| **Auth (Phase 2 launch)** | Kinde | SSO/SAML for enterprise |
| **Vector store** | pgvector (Supabase extension) | $0 incremental, handles <5M vectors, hybrid search in single SQL |
| **Interface (Phase 1)** | Viktor / Slack | Zero frontend to build |
| **Interface (Phase 2)** | Next.js web app | Architects don't use Slack; they use email/Teams |
| **Hosting** | Hetzner VPS + Coolify | EU data, €12.90/mo. Vercel = BANNED. |
| **LLM (Compile/Query)** | Claude 3.7 Sonnet | Best structured Markdown, 200K context. Claude ban in GapRoll (pay equity ToS) does NOT apply here. |
| **Embeddings** | OpenAI text-embedding-3-small | 1536 dims, cheap |
| **Agent framework** | LangGraph | Deterministic, HITL, PostgresSaver checkpointing |
| **Orchestration** | n8n (37.27.14.41) | Already running |
| **Lint mode** | On-demand only | "Agentic Loop of Death" = budget killer |
| **Pricing (Phase 2)** | Usage-based, NOT flat-rate | API costs are variable; flat-rate = bankruptcy |
| **Name** | Compilore | — |

---

## 3. TECH STACK

### 3.1 Phase 1 Stack (Playground — text/Markdown only)

| Layer | Technology | Notes |
|-------|-----------|-------|
| **Backend** | FastAPI (Python 3.12) | Pydantic validation, async |
| **Database** | Supabase PostgreSQL 16 | RLS, JSONB, pgvector |
| **Vector Search** | pgvector extension | 1536 dims |
| **Full-text Search** | PostgreSQL ts_rank_cd + GIN | BM25-approximate |
| **Hybrid Search** | RRF stored procedure | Combining both in single query |
| **Auth** | Supabase Auth | JWT, email/password |
| **File Storage** | Supabase Storage | Raw uploads + compiled Markdown |
| **Agent Framework** | LangGraph | PostgresSaver checkpointer |
| **LLM** | Anthropic Claude 3.7 Sonnet | Compile, Query synthesis, Lint |
| **Embeddings** | OpenAI text-embedding-3-small | 1536 dims |
| **Automation** | n8n (37.27.14.41) | Workflow triggers |
| **Interface** | Viktor.ai (Slack) | Zero frontend |
| **Hosting** | Hetzner + Coolify | EU |
| **Monitoring** | LangSmith | Token cost tracking |
| **Wiki Version Control** | Git | Every compilation = atomic commit |

### 3.2 Phase 2 Additions (Architect SaaS — deferred)

| Layer | Technology | When |
|-------|-----------|------|
| **PDF Extraction** | Docling (TableFormer ACCURATE mode) | Phase 2 |
| **VLM Fallback** | GPT-4o Vision | Phase 2 (scans, maps) |
| **Encoding Detection** | Custom mojibake detector | Phase 2 |
| **Page Padding** | pypdf (40pt margin fix) | Phase 2 |
| **Cross-page Tables** | Custom DataFrame merger | Phase 2 |
| **PII Middleware** | spaCy NER + RegEx | Phase 2 |
| **Map Parser** | LayoutLMv3 + GPT-4o | Phase 2 |
| **Frontend** | Next.js 15 + Shadcn/UI | Phase 2 |
| **Auth** | Kinde | Phase 2 |
| **Legal docs** | DPA, DPIA, Regulamin, OC insurance | Phase 2 (before first client) |

### 3.3 BANNED Technologies

| Banned | Reason | Alternative |
|--------|--------|-------------|
| AWS, Azure, GCP | US-centric, expensive, RODO | Hetzner (EU) |
| Vercel | Expensive, vendor lock-in | Coolify on Hetzner |
| CrewAI, AutoGen | No HITL | LangGraph |
| MongoDB, Firebase | Schema chaos | PostgreSQL/Supabase |
| Pinecone, Weaviate (MVP) | Extra infra, expensive | pgvector |
| LangChain | Deprecated for agents | LangGraph + clean API |
| Stripe (for PL B2B) | No JPK_FA | Fakturownia + P24 |

---

## 4. ARCHITECTURE

### 4.1 Sacred Modularity Rule

> When introducing new functionality, **ALWAYS create a new isolated module/adapter**. NEVER expand a monolithic script. Core Engine is blind to industry-specific logic.

### 4.2 Directory Structure

```
src/
├── modules/
│   ├── ingest/
│   │   ├── base_adapter.py          # Abstract interface
│   │   ├── markdown_adapter.py      # .md files (Phase 1 primary)
│   │   ├── text_adapter.py          # .txt files
│   │   └── pdf_text_adapter.py      # Simple native-digital PDFs (PyMuPDF)
│   ├── compile/
│   │   ├── wiki_generator.py        # Claude → Markdown Wiki pages
│   │   ├── prompts.py               # System prompts for compilation
│   │   ├── index_manager.py         # INDEX.md maintenance
│   │   └── confidence_decay.py      # Monthly: -5%/month, archive <0.30
│   ├── query/
│   │   ├── hybrid_search.py         # RRF fusion (pgvector + ts_rank_cd)
│   │   ├── synthesizer.py           # Claude answer generation with citations
│   │   ├── gatekeeper.py            # Decides if answer is worth saving
│   │   └── compounding.py           # Save approved answers to Wiki
│   ├── lint/
│   │   ├── orphan_detector.py       # RegEx-based (free, deterministic)
│   │   ├── contradiction_checker.py # Claude-powered (on-demand only)
│   │   ├── stale_detector.py        # Date-based freshness check
│   │   └── deduplication.py         # Monthly: cosine >0.92 → merge
│   └── adapters/                    # Phase 2+ industry-specific
│       └── architect/               # DEFERRED — entire directory
│           ├── README.md            # "Phase 2: MPZP, Docling, VLM, PII"
│           ├── mpzp_parser.py       # Docling + encoding detection
│           ├── page_padder.py       # pypdf 40pt margin fix
│           ├── table_merger.py      # Cross-page DataFrame concat
│           ├── pii_stripper.py      # spaCy NER + RegEx
│           └── building_law_kb.py   # Pre-loaded Prawo Budowlane
├── lib/
│   ├── supabase.py                  # Client config
│   ├── anthropic_client.py          # Claude API wrapper
│   ├── openai_client.py             # Embeddings wrapper
│   └── token_tracker.py             # Cost + page ratio monitoring
├── graphs/                          # LangGraph definitions
│   ├── ingest_compile_graph.py      # Upload → Extract → Compile → Store
│   ├── query_graph.py               # Question → Search → Synthesize → Gate → Save?
│   └── lint_graph.py                # On-demand audit with HITL interrupt
├── wiki/                            # Git-versioned Wiki storage
│   ├── .git/                        # Every compilation = atomic commit
│   ├── index.md                     # Master index (flat until 2000 pages)
│   ├── log.md                       # Append-only operation log
│   ├── concepts/                    # Compiled knowledge hubs
│   ├── entities/                    # People, organizations, tools
│   ├── sources/                     # One summary per raw document
│   └── outputs/                     # Gatekeeper-approved query answers
└── config/
    ├── settings.py                  # Environment variables
    └── prompts/                     # Version-controlled system prompts
        ├── compile_wiki.md
        ├── query_synthesize.md
        ├── gatekeeper_evaluate.md
        └── lint_contradiction.md
```

### 4.3 Database Schema

```sql
-- Extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Tenants (multi-tenant ready for Phase 2)
CREATE TABLE tenants (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- User profiles
CREATE TABLE user_profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id),
  tenant_id UUID REFERENCES tenants(id) NOT NULL,
  role TEXT DEFAULT 'user',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Raw documents
CREATE TABLE documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES tenants(id) NOT NULL,
  title TEXT NOT NULL,
  source_url TEXT,
  file_path TEXT,
  doc_type TEXT DEFAULT 'markdown', -- markdown, text, pdf
  status TEXT DEFAULT 'pending',    -- pending, ingested, compiled, error
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Wiki pages (compiled by AI)
CREATE TABLE wiki_pages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES tenants(id) NOT NULL,
  slug TEXT NOT NULL,
  title TEXT NOT NULL,
  page_type TEXT NOT NULL,       -- concept, entity, source_summary, output, index
  content_markdown TEXT NOT NULL,
  frontmatter JSONB DEFAULT '{}',
  -- Frontmatter includes: sources[], related[], confidence, context_hierarchy,
  -- last_compiled, last_verified, status (draft/review/final/deprecated)
  source_documents UUID[] DEFAULT '{}',
  confidence NUMERIC(3,2) DEFAULT 0.90,
  status TEXT DEFAULT 'draft',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(tenant_id, slug)
);

-- Document chunks (for vector + full-text search)
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

-- Activity log (costs, operations)
CREATE TABLE wiki_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES tenants(id) NOT NULL,
  operation TEXT NOT NULL,    -- ingest, compile, query, lint, gatekeeper, decay
  details JSONB NOT NULL,
  tokens_used INT DEFAULT 0,
  cost_usd NUMERIC(10,6) DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS on all tables
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE wiki_pages ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE wiki_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY "tenant_isolation" ON documents FOR ALL
  USING (tenant_id = (SELECT tenant_id FROM user_profiles WHERE id = auth.uid()));
CREATE POLICY "tenant_isolation" ON wiki_pages FOR ALL
  USING (tenant_id = (SELECT tenant_id FROM user_profiles WHERE id = auth.uid()));
CREATE POLICY "tenant_isolation" ON document_chunks FOR ALL
  USING (tenant_id = (SELECT tenant_id FROM user_profiles WHERE id = auth.uid()));
CREATE POLICY "tenant_isolation" ON wiki_log FOR ALL
  USING (tenant_id = (SELECT tenant_id FROM user_profiles WHERE id = auth.uid()));

-- Hybrid Search (RRF)
CREATE OR REPLACE FUNCTION hybrid_search(
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
LANGUAGE sql STABLE
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

### 4.4 Wiki Page Format

```markdown
---
title: "Karpathy LLM Knowledge Base Pattern"
date_created: 2026-04-09
date_modified: 2026-04-09
summary: "4-loop architecture for persistent AI knowledge compilation"
type: concept
status: final
confidence: 0.95
last_verified: 2026-04-09
sources:
  - doc_id: "abc123"
    reference: "Section 2, paragraph 3"
related:
  - "[[agentic-wiki-architecture]]"
  - "[[compounding-loop-risks]]"
tags:
  - ai-architecture
  - knowledge-management
context_hierarchy: "AI Research > Knowledge Systems > Karpathy Pattern"
---

# Karpathy LLM Knowledge Base Pattern

Content here...

## Sources
- Karpathy GitHub Gist (doc: abc123)

## Related
- [[agentic-wiki-architecture]]
```

---

## 5. KEY ARCHITECTURAL SAFEGUARDS (from Deep Research)

### 5.1 Gatekeeper Pattern (CRITICAL)

Not every query answer deserves saving to Wiki. Before write, lightweight evaluation:

1. **Novelty:** Does this synthesize something not already in concept pages?
2. **Necessity:** Is this reusable globally, or hyper-specific/transient?
3. **Grounding:** Are citations valid? Logic derived from sources, not hallucinated?

Only if all three pass → save to `wiki/outputs/`. Otherwise → serve answer, discard from memory.

**Implementation:** `gatekeeper.py` — separate Claude call with `gatekeeper_evaluate.md` prompt. Returns boolean + reasoning. Cost: ~$0.01 per evaluation.

### 5.2 Confidence Decay

Every Wiki page gets `confidence` score (0.0–1.0) in frontmatter.
- Initial: 0.90 (concept pages), 0.80 (output pages)
- Decay: **-5% per month** without verification/access
- Reinforcement: if page is cited in a query and user doesn't flag it → `last_verified` updates, confidence holds
- Archive threshold: **<0.30** → move to `wiki/archive/`, exclude from INDEX.md and retrieval
- Monthly cron via n8n → `confidence_decay.py`

### 5.3 Page Ratio Monitoring

| Type | Target | Alert if exceeds |
|------|--------|-----------------|
| Raw sources | 5% | — |
| Concept/entity pages | 75% | — |
| Output pages (saved answers) | **max 20%** | >25% triggers auto-pruning |

`token_tracker.py` monitors ratios. If output pages >25% → Slack alert + auto-archive lowest-confidence outputs.

### 5.4 Git Version Control on Wiki

- Every compilation = atomic `git commit` with machine-readable diff
- `git blame` to trace when a hallucination was introduced
- Rollback capability if agent corrupts subtree
- `log.md` = append-only operation chronology

### 5.5 INDEX.md Scaling Strategy

- **<2000 pages:** Flat INDEX.md in context (current approach)
- **2000-5000 pages:** Category-level indexes (`concepts/_index.md`, `entities/_index.md`) + hybrid search as primary routing
- **>5000 pages:** Full hybrid search (pgvector + BM25 RRF), INDEX.md used only for high-level overview

### 5.6 Scheduled Maintenance

| Frequency | Operation | Cost |
|-----------|-----------|------|
| **Event-driven** | Re-compile when source document changes (frontmatter dependency tracking) | Per-update |
| **Weekly** | Lint: orphan links, broken wikilinks (RegEx, $0) | $0 |
| **Monthly** | Confidence decay + semantic dedup (cosine >0.92 → merge) | ~$2-5/tenant |
| **Quarterly** | Full audit vs source truth + human review of stale pages | ~$10-20/tenant |

---

## 6. COST MODEL

### 6.1 Phase 1 Costs (Playground — text/Markdown only)

| Operation | Model | Cost |
|-----------|-------|------|
| **Ingest** (Markdown/text) | No LLM needed, direct read | $0.00 |
| **Compile** (per document) | Claude 3.7 Sonnet (~50K input + ~15K output) | ~$0.40 |
| **Embeddings** (per document) | text-embedding-3-small | ~$0.01 |
| **Query** (per question) | Claude synthesis | ~$0.05 |
| **Gatekeeper** (per query) | Claude mini evaluation | ~$0.01 |
| **Lint** (on-demand) | Claude contradiction check | ~$0.40 |

**Monthly estimate for personal use (50 docs, 200 queries):** ~$30-40

### 6.2 Phase 2 Costs (Architect SaaS — per client)

| Operation | Cost |
|-----------|------|
| Ingest 50-page MPZP (Docling + VLM fallback) | $0.29-$1.14 |
| Compile | ~$0.75 |
| Embeddings | ~$0.01 |
| Query (per question) | ~$0.06 (incl. gatekeeper) |
| Monthly maintenance | ~$2-5 |

### 6.3 Phase 2 Pricing

| Tier | Price | Includes |
|------|-------|----------|
| **Starter** | ~200 PLN/mo | 20 docs/mo, 200 queries, no Lint |
| **Professional** | ~600 PLN/mo | 100 docs/mo, unlimited queries, weekly Lint |
| **Enterprise** | Custom 2500+ PLN/mo | Unlimited, daily Lint, API |

Value metric: documents processed + Wiki size. NOT per-seat.

---

## 7. SPRINT PLAN (Phase 1 — Playground)

### Sprint 0: Infrastructure (3-4 days)

**Goal:** Repo, database, auth, module scaffolding.

- [ ] Create GitHub repo `compilore` (private)
- [ ] Initialize Git-versioned `wiki/` directory inside repo
- [ ] Create new Supabase project (EU region)
- [ ] Enable pgvector extension
- [ ] Run database migration (schema from §4.3)
- [ ] Deploy FastAPI skeleton to Hetzner via Coolify
- [ ] Create `.cursor/rules/compilore.mdc` with architecture rules
- [ ] Create module directories with docstrings per §4.2
- [ ] Set env vars in Coolify (Supabase, Anthropic, OpenAI, LangSmith)

**Owner:** Claude Code (infra) + Cursor Composer (scaffolding).

### Sprint 1: Ingest + Compile (1 week)

**Goal:** Upload .md file → get structured Wiki pages with cross-references.

- [ ] `markdown_adapter.py` — read .md files, extract frontmatter + content
- [ ] `text_adapter.py` — read plain .txt
- [ ] `pdf_text_adapter.py` — PyMuPDF for native-digital PDFs (simple text only)
- [ ] `wiki_generator.py` — Claude Compile prompt → creates concept/entity pages
- [ ] `index_manager.py` — create/update flat INDEX.md
- [ ] `token_tracker.py` — log every API call cost to wiki_log
- [ ] `ingest_compile_graph.py` — LangGraph: Upload → Read → Compile → Embed → Store → Git commit → Log
- [ ] **Test:** Upload one article .md → verify Wiki pages in Supabase + INDEX.md + git log

### Sprint 2: Query + Gatekeeper (1 week)

**Goal:** Ask question via Slack → get cited answer → Gatekeeper decides if saved.

- [ ] `hybrid_search.py` — call RRF stored procedure
- [ ] `synthesizer.py` — Claude synthesis with [[wikilink]] citations
- [ ] `gatekeeper.py` — evaluate novelty × necessity × grounding
- [ ] `compounding.py` — save approved answers to `wiki/outputs/`
- [ ] `query_graph.py` — LangGraph: Question → Embed → Search → Synthesize → Gate → Save? → Reply
- [ ] Viktor/Slack integration: `/compilore ask [question]`
- [ ] Viktor/Slack: `/compilore ingest [paste text or URL]`
- [ ] **Test:** Ask question → verify cited answer + gatekeeper decision + git commit if saved

### Sprint 3: Lint + Maintenance (1 week)

**Goal:** On-demand audit + automated health maintenance.

- [ ] `orphan_detector.py` — RegEx for broken [[wikilinks]] ($0)
- [ ] `stale_detector.py` — flag pages not updated >30 days
- [ ] `contradiction_checker.py` — Claude structured JSON for conflicts
- [ ] `deduplication.py` — cosine similarity >0.92 → suggest merge
- [ ] `confidence_decay.py` — monthly cron: -5%, archive <0.30
- [ ] `lint_graph.py` — LangGraph with `interrupt_before` on contradictions (HITL)
- [ ] Viktor/Slack: `/compilore lint` → run audit → post results
- [ ] Viktor/Slack: `/compilore stats` → page counts, ratios, costs
- [ ] n8n workflow: monthly confidence decay trigger
- [ ] **Test:** Run lint on Wiki with intentionally broken links + stale pages

### Sprint 4: Polish + Daily Use (1 week)

**Goal:** Use it daily. Fix friction points. Prepare for Phase 2 decision.

- [ ] Refine prompts based on real usage (compile_wiki.md, query_synthesize.md)
- [ ] Add `/compilore status` — show Wiki health dashboard on Slack
- [ ] Add incremental re-compilation: when source document is updated, only affected pages recompile (dependency tracking via frontmatter)
- [ ] Weekly cost report via Slack (from wiki_log)
- [ ] Document learnings for Phase 2
- [ ] **Decision gate:** Is the 4-loop architecture working? Am I using it daily? → Go/No-Go for Phase 2

---

## 8. PHASE 2 CHECKLIST (Architect SaaS — only after Phase 1 validation)

### 8.1 Technical Additions

- [ ] Docling integration (TableFormerMode.ACCURATE, do_cell_matching=True)
- [ ] Encoding detector (mojibake → force OCR)
- [ ] Page padder (pypdf 40pt margin for edge tables)
- [ ] Cross-page table merger (DataFrame concat heuristic)
- [ ] PII stripping middleware (spaCy NER + RegEx, BEFORE external API)
- [ ] GPT-4o Vision fallback (scanned pages + maps only)
- [ ] Tiered document sensitivity routing:
  - 🟢 Public (MPZP text) → standard API
  - 🟡 Sensitive (permits) → PII strip → ZDR endpoints
  - 🔴 Confidential (NDA docs) → local processing only
- [ ] Pydantic MPZP schema validation (height 1-50m, green ratio 0-1.0, etc.)
- [ ] Logprobs confidence scoring (threshold 95% → HITL flag)
- [ ] Next.js web UI (chat, document list, Wiki browser, audit button)
- [ ] Kinde auth migration
- [ ] 20-document benchmark (6 modern + 4 legacy font + 4 scans + 4 hybrid + 2 cross-page)

### 8.2 Legal Requirements (before first paying client)

- [ ] ZDR application to OpenAI (start early — approval takes weeks)
- [ ] DPA (Umowa Powierzenia Przetwarzania Danych) — with lawyer
- [ ] DPIA (Ocena Skutków dla Ochrony Danych) — internal, documenting all flows
- [ ] Regulamin Świadczenia Usług — with Art. 473 KC liability cap (12 months subscription)
- [ ] Privacy Policy (Polityka Prywatności)
- [ ] OC Zawodowe IT insurance (1-3M PLN, covering AI hallucinations + data breach)
- [ ] Landing page trust signals:
  - "Twoje dane nie trenują AI" badge
  - "100% danych w UE" badge
  - "Tajemnica Przedsiębiorstwa" document toggle in UI

### 8.3 Validation Metrics (before writing Phase 2 code)

1. **Deep Problem Resonance:** 15 interviews with architects; 7/10 must cite MPZP chaos as burning pain
2. **Skin-in-the-Game:** Landing page where architects upload real MPZP to join waitlist. Target: 5-10 docs
3. **Pre-sale:** 2 Letters of Intent for paid pilot (~$250 for archive compilation)

---

## 9. KEY RISKS & MITIGATIONS

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Hallucination amplification** (compounding loop) | Wrong info cascades through Wiki | Gatekeeper pattern + confidence decay + git version control |
| **Knowledge rot** (stale pages) | Outdated info served confidently | Confidence decay (-5%/mo) + event-driven recompilation + quarterly audit |
| **State space explosion** (too many output pages) | Outputs drown source pages | Page ratio monitoring (max 20% outputs) + auto-pruning |
| **INDEX.md scaling** | Model can't navigate >5000 pages | Hierarchical indexes at 2000+ pages; hybrid search as primary routing |
| **Semantic drift** (Model Collapse) | Wiki diverges from reality over 6 months | Git diffing, quarterly baseline audit, human review triggers |
| **VLM cost explosion** (Phase 2) | Margin death on MPZP processing | Docling as default ($0), VLM only for scans/maps (20-30% pages) |
| **RODO / data privacy** (Phase 2) | Legal exposure sending docs to US API | PII stripping + ZDR endpoints + tiered sensitivity routing |
| **Trade secret invalidation** (Phase 2) | Clients legally can't use the tool | DPA + ZDR + "Tajemnica Przedsiębiorstwa" toggle routing to ZDR-only paths |
| **AI hallucination liability** (Phase 2) | Architect builds based on wrong parameter | Art. 473 KC liability cap + mandatory verification clause + source citations in every answer |
| **Platform risk** (Anthropic/OpenAI builds this) | Commoditization | Vertical depth (Polish MPZP), proprietary compiled data, workflow lock-in, regulatory moat |
| **Docling RAM crash** (Phase 2) | OOM on 8GB Hetzner | OMP_NUM_THREADS=1, page-by-page processing, gc.collect(), OCR offload to VLM API |

---

## 10. SYNERGIES WITH GAPROLL

| GapRoll Asset | Compilore Reuse |
|---------------|-----------------|
| Hetzner VPS + Coolify | Shared hosting |
| n8n VPS (37.27.14.41) | Workflow orchestration |
| Viktor.ai (Slack) | Phase 1 interface |
| Cloudflare | DNS |
| LangGraph expertise | Agent framework for all 4 loops |
| PostgresSaver pattern | Proven checkpointing |
| Supabase RLS patterns | Multi-tenant isolation |
| LangSmith | Token monitoring |
| Instantly.ai | Phase 2 architect outreach |
| Biura rachunkowe network | Phase 2 referral channel |
| LinkedIn "Build in Public" | Dual content for GapRoll PH + Compilore validation |

---

## 11. CURSOR COMPOSER MEGA PROMPT (Sprint 0)

```
You are a Principal Staff Engineer setting up a Python + FastAPI 
project called "Compilore" — an Agentic Knowledge Compiler.

The system implements Karpathy's 4-loop pattern: Ingest, Compile, 
Query (with Gatekeeper), and Lint. Phase 1 processes ONLY text and 
Markdown documents (no PDFs, no scans, no VLM). The Wiki is a 
Git-versioned collection of Markdown files.

1. Create `.cursor/rules/compilore.mdc`:
   - Python 3.12+ with type hints everywhere
   - FastAPI for all endpoints
   - Pydantic v2 for validation
   - NEVER monolithic scripts — Adapter Pattern always
   - Business logic in src/modules/, NOT in route handlers
   - LangGraph for all agent orchestration
   - All prompts in src/config/prompts/ as .md files
   - Every wiki write = git commit

2. Create directory structure per the blueprint:
   src/modules/ingest/ (markdown_adapter.py, text_adapter.py, 
     pdf_text_adapter.py, base_adapter.py)
   src/modules/compile/ (wiki_generator.py, prompts.py, 
     index_manager.py, confidence_decay.py)
   src/modules/query/ (hybrid_search.py, synthesizer.py, 
     gatekeeper.py, compounding.py)
   src/modules/lint/ (orphan_detector.py, contradiction_checker.py, 
     stale_detector.py, deduplication.py)
   src/modules/adapters/architect/ (empty, README: "Phase 2")
   src/lib/ (supabase.py, anthropic_client.py, openai_client.py, 
     token_tracker.py)
   src/graphs/ (ingest_compile_graph.py, query_graph.py, 
     lint_graph.py)
   src/config/prompts/ (compile_wiki.md, query_synthesize.md, 
     gatekeeper_evaluate.md, lint_contradiction.md)
   wiki/ (initialize as git repo with index.md, log.md, 
     concepts/, entities/, sources/, outputs/)
   src/main.py (FastAPI with /health endpoint)

3. Each module file: docstring explaining purpose in context of 
   Karpathy's 4-loop architecture, placeholder class/function 
   with proper type hints.

4. requirements.txt: fastapi, uvicorn, supabase, anthropic, 
   openai, langgraph, langsmith, pydantic>=2.0, python-multipart, 
   PyMuPDF, gitpython

5. .env.example with all required environment variables.

6. README.md with project overview.

Do NOT implement logic yet — clean scaffold with typing and 
docstrings only.
```

---

## 12. DECISIONS DEFERRED

- Frontend UI design (Phase 2)
- Payment integration (Phase 2, after first client)
- Proactivity / push notifications (Phase 3)
- Voice interface (Phase 4)
- Multiple industry adapters (Phase 3+)
- Fine-tuning on compiled Wiki data (post-PMF)
- Kinde auth migration (Phase 2 launch)
- Docling, VLM, PII middleware, map parser (all Phase 2)
- OC insurance, DPA, DPIA (Phase 2, before first client)
- 385-document statistical validation (Phase 2 production)
