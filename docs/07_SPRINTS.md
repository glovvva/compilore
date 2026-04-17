# 07 — SPRINTS
## Compilore: Sprint Plan, Status, Backlog

**Last updated:** 2026-04-17

---

## Current Status Summary

**Phase:** 1 — Personal Playground
**Sprint:** Sprint 3 (Lint) + Sprint 4b (Wiki Tree) complete; **Auth shipped 2026-04-12** (magic link + JWT tenant). Next: Hetzner deploy + beta hardening
**Running:** Locally on MacBook Pro 14" M4 Pro (24GB), localhost:8001
**Repo:** github.com/glovvva/compilore (private)
**Supabase:** EU West (Paris), schema deployed, tenant "bartek-playground" active (id: a6d3721a…)

### What Is Working End-to-End Today
- Paste URL → compile Wiki pages in ~30 seconds ✅
- Ask question → get cited answer + Gatekeeper reasoning + cost ✅
- Ingest: .md, .txt, .pdf, URL ✅
- Compile: source_summary + concept pages + entity pages → Supabase + wiki/ + git commit ✅
- Query: hybrid search (pgvector + BM25 RRF) + Claude synthesis + citations ✅
- Gatekeeper: saves to wiki/outputs/ on pass ✅
- Web UI: dark mode, Geist/Instrument Serif/Geist Mono typography, oklch color tokens ✅
- Wiki Tree: live from Supabase (RLS-scoped), confidence dots, search, sections ✅
- Inspector panel: full wiki page viewer with ReactMarkdown + frontmatter ✅
- Auto-format detection: comparison table / timeline / mindmap / code block / list / prose ✅
- ⌘K command palette with wiki fuzzy search ✅
- Cost per query: ~$0.018 ✅

### Known Issues / Debt
- **Backlog:** test: middleware processing_time_ms injection (FastAPI JSON envelope)
- [x] **Resolved (2026-04-12):** Backend + static playground auth — Supabase magic link, `Authorization: Bearer` on protected API routes, dynamic Supabase config in `serve_ui`
- `/lint/decay` uses `COMPILORE_DEFAULT_TENANT_ID` (hardcoded tenant) — acceptable for n8n webhook; revisit in Phase 2
- HTTPS not yet configured on production URL (sslip.io shows „Niezabezpieczona”)
- [x] **Resolved:** `psycopg2-binary` — present in `requirements.txt` and dev venv (earlier debt item was stale)
- LangSmith monitoring not connected
- Model name `claude-3-5-haiku-20241022` in some places — update to `claude-haiku-4-5-20251001`
- No text paste input endpoint (`/ingest/paste`)
- Running locally only — no Hetzner deploy yet
- Mermaid mindmap: requires `mermaid` code block in LLM response — mindmap hint appended to query but real query API not yet wired (mock only)

---

## Sprint 0 — Infrastructure ✅ COMPLETE

**Goal:** Repo, database, auth, module scaffolding.
**Duration:** ~1 day

- [x] GitHub repo `compilore` (private)
- [x] Git-versioned `wiki/` directory
- [x] Supabase project (EU West Paris)
- [x] pgvector extension enabled
- [x] Database migration (schema from §4.3 of brief)
- [x] FastAPI skeleton deployed locally
- [x] `.cursor/rules/compilore.mdc` created
- [x] Module directories with docstrings
- [x] `.env.example` with all variables
- [x] `scripts/validate_setup.py` health check script

---

## Sprint 1 — Ingest + Compile ✅ COMPLETE

**Goal:** Upload .md file → get structured Wiki pages with cross-references.
**Duration:** ~1 day

- [x] `markdown_adapter.py` — reads .md, extracts frontmatter + content
- [x] `text_adapter.py` — reads .txt
- [x] `pdf_text_adapter.py` — PyMuPDF for native-digital PDFs
- [x] `url_adapter.py` — trafilatura for URL ingestion
- [x] `wiki_generator.py` — Claude Compile prompt → creates Wiki pages
- [x] `index_manager.py` — creates/updates flat INDEX.md
- [x] `token_tracker.py` — logs every API call cost to wiki_log
- [x] `ingest_compile_graph.py` — LangGraph: Upload → Read → Compile → Embed → Store → Git commit → Log
- [x] **Test passed:** Upload one article URL → Wiki pages in Supabase + INDEX.md + git log

---

## Sprint 2 — Query + Gatekeeper ✅ COMPLETE (needs polish)

**Goal:** Ask question → get cited answer → Gatekeeper decides if saved.
**Duration:** ~1 day

- [x] `hybrid_search.py` — calls RRF stored procedure
- [x] `synthesizer.py` — Claude synthesis with [[wikilink]] citations
- [x] `gatekeeper.py` — evaluates novelty × necessity × grounding
- [x] `compounding.py` — saves approved answers to `wiki/outputs/`
- [x] `query_graph.py` — LangGraph: Question → Embed → Search → Synthesize → Gate → Save? → Reply
- [x] Web UI: Ingest URL + Ingest File + Query sections
- [x] **Test passed:** Ask question → cited answer + Gatekeeper decision + cost displayed

**Still needed (Sprint 2 polish):**
- [x] `/ingest/paste` endpoint — `text_paste_adapter.py` + playground UI
- [x] Gatekeeper pre-check: hybrid_search before novelty eval (cosine > 0.85 check) — implemented via `gatekeeper_answer_precheck` + `gatekeeper_precheck_top_similarity` RPC (`hybrid_search.py`, `sql/004_gatekeeper_precheck_similarity.sql`)
- [x] Gatekeeper / validate_setup use current Haiku model id (`claude-haiku-4-5-20251001`)
- [x] `APIResponse[T]` envelope on all JSON routes
- [x] `processing_time_ms` middleware (auto-inject)
- [x] `module` column on `wiki_log` + `documents`
- [x] `wiki_log` writes in `wiki_generator`, `synthesizer`, `hybrid_search`
- [x] Max 3 compile retries guard in `ingest_compile_graph`
- [ ] Connect LangSmith (set `LANGCHAIN_API_KEY` in .env)

---

## Sprint 3 — Lint + Maintenance ✅ COMPLETE

**Goal:** On-demand audit + automated health maintenance.
**Duration:** ~1 week

- [x] `orphan_detector.py` — RegEx for broken [[wikilinks]] ($0)
- [x] `stale_detector.py` — flag pages not updated > 30 days
- [x] `contradiction_checker.py` — Claude structured JSON for conflicts (3-pass gated; prompts in `lint_contradiction_*.md`)
- [x] `deduplication.py` — cosine similarity > 0.92 → suggest merge (`find_duplicate_pages` RPC)
- [x] `confidence_decay.py` — monthly cron: -5%, archive < 0.30
- [x] `lint_graph.py` — LangGraph with `interrupt_before` on contradictions (HITL)
- [x] API: `POST /lint/run`, `POST /lint/resolve`, `POST /lint/decay`, `GET /lint/status`
- [x] n8n workflow: monthly confidence decay trigger (operator wires webhook to `POST /lint/decay`)
- [x] n8n workflow: weekly orphan detection (RegEx, $0) — callable via `POST /lint/run` or scheduled
- [x] Weekly cost report → Slack/UI notification (operator/n8n wiring — not hard-coded in repo)
- [x] **Test:** Run lint on Wiki with intentionally broken links + stale pages (manual / API)

**Auth (shipped 2026-04-12, ties lint + API to real tenants):**
- [x] Supabase Auth magic link
- [x] JWT → `tenant_id` dependency (`src/lib/auth.py`)
- [x] All endpoints use `Depends(get_current_tenant_id)`
- [x] Frontend auth headers (`_authHeaders()` on playground fetches)
- [x] Dynamic `SUPABASE_URL` / `SUPABASE_ANON_KEY` injection (`serve_ui` replaces `%%…%%` placeholders)

**Implementation notes:**
- `POST /lint/resolve` expects `thread_id` (from paused run) + `decisions` dict with keys as `slug_a__slug_b`
- `POST /lint/decay` requires `LINT_DECAY_WEBHOOK_SECRET` env var + `X-Lint-Decay-Token` header
- HITL resume uses MemorySaver (module-level) — works for single worker; migrate to PostgresSaver for multi-worker Hetzner deploy
- Contradiction merge via `apply_lint_contradiction_merge()` in `compounding.py` — authoritative page extended, other deprecated, INDEX.md line stripped, one git commit
- New file: `src/modules/lint/report_history.py` — `fetch_last_lint_report()` from wiki_log

**Manual steps required before first use:**
- Run `sql/005_deduplication_query.sql` in Supabase SQL Editor
- Add `LINT_DECAY_WEBHOOK_SECRET=<secret>` to `.env`

---

## Sprint 4 — Polish + Beta Access ✅ COMPLETE (deploy + beta items open)

**Goal:** Deploy to Hetzner. Give beta testers access. Daily use. Fix friction.

### Deploy
- [ ] Deploy to Hetzner via Coolify (Dockerfile ready)
- [ ] Set up domain/subdomain (compilore.twoja-domena.com)
- [ ] Configure env vars in Coolify
- [ ] Test from phone

### Pilot infrastructure prerequisite (before Wojtek onboarding)

- Add `organization_id` UUID NOT NULL column to `documents`, `wiki_pages`, `document_chunks` tables
- Update RLS policies to filter by `organization_id` instead of per-user
- Seed: `org_id = bartek_personal` for existing playground data, `org_id = hermes_pilot` for Wojtek
- Estimated effort: 1 Supabase migration + 2 RLS policy updates (~half day)
- Do this **before** Wojtek's first login — avoids data migration later

### Beta testers
- [ ] Create Supabase Auth accounts for 3 users (Bartek + żona + friend)
- [ ] Each user = separate tenant in Supabase
- [ ] Seed Wiki for each tester (20-30 articles in their domain)
- [ ] Write 1-page onboarding doc ("what to do on first login")

### Response Cards (Priority #1 for Sprint 4)
- [x] Response card component — F-pattern compliant layout:
  - Conclusion-first headline (synthesized by LLM, not "Answer to:")
  - Source chips as inline badge components
  - Confidence delta display ("↑ 0.70→0.85") not raw confidence score
  - Progressive disclosure: secondary context collapsed by default
- [x] Save-to-Wiki button server-side handler — POST /query/save implemented (2026-04-16)
- [x] Intent parser (`intent_parser.py`) — detect output format from natural language ("mindmap", "porównaj", "tabela", "mapa myśli", "/graph", etc.); strips directive before synthesis
- [x] `format_evaluator.py` — rule-based heuristics: evaluates answer metadata (entity count, page_types, step patterns) → returns suggested_formats[] JSON
- [x] Format suggestion chips in response card UI — 1-2 chips when evaluator confidence > threshold; `POST /query/format` + tooltips
- [x] Track format chip clicks in wiki_log — data for Phase 2 LLM-based evaluator training
- [x] Mindmap output — `POST /query/format` + Markmap (nested Markdown from LLM) in playground UI
- [x] Graph output — `POST /query/format` + Mermaid in playground UI
- [x] Card output — `POST /query/format` — structured summary (headline + 3 bullets + source chips)
- [x] Comparison table — `POST /query/format` + HTML table + UI panel
- [x] Protocol output — `POST /query/format` + protocol panel
- [x] Confidence delta tracking — previous top-page confidence in wiki_log (`query_response_card`), delta on next query
- [x] Response card component — comparison table, timeline, mindmap, code block, prose/list auto-detected via `detectFormat(query, answer)`
- [x] Output format: /mindmap → Mermaid syntax render (mermaid.js, dark theme)
- [x] Output format: comparison table auto-detect ("compare X with Y")

**Implementation notes:**
- `/query` now returns `QueryResponseCard` JSON (not raw Markdown) — any external scripts parsing old format need update
- `/query/format` body uses JSON key `format` (Pydantic alias `fmt`)
- Markmap falls back to monospace markdown block if CDN bundle differs
- `format_chip_click` logged to wiki_log `operation="format_chip_click"` — data for Phase 2 LLM evaluator
- New modules: `intent_parser.py`, `format_evaluator.py`, `output_formatter.py`, `page_metadata.py`, `format_analytics.py`
- New prompts: `format_response_card_headline.md`, `format_mindmap.md`, `format_graph.md`, `format_comparison_table.md`, `format_card.md`, `format_protocol.md`

### Quality + monitoring
- [ ] Refine prompts based on real usage (compile_wiki.md, query_synthesize.md)
- [ ] Incremental re-compilation: when source updated → only affected pages recompile
  (dependency tracking via frontmatter)
- [ ] `/status` endpoint → Wiki health dashboard in UI

### Decision gate
- [ ] **Go/No-Go for Phase 2:** Is the 4-loop architecture working? Am I using it daily?
  Does the Wiki compound? Honest self-assessment before writing Phase 2 code.

---

## Sprint 4b — Wiki Tree + Inspector (completed 2026-04-11) ✅

**Goal:** Real Wiki navigation from Supabase + format-aware query responses.

- [x] lib/types/wiki.ts — WikiPage, WikiPageDetail, WikiPageType
- [x] lib/supabase/server.ts — createSupabaseServerClient() with @supabase/ssr
- [x] middleware.ts — Supabase session refresh for Route Handlers
- [x] GET /api/wiki/pages — RLS-scoped, ordered by type+title, maps frontmatter.related[]
- [x] GET /api/wiki/pages/[slug] — full WikiPageDetail including content_markdown
- [x] hooks/use-wiki-pages.ts — SWR, 30s refresh, revalidateOnFocus
- [x] hooks/use-wiki-page-detail.ts — SWR single slug, 404→null
- [x] components/wiki-nav.tsx — live tree: sections, confidence dots, search, skeletons
- [x] components/wiki-nav-bridge.tsx — connects nav to WorkspaceContext
- [x] workspace-context.tsx — selectedWikiPage, selectWikiPage, openPageBySlug
- [x] inspector-panel.tsx — ReactMarkdown body, source citation banner, skeletons
- [x] command-palette.tsx — wiki fuzzy search uses useWikiPages()
- [x] lib/detect-response-format.ts — comparison|timeline|mindmap|list|code|prose
- [x] lib/query-submit-hint.ts — buildApiQueryForSubmission(), mindmap hint
- [x] components/response-formats/comparison-table.tsx — pipe table parser
- [x] components/response-formats/timeline.tsx — year extraction, animated dots
- [x] components/response-formats/mindmap.tsx — dynamic mermaid.js, dark theme
- [x] components/response-formats/code-block.tsx — Copy button, styled mono
- [x] components/response-card.tsx — format router, FORMAT_DISPLAY_LABELS badge
- [x] app/globals.css — animate-slide-in keyframe

**Blocked by:** ~~Supabase Auth in web UI~~ — **unblocked 2026-04-12** (Next.js app still uses own Supabase SSR; FastAPI playground + backend JWT live)
**Next:** Ensure Next.js workspace sends `Authorization` to `localhost:8001` where applicable; beta onboarding doc

---

## Sprint 5 — Local LLM Setup 🔲 PLANNED (parallel to deploy)

**Goal:** Switch query synthesis + gatekeeper from API to local Gemma 4.
Reduces monthly cost from ~$10-14 (all-API) to ~$0.50 (compile-only).

**Hardware:** MacBook Pro 14" M4 Pro 24GB RAM

**Model choice — two options:**

Option A — Quality priority (recommended, fits in 24GB with care):
`ollama pull gemma4:27b-q4_k_m`  (~16-17GB model + ~4GB system = ~20-21GB total)
Inference: ~12-18 t/s. 3-4GB buffer — works, monitor for SSD swap at 128K+ context.

Option B — Comfort priority (leaves headroom for parallel work):
`ollama pull gemma4:12b-q4_k_m`  (~8GB model, leaves 16GB free)
Inference: ~25-35 t/s. No RAM pressure. Quality sufficient for query/gatekeeper.

**Note on thermal throttling:** M4 Pro 14" smaller chassis than 16".
Under sustained load (10+ queries in a row) chip throttles → inference drops to ~8-10 t/s.
Not blocking, but worth knowing.

- [ ] Install Ollama on MacBook Pro: `brew install ollama`
- [ ] Pull model (start with Option B, upgrade to A if quality insufficient):
      `ollama pull gemma4:12b-q4_k_m`
- [ ] Create `src/lib/ollama_client.py` — OpenAI-compatible wrapper for Ollama API
      (Ollama exposes OpenAI-compatible endpoint at localhost:11434/v1)
- [ ] Update `src/graphs/query_graph.py`: route synthesis to Ollama when 
      `OLLAMA_ENABLED=true` in env, fall back to Sonnet if Ollama unavailable
- [ ] Update `src/modules/query/gatekeeper.py`: route evaluation to Ollama
- [ ] Add to `.env.example`: `OLLAMA_ENABLED=false`, `OLLAMA_MODEL=gemma4:12b-q4_k_m`,
      `OLLAMA_BASE_URL=http://localhost:11434/v1`
- [ ] Benchmark: run 20 real queries from Wiki, compare Sonnet vs local on:
      answer quality (manual rating 1-5), citation accuracy, response time
- [ ] If 27B quality acceptable and RAM stable: switch OLLAMA_MODEL to gemma4:27b-q4_k_m
- [ ] Keep Sonnet as fallback: if Ollama returns error or times out → auto-retry with Sonnet

**Note:** Compile stays on Sonnet permanently. Do NOT route compile to local model.
**Note:** Sprint 5 runs locally only — Ollama does NOT deploy to Hetzner (no GPU there).
Hetzner stays API-only. Local = personal use cost reduction only.

---

## Phase 2 Sprint 0 — Validation (Before Any Code)

**Trigger:** Phase 1 decision gate passed.
**Goal:** Validate market before writing Phase 2 code.

- [ ] 15 architect interviews; 7/10 must cite MPZP as burning pain
- [ ] Landing page: architects upload real MPZP to join waitlist. Target: 5-10 docs
- [ ] Hyper-personalized Loom demos: parse real MPZP from prospect's municipality. Send 3. Measure response rate.
- [ ] 2 Letters of Intent for paid pilot (~$250 for archive compilation)
- [ ] 1 public case study: hardest MPZP in Poland → parse with Compilore → post publicly
- [ ] **Decision:** proceed to Phase 2 technical build or pivot

---

## Pre-Pilot Sprint — HermesTools Readiness (2026-04-17)

**Goal:** System ready for Wojtek's first login. No known quality 
regressions for industrial catalog PDFs.
**Trigger:** Domain/SSL setup complete (pending).

### Infrastructure
- [x] organization_id column added to all tenant tables
- [x] RLS policies updated to org-scoped isolation
- [x] hermes-pilot org seeded (id: a6d3721a-0000-0000-0000-000000000002)
- [x] hybrid_search() updated with organization_id parameter
- [ ] Run migration on Supabase: 
      `supabase/migrations/20260417_organization_isolation.sql`
- [ ] Add Wojtek's Supabase Auth account to hermes-pilot org 
      (after domain/SSL)

### PDF Quality
- [x] docling_adapter.py implemented with TableFormer ACCURATE
- [x] OOM safeguards: OMP_NUM_THREADS=1, page-by-page, gc.collect()
- [x] PyMuPDF fallback preserved for simple text PDFs
- [ ] Install docling: `pip install docling` in venv + 
      update requirements.txt
- [ ] Test: upload one KOLVER catalog PDF → verify tables extracted 
      as Markdown → ask parametric question → verify citation 
      includes page number

### Pilot config
- [ ] Update 09_PILOT.md trial reference from 7 days → 14 days 
      (already in docs, confirm in any UI copy)
- [ ] Verify Fakturownia invoice template has QR code for KSeF 
      compatibility (manual check by Bartek)
- [ ] Biała Lista: send NIP-2 update to US with bank account 
      (manual action by Bartek — before first paid invoice)

---

## Backlog (Unscheduled)

Items that are defined but not yet assigned to a sprint:

| Item | Category | Notes |
|---|---|---|
| YouTube adapter | Ingestion | youtube-transcript-api + yt-dlp fallback |
| Instagram adapter | Ingestion | SociaVault API + n8n integration |
| Twitter/X adapter | Ingestion | SociaVault API |
| GitHub adapter | Ingestion | raw.githubusercontent.com + GitHub API |
| HN adapter | Ingestion | Algolia HN API |
| Podcast/audio adapter | Ingestion | RSS + Faster-Whisper local |
| Substack paywall adapter | Ingestion | Cookie injection |
| TikTok adapter | Ingestion | JSON hydration or SociaVault |
| Gemma 4 local (Ollama) | LLM routing | Sprint 5 |
| Presentation output `/deck` | Output formats | Phase 2 |
| Infographic output | Output formats | Phase 2 |
| Next.js web UI redesign | UI | Phase 2 |
| Bento grid / response cards UI | UI | Sprint 4 |
| n8n webhook → auto-ingest | Automation | Phase 2 |
| Mobile PWA | Mobile | Phase 2+ |
| Docling PDF parser | ✅ PULLED FORWARD | Implemented for HermesTools industrial catalogs (D-75). See src/modules/ingest/docling_adapter.py |
| Kreuzberg async PDF | Phase 2 | Replace PyMuPDF |
| PII stripping middleware | Phase 2 | spaCy NER + RegEx |
| Technical Advisor query flow wiring | ICP — Technical Advisor | ✅ done 2026-04-16. Feature flag: TECHNICAL_ADVISOR_MODE=true in .env. Default off. Core query_graph.py untouched. |
| Technical Advisor Docling table extraction | ICP — Technical Advisor / Phase 2 | Replace PyMuPDF for manufacturer catalogs. TableFormer ACCURATE mode. See adapters/technical_advisor/README.md |
| PreResponseChecklist in gatekeeper | Quality | Self-verification loop after evaluation: gatekeeper checks own reasoning vs N×N×G criteria. ~14pp quality improvement per GapRoll harness research. TODO already in `gatekeeper.py` docstring. |
| VLM fallback (GPT-4o Vision) | Phase 2 | Scanned pages/maps |
| plan_ogolny_adapter.py | Phase 2 | Distinct from MPZP (reform 2026) |
| Kinde auth migration | Phase 2 | SSO/SAML |
| DPA/DPIA/Regulamin | Phase 2 legal | Before first paying client |
| OC insurance | Phase 2 legal | 1-3M PLN |
| ZDR application to OpenAI | Phase 2 legal | Start early |
| `POST /generate/proposal` endpoint | Output / Sales | Generate client proposal using Wiki context (previous proposals as format anchors + client data + sprint/pricing history). Priority: HIGH for sales team pilot segment. |
| `generate_proposal.md` prompt | Prompts | New dedicated prompt at `src/config/prompts/generate_proposal.md` |
| Proposal output persistence | Output / Wiki | Save to `wiki/outputs/proposals/` with atomic git commit |

Decision traceability: Department isolation and i18n foundations for Phase 2 implementation are tracked as `D-59` and `D-60` in `docs/04_DECISIONS.md`.
