# 04 — DECISIONS
## Compilore: Decision Log

**Format:** Every significant decision is logged here with rationale and date.
When a decision is reversed, the old entry is marked SUPERSEDED and a new entry added.
This file answers "why did we do it this way?" forever.

**Last updated:** 2026-04-17

---

## Numbering Conventions

- Decision IDs are monotonically increasing and **globally unique**. Once assigned, an ID is never reused.
- When a research round (e.g. DR-7, DR-8) proposes draft IDs that collide with already-locked IDs, the whole block is renumbered to the next free range; a `*re-numbered …*` note is preserved in the affected section.
- `D-36–D-38` are **reserved / never assigned** (see DR-7 renumbering note below). Do not reuse.
- `D-52–D-57` are **reserved / renumbered** — originally assigned to DR-8 GIS LEGAL, later re-numbered to `D-61–D-68` to avoid colliding with OUTPUT FORMAT `D-50`/`D-51` (see DR-8 renumbering note below). Do not reuse.
- When a decision is reversed, the original row is moved to `SUPERSEDED` and suffixed with `-orig` (see `D-02-orig`). A fresh ID is minted for the replacement.

---

## LOCKED — Core Decisions (Do Not Revisit Without Strong Evidence)

| # | Decision | Choice | Rationale | Date |
|---|---|---|---|---|
| D-01 | Separate project from GapRoll | New repo, new Supabase, own domain | Clean separation. GapRoll ToS issues with Claude don't apply here. | 2026-04-09 |
| D-02 | Phase 1 interface | Web UI (local → Hetzner) | Viktor/Slack was original plan but web UI ships faster and works for beta testers | 2026-04-09 |
| D-03 | Phase 2 interface | Next.js web app | Architects don't use Slack | 2026-04-09 |
| D-04 | Vector store | pgvector (Supabase) | $0 incremental cost, handles <5M vectors, hybrid search in single SQL query | 2026-04-09 |
| D-05 | Hosting | Hetzner + Coolify | EU data sovereignty, RODO compliant, €12.90/mo | 2026-04-09 |
| D-06 | Agent framework | LangGraph | Deterministic, HITL via interrupt_before, PostgresSaver checkpointing | 2026-04-09 |
| D-07 | Lint mode | On-demand ONLY | Autonomous background lint = "Agentic Loop of Death" = uncontrolled spend | 2026-04-09 |
| D-08 | Embeddings | OpenAI text-embedding-3-small | 1536 dims, ~$0.001/1M tokens, sufficient quality | 2026-04-09 |
| D-09 | Phase 2 pricing model | Usage-based, not flat-rate | API costs are variable. Flat-rate at scale = bankruptcy | 2026-04-09 |
| D-10 | Payment stack (Phase 2) | Fakturownia + Przelewy24 | Stripe has no JPK_FA support. Polish B2B prefers bank transfer/BLIK | 2026-04-09 |
| D-11 | Phase 2 auth | Kinde | SSO/SAML for enterprise clients. Migration from Supabase Auth at Phase 2 launch | 2026-04-09 |
| D-12 | Adapter pattern | New isolated module for every new source/format | Core engine stays clean. Industry logic never bleeds into base | 2026-04-09 |
| D-33 | APIResponse[T] envelope | Required on all JSON routes | Agent-readiness: external integrations (Viktor, future MCP) need structured metadata. Learned from GapRoll cross-project reference. Implemented via HTTP middleware for auto `processing_time_ms` injection. | 2026-04-12 |
| D-34 | `module` column on `wiki_log` and `documents` | All rows must set `module` = source adapter/module name | Prevents migration hell at scale. 500 logs with `module=NULL` = undebuggable. Lesson from GapRoll. | 2026-04-12 |
| D-35 | Max 3 compile retries in `ingest_compile_graph` | `max_retries=3`, `compile_retry_count` tracked in state | Prevents agentic loop of death in compile path. 3 failures = structural document problem, not transient error. | 2026-04-12 |

---

## COMPILE LOOP DECISIONS

| # | Decision | Choice | Rationale | Date |
|---|---|---|---|---|
| D-13 | LLM for Compile | Claude 3.7 Sonnet (API) — permanent | Quality of structured Markdown is permanent in the Wiki. Gemma 4 31B scores better on IFBench but compile is ~$0.07/doc at current volume — acceptable. Revisit at Phase 2 scale. | 2026-04-11 |
| D-14 | git_commit_hash in frontmatter | Yes — add to every wiki_page frontmatter | Enables rollback without new infrastructure. `git checkout <hash> -- wiki/page.md` + re-embed. Identified from Gemini analysis 2026-04-09 | 2026-04-09 |

---

## QUERY LOOP DECISIONS

| # | Decision | Choice | Rationale | Date |
|---|---|---|---|---|
| D-15 | Gatekeeper evaluation criteria | Novelty × Necessity × Grounding (3 criteria) | Standard pattern. All three must pass for write. | 2026-04-09 |
| D-16 | Gatekeeper pre-check | hybrid_search before novelty eval; if cosine > 0.85 with existing page → Gatekeeper sees "already exists at [[X]]" | Prevents duplicate output pages as Wiki grows. Cost: ~$0.001 per query. Identified 2026-04-09 | 2026-04-09 |
| D-17 | LLM for Query synthesis | Migrating from Claude Sonnet → Gemma 4 31B Dense (local, Ollama) | High frequency operation, $0 marginal cost. 31B Dense has 78.7% IFBench vs Sonnet 74.7%. 100% agentic reliability. | 2026-04-11 |
| D-18 | LLM for Gatekeeper | Migrating from Claude Haiku → Gemma 4 31B Dense (local, Ollama) | Simple classification. Local = $0. | 2026-04-11 |
| D-19 | Citation trail | Every answer MUST have verifiable citation to source doc + page/section | Hard requirement. Architects perform "shadow testing" — they verify answers against known projects. One wrong answer = tool discarded permanently. Not a UX nicety, a conversion gate. | 2026-04-11 |

---

## INGESTION DECISIONS

| # | Decision | Choice | Rationale | Date |
|---|---|---|---|---|
| D-20 | Phase 1 text extraction | trafilatura for URLs | Simple, works, free. Upgrade to Firecrawl (self-hosted) at Phase 2 if quality issues arise | 2026-04-09 |
| D-21 | PDF extraction Phase 1 | PyMuPDF (sync) | Simple, works for native-digital PDFs. Replace with Kreuzberg (async) at Phase 2 for non-blocking FastAPI | 2026-04-09 |
| D-22 | Instagram/TikTok transcript | SociaVault API | 1 credit per transcript regardless of length. Growth pack $79/20K = $0.004/transcript. 80x cheaper than GetTranscribe, more reliable than Apify headless actors | 2026-04-11 |
| D-23 | Twitter/X thread extraction | SociaVault API | Official X API $100-5000/mo. Apify brittle on virtualized DOM for >50 tweets. SociaVault $29/6000 credits | 2026-04-11 |
| D-24 | Spotify podcast | RSS feed → local Faster-Whisper | No legitimate API path for Spotify transcripts. RSS available for non-exclusive podcasts. Local Whisper = GDPR compliant (audio never leaves EU) | 2026-04-11 |
| D-25 | Audio transcription | Faster-Whisper (self-hosted, Large-v3 model) | 4x faster than original Whisper. Handles Polish diacritics + PL/EN code-switching. $0 per minute. GDPR compliant. | 2026-04-11 |
| D-26 | Hacker News ingestion | Algolia HN API (not Firebase) | Firebase API has N+1 problem: 500 comments = 500 HTTP requests. Algolia: single request returns full nested thread with hierarchy preserved. Hierarchy matters for LLM synthesis. | 2026-04-11 |
| D-27 | Substack paywalled content | Authenticated cookie injection (substack.sid + substack.lli) | Only for own paid subscriptions. Private PKB use only. Never redistribute. Cookies require periodic manual rotation. | 2026-04-11 |
| D-28 | Text paste input | Direct POST to `/ingest/paste` endpoint | Trivially simple (~20 lines). Cheapest compile ($0.03 for a snippet). Missing from initial build — add Sprint 2. | 2026-04-11 |
| D-29 | Article extraction quality | trafilatura (current) → Firecrawl self-hosted (Phase 2) | Firecrawl: native JS rendering, recursive sitemap discovery, clean Markdown output. AGPL-3.0 = self-hostable. Better signal/noise for RAG. Defer until quality issues appear. | 2026-04-11 |

---

## LLM MODEL DECISIONS

| # | Decision | Choice | Rationale | Date |
|---|---|---|---|---|
| D-30 | Local LLM model choice | Gemma 4 31B Dense (NOT 26B A4B MoE) | MoE systematically produces malformed YAML/JSON — trailing garbage tokens, broken schema. 3.8B active parameters insufficient for deterministic formatting. This is architectural, not fixable. 31B Dense: 78.7% IFBench, 100% agentic simulation survival, OmniDocBench 0.131. | 2026-04-11 |
| D-31 | Local LLM quantization | Q4_K_M | Metal-accelerated on Apple Silicon. Near-lossless quality. ~17-20GB RAM. MoE would require IQ4_XS (iMatrix) — poor Metal optimization, still broken schema. | 2026-04-11 |
| D-32 | Local LLM runtime | Ollama + MLX backend | Auto-uses Apple MLX for faster inference on Apple Silicon. No manual configuration. | 2026-04-11 |

---

## OUTPUT FORMAT DECISIONS

| # | Decision | Choice | Rationale | Date |
|---|---|---|---|---|
| D-39 | Presentation output format | Marp → PPTX (not Slidev) | Slidev requires Vue syntax — high LLM hallucination risk. Marp: pure Markdown with --- separators → PPTX/PDF. Export fidelity critical for enterprise use. | 2026-04-11 |
| D-40 | Lint contradiction check architecture | Gated 3-pass: Detect → Plan → Implement (HITL between each) | Single-pass prompts produce hallucinated contradictions. 3-pass: pass 1 lists conflicts, pass 2 proposes merges, pass 3 only after human approval. Reduces context bloat. | 2026-04-11 |
| D-41 | Format selection UX | Proactive suggestion chips + natural language (hybrid) | Rule-based heuristics evaluate answer shape after synthesis → suggest 1-2 relevant formats as clickable chips. User can also type format intent in natural language. Heuristics: ≥3 entities with parallel attributes → comparison_table; ≥4 wiki_pages of different types → mindmap; ≥3 sequential steps → protocol; single long content → card. Rule-based = $0, zero latency. LLM-based format evaluation deferred to Phase 2 when usage data exists. | 2026-04-11 |
| D-42 | Mind map renderer | Markmap (not Mermaid, not D3.js) | LLM outputs standard nested Markdown. Markmap renders as SVG. ~30 token cost, zero hallucination risk, zero extra LLM call. D3.js rejected: coordinate state persistence is unsolved engineering problem for dynamic AI-generated nodes. | 2026-04-11 |
| D-43 | Phase 2 UI paradigm | Wiki Graph Browser (not chat UI) | Spatial epistemology model (Heptabase). Concept pages as nodes, [[wikilinks]] as edges. Compounding must be visually explicit — this is Compilore's core differentiator vs RAG. | 2026-04-11 |
| D-44 | Response card design | F-pattern + atomic interactivity + delta-first | Cognitive load research: users scan F-pattern, atomic cards require no navigation, delta (change over time) is more actionable than raw scores. Every response card: conclusion headline, source chips, confidence delta, Save-to-Wiki toggle in-card. | 2026-04-11 |
| D-50 | Audio summary output (`/audio`) | Custom `audio_summary.py` (NOT Podcastfy library) | Podcastfy is optimized for dialogue, not monologue summary. Single maintainer = abandonment risk. Our synthesizer already produces the input. Implementation: Sonnet generates spoken-word transcript (~$0.01) → OpenAI `tts-1` TTS (~$0.15 per 10K chars). Voice: `onyx` (neutral) or `nova` (conversational). Polish language supported natively by OpenAI TTS. Zero new dependencies beyond existing OpenAI SDK. Podcastfy used as architecture reference only. | 2026-04-13 |
| D-51 | Presentation deck templates | Multi-template system (NOT SCQA-only) via Marp → PPTX | SCQA alone is insufficient — different use cases need different structures. Six templates: `executive_brief` (SCQA + single recommendation), `data_story` (context → trend → implication), `status_update` (status → risks → next steps), `comparison` (2-3 columns, pros/cons, recommendation), `process_flow` (swimlane or step-by-step), `executive_summary` (3-5 bullets + So What). LLM selects template based on intent or user choice. Marp renderer unchanged (D-39). | 2026-04-13 |

---

## GIS SPATIAL ENGINE — PRODUCT & GTM (DR-7, 2026-04-12)

*IDs D-45–D-49: numeracja „D-33–D-37” z DR-7 przesunięta, bo D-33–D-35 w LOCKED dotyczą już API envelope / `module` / compile retries. IDs **D-36–D-38 are reserved and intentionally unassigned** — do not reuse.*

| # | Decision | Choice | Rationale | Date |
|---|---|---|---|---|
| D-45 | Primary product pivot | GIS Spatial Engine jako produkt priorytetowy, Compilore jako secondary | Painkiller > Vitamin; wyższe ARPU; krótszy czas do walidacji | 2026-04-12 |
| D-46 | Primary customer segment | Deweloperzy MŚP (5–50 projektów/rok), nie fundusze PE | Krótszy cykl sprzedaży (1–3 tyg. vs 3–6 msc); właściciel decyduje bez procurement | 2026-04-12 |
| D-47 | GIS data resilience | Trzy źródła z failover: Rejestr Urbanistyczny API → Geoportal WFS → BIP scraper. Nie uzależniać od jednego źródła | Rejestr Urbanistyczny może nie być gotowy przed sierpniem 2026 | 2026-04-12 |
| D-48 | Legal disclaimer mandatory | Każda odpowiedź systemu musi zawierać: „Dane informacyjne z rejestrów publicznych. Wymagana weryfikacja przez uprawnionego specjalistę przed złożeniem wniosku WZ” | Ochrona przed ryzykiem prawnym (opinia urbanistyczna może wymagać uprawnień) | 2026-04-12 |
| D-49 | Concierge test before build | 3–5 ręcznych analiz OUZ+POG dla deweloperów za 500–1,500 PLN przed budową produktu | Walidacja WTP empirycznie, nie teoretycznie | 2026-04-12 |

---

## GIS SPATIAL ENGINE — LEGAL & COMPLIANCE (DR-8, 2026-04-12)

*W briefie DR-8 użyto oznaczeń D-38–D-45. Pierwotnie nadano **D-50–D-57**, ale te IDs kolidowały z OUTPUT FORMAT D-50 / D-51 (audio, deck templates, 2026-04-13). Finalna numeracja: **D-61–D-68**. Treść decyzji = DR-8.*

| # | Decision | Choice | Rationale | Date |
|---|---|---|---|---|
| D-61 | Terminologia produktu | Tylko: „raport parametrów przestrzennych”, „kalkulacja algorytmiczna”, „zestawienie danych wektorowych”. Zakaz terminologii zawodów regulowanych | Ustawa 2014 deregulacja + granica art. 12 PB. Priorytet: krytyczny | 2026-04-12 |
| D-62 | Timestamp na każdym wyniku | Źródło pliku GML + data + ID rekordu na każdym parametrze. Logi po stronie serwera | Art. 417 KC — przeniesienie odpowiedzialności na gminę. Priorytet: krytyczny | 2026-04-12 |
| D-63 | Liability Cap w ToS | Max = 12 msc subskrypcji. Wyłączenie *lucrum cessans*. Indemnification clause | Art. 473 § 1 KC + PLD 2024/2853. Krytyczny — prawnik przed launch | 2026-04-12 |
| D-64 | Zero KW w systemie | Absolutny zakaz pobierania KW | NSA 2025–26, UODO. Priorytet: krytyczny | 2026-04-12 |
| D-65 | DPA monitoring portfela | DPA jako załącznik ToS dla funkcji śledzenia działek | RODO — klienci JDG. Przed launch | 2026-04-12 |
| D-66 | UI: tabele i mapy, nie bryły | Parametry + mapy stref, nigdy wizualizacje architektoniczne | Granica art. 12 PB. Decyzja produktowa | 2026-04-12 |
| D-67 | ToS przed PLD grudzień 2026 | Wdrożyć umowy przed 9 grudnia 2026 | PLD 2024/2853. Ważny — timing | 2026-04-12 |
| D-68 | Multitenancy izolacja | Portfel każdego klienta w izolowanej przestrzeni danych | RODO art. 25. Wymóg techniczny | 2026-04-12 |

---

## D-58: Multi-tenant auth — invite-only (magic link)

**Date:** 2026-04-12

**Decision:** Supabase Auth magic link, invite-only (no self-registration). Each user maps to one tenant via `user_profiles` table. JWT extracted per-request via FastAPI `Depends(get_current_tenant_id)` in `src/lib/auth.py`. `/lint/decay` exempt from JWT (n8n webhook, uses `COMPILORE_DEFAULT_TENANT_ID`). Frontend: Supabase JS UMD, `_authHeaders()` on all API calls, `%%SUPABASE_URL%%` / `%%SUPABASE_ANON_KEY%%` injected at runtime by FastAPI `serve_ui` route.

**Rejected:** Full registration flow (too slow for beta, token cost risk).

---

| # | Decision | Choice | Rationale | Date |
|---|---|---|---|---|
| D-69 | Technical Advisor ICP — Phase 1 approach | New compile/query/gatekeeper prompts only (no core changes). technical_parameter_filter.py as isolated post-search module. PyMuPDF for Phase 1 with documented table extraction limitation communicated to pilot user. Query flow wiring deferred to pilot start. | Adapter Pattern + Sacred Modularity respected. Pilot user (technical advisor, industrial distribution) validated as first external beta. Core Engine untouched. | 2026-04-16 |

---

## DEFERRED — Decisions Explicitly Not Made Yet

These are real questions, but not yet time to answer them:

| Topic | Why Deferred | When to Decide |
|---|---|---|
| Frontend UI design (Phase 2) | Depends on Phase 1 learnings | Phase 2 Sprint 0 |
| Payment integration | After first paying client | Phase 2 |
| Output formats: presentations, infographics | → See D-50 (audio), D-51 (deck templates), Phase 2. | Sprint 4 |
| Mobile UX (PWA vs native) | Validate on desktop first | Sprint 4 |
| Phase 2 Go/No-Go | Decision gate at Sprint 4 | End of Sprint 4 |
| Public MPZP knowledge pool (data moat) | Phase 3 feature | Post-PMF |
| Fine-tuning on compiled Wiki data | Post-PMF | Post-PMF |
| Multiple industry adapters beyond architect | Phase 3+ | Post-PMF |
| Voice interface | Phase 4 | — |
| 385-document statistical validation | Phase 2 production | Phase 2 |
| Proactivity / push notifications | Phase 3 | — |
| Exit strategy timing | Przy $1–2M ARR ocenić czy EU expansion vs Transaction platform vs exit | Rok 2–3 |
| Weryfikacja prawna: czy „analiza informacyjna GIS” wymaga uprawnień urbanistycznych? | Konsultacja prawnik | Phase 2 Sprint 0, **PRZED launch** |
| OpenStreetMap fallback dla OUZ | Gdy jakość danych EGiB poniżej 70% dla danego powiatu | Phase 2 Sprint 1 |

---

## SUPERSEDED — Changed Decisions

| # | Original decision | What replaced it | Why | Date changed |
|---|---|---|---|---|
| D-02-orig | Phase 1 interface = Viktor/Slack | Web UI (localhost → Hetzner) | Web UI built and working in Phase 1. Slack adds complexity without benefit for playground phase. | 2026-04-11 |

---

## BEACHHEAD PIVOT — B2B Technical Distribution (2026-04-16)

*Originally drafted as D-50–D-54; renumbered to **D-70–D-74** for uniqueness against existing D-50 (audio) / D-51 (deck templates) and the DR-8 GIS LEGAL block.*

| # | Decision | Choice | Rationale | Date |
|---|---|---|---|---|
| D-70 | Beachhead pivot | B2B technical distribution (HVAC, electrical wholesale) replaces Polish architectural firms as Phase 2 primary target | Architects = vitamin. Distribution advisors = painkiller with quantified €1,000+/msc/employee cost. No existing architect relationships lost. Wojtek pilot = direct conversion path to first corporate client. | 2026-04-16 |
| D-71 | Pricing model for Phase 2 | Team-tier flat fee (Solo / Team / Company / Enterprise), NOT per-seat | Per-seat triggers SME sticker shock. Flat team tier anchors on org value. Usage limits only above tier thresholds. | 2026-04-16 |
| D-72 | Citation as hard requirement | Every answer must include source document name + page number. Answer without citation = not displayed. | In safety-critical B2B (HVAC, electrical, medical), wrong answer = physical/financial/regulatory damage. Citation trail is the product differentiator, not a UX nicety. DR-1 shadow testing behavior confirms: one wrong answer = tool discarded permanently. | 2026-04-16 |
| D-73 | Organization_id isolation | Multi-tenant architecture must enforce `organization_id` as hard DB boundary. No cross-org data leakage. | Team model requires strict data isolation. Firm A's manufacturer catalog chunks must never appear in Firm B's search results. | 2026-04-16 |
| D-74 | GTM channel for B2B distribution | Trade shows + champion-led (Wojtek → his company → adjacent firms). NOT LinkedIn-first, NOT cold email. | Sector trust deficit is real (17% cite distrust as primary barrier). Physical demo at trade show = highest conversion for this demographic. | 2026-04-16 |

---

## ARCHITECTURE DECISIONS — 2026-04-17

| # | Decision | Choice | Rationale | Date |
|---|---|---|---|---|
| D-59 | Department isolation model | Option B chosen: default open within tenant + department-scoped pages | Passes Lean Test. Option A (hard silos) rejected: cross-department knowledge sharing (e.g., client info visible to sales + legal) is a core use case. Option C (per-page ACL) deferred to Phase 3. | 2026-04-17 |
| D-60 | i18n strategy | Infrastructure-first: externalize strings now, translations deferred | Zero cost to do foundations correctly now; high retrofit cost later. | 2026-04-17 |

---
