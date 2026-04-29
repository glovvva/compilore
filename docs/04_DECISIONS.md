# 04 — DECISIONS
## Compilore: Decision Log

**Format:** Every significant decision is logged here with rationale and date.
When a decision is reversed, the old entry is marked SUPERSEDED and a new entry added.
This file answers "why did we do it this way?" forever.

**Last updated:** 2026-04-27

---

## ARCHITECTURE & STRATEGY DECISIONS (2026-04-27)

Context: Three analysis sessions — (1) pre-mortem on 12 failure scenarios,
(2) ProcessOS × Compilore synergy and headless architecture debate,
(3) language-agnostic wiki and cross-lingual query support.

| # | Decision | Choice | Rationale | Date |
|---|---|---|---|---|
| D-97 | Confidence decay — page_type-aware rules | Engineering/catalog pages: 0% decay. Output pages: -5%/month. Source_summary pages: -2%/month. Index pages: 0% decay. | Physical engineering constants (thermodynamics, fluid dynamics, material properties) do not rot. Flat -5% applied uniformly creates two failure modes: (1) valid engineering data gets archived as stale after 20 months despite still being correct, (2) alert fatigue — users batch-approve "verify" prompts without reading, defeating gatekeeper. Pre-mortem Scenario 11 confirmed this is existential at scale. DR-15 elevated from research backlog to locked decision. Implementation required before Step 0 sign-off. | 2026-04-27 |
| D-98 | Pilot document scope gate (Wojtek) | Maximum 30 documents for initial Wojtek pilot batch. Documents must be modern PDF (text-selectable). Scanned-only PDFs deferred to Phase 2 Docling batch. | Docling TableFormerMode.ACCURATE is Phase 2 technology. Current Phase 1 parser (PyMuPDF) will produce cascading table-chunking failures on scanned tabular data. Pre-mortem Scenario 10 (Onboarding Cliff) is existential — solo founder manually cleaning 300 PDFs halts all sales. Scope gate is cheaper than rushing Phase 2 tech into Phase 1. Wojtek briefed to start with his 20-30 most-used modern catalogs. | 2026-04-27 |
| D-99 | knowledge_class frontmatter field | Add `knowledge_class` to wiki_pages frontmatter (JSONB). Three values: `explicit_normative` (official manufacturer doc, certified catalog, regulatory text — authoritative, 0% extra decay penalty), `explicit_derived` (AI-compiled synthesis with citation trail — standard decay applies per page_type), `empirical_descriptive` (reserved for ProcessOS Living Playbooks, Phase 3+). Default for all current pages: `explicit_normative` if `source_documents` references an uploaded document, else `explicit_derived`. | Enables trust tiering in query responses (normative source vs AI synthesis). Required infrastructure for ProcessOS integration (D-101). Useful standalone: user can see whether an answer comes from official manufacturer doc vs AI-compiled summary. Lint loop extended to flag Normative vs Derived conflicts as "Pathology Alert" rather than auto-merging. | 2026-04-27 |
| D-100 | Silent API fallback — RODO vector | API fallback from local Gemma → Claude/OpenAI must NEVER be silent. If fallback is triggered: (1) log event to `wiki_log` with `operation=api_fallback`, (2) surface explicit notification to user in UI, (3) require user acknowledgement before processing continues. | Pre-mortem Scenario 7 confirmed: silent routing of client data to external API without notification is a direct RODO violation. Client may have uploaded confidential trade secrets assuming local-only processing. Silent fallback invalidates the "local Gemma = data stays local" trust promise. Explicit fallback is also a feature: user can choose to cancel and re-upload to ZDR endpoint instead. | 2026-04-27 |
| D-101 | ProcessOS architecture — dual-layer model (SUPERSEDES draft D-101 from session notes) | ProcessOS has TWO layers: (1) Minimal UI for process visualization only (swimlane diagrams, timeline, anomaly highlight, bottleneck heatmap) — no search, no knowledge base, no query engine. (2) Living Playbook output = headless Markdown artifact committed to Compilore git repo with frontmatter `knowledge_class: empirical_descriptive`. Single query engine = Compilore. | Purely headless ProcessOS (no UI at all) was rejected because: process visualization is fundamentally non-textual — swimlanes, timelines, and bottleneck heatmaps require dedicated rendering that Compilore's Markdown wiki cannot provide; removing process UI entirely degrades adoption for the manager persona who needs to see the process to trust it. However, ProcessOS must NOT have its own knowledge base, search, or query engine — that fragments the corpus and forces users to context-switch for knowledge queries. Resolution: visualization UI yes, knowledge layer no. One source of truth = Compilore git repo. | 2026-04-27 |
| D-102 | Grant advisor incentive model — correction | Grant advisor channel does NOT operate on SaaS rev share per client per month. Correct model: (1) advisor helps client win Dig.IT / RPO grant (grant value: 150K–850K PLN); (2) advisor takes standard success fee from total grant value (5–8% industry rate, paid by client from grant proceeds); (3) Compilore is line item in client's grant application framed as "AI/ML analytics system" or "automated process knowledge platform"; (4) Compilore pays NO direct commission to advisor. Compilore provides: Polish-language ROI calculator, technical specification document for grant application, pricing in PLN, reference case study post-pilot. | D-84 described 5% recurring rev share — this is economically broken for grant advisors (75 PLN/month = no behavioral change). Pre-mortem Scenario 6 confirmed. Correct model aligns with how grant consultants actually earn: they are compensated by the client from the grant, not by the SaaS vendor. Compilore's role is to provide application-ready materials that make Compilore easy to include as a grant line item. | 2026-04-27 |
| D-103 | Cross-lingual query support — Phase 2 | Phase 2 supports queries in any EU language (PL/EN/DE/CS/SK minimum). Architecture: (1) user asks in any language, (2) `text-embedding-3-small` handles cross-lingual embedding natively (already multilingual), (3) LLM synthesis (Claude) answers in the language of the question, (4) source documents remain in original language — no translation of corpus required. Test trigger: include in Wojtek pilot — have him ask a Polish-language question about an English-language catalog. If retrieval miss rate >15% on cross-lingual queries → activate D-104. | Enables: one tenant, multiple users in different countries, same knowledge corpus. Target use case: distributor with Polish HQ and Czech/Slovak branch — single catalog wiki, local-language queries. Zero additional infrastructure — this is native capability of Claude + text-embedding-3-small. D-60 (i18n infrastructure-first) already covers UI translation; D-103 covers corpus query layer. | 2026-04-27 |
| D-104 | Cross-lingual ingestia — DEFERRED | Translation during ingest (source document → canonical EN chunks + original stored) is NOT implemented in Phase 1 or Phase 2 baseline. Activation trigger: pilot data shows cross-lingual retrieval miss rate >15% on real Wojtek queries. If triggered: DeepL API or Claude Haiku for translation at ingest time (~$0.002/page), store both `chunk_text_original` and `chunk_text_canonical_en` in `document_chunks`, embed canonical version for retrieval, display original + translation toggle in UI. | Pre-emptive translation adds cost and complexity before evidence of need. `text-embedding-3-small` cross-lingual quality is sufficient for PL/EN/DE without translation layer in most cases. Defer until empirical signal from pilot. | 2026-04-27 |

---

## SUPERSEDED DECISIONS

| Original # | Superseded by | Reason | Date |
|---|---|---|---|
| Draft D-101 (session notes, headless-only ProcessOS) | D-101 (2026-04-27) | Headless-only rejected: process visualization requires dedicated UI. Dual-layer model adopted. | 2026-04-27 |
| D-84 rev-share model description | D-102 (2026-04-27) | 5% recurring SaaS rev share economically broken for grant advisors. Grant-application model adopted. | 2026-04-27 |

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
| D-80-v1 | HermesTools ERP angle | D-94 | Trigger: pilot outcome determines disclosure; POST-BEACHHEAD block minted at D-84–D-88 (2026-04-20), ERP disclosure row moved to D-94 | 2026-04-19 |
| D-84-orig-erp | HermesTools ERP disclosure timing (2026-04-19 row) | D-94 | Numeric ID D-84 reassigned to POST-BEACHHEAD strategy block (grant writer partnership, 2026-04-20). | 2026-04-20 |
| D-85-orig-audit | Audit-deadline positioning deferred (2026-04-19 row) | D-95 | Numeric ID D-85 reassigned per same block. | 2026-04-20 |
| D-86-orig-tenant | Cross-tenant isolation NO cross-client learning (2026-04-19 row) | D-96 | Numeric ID D-86 reassigned per same block. | 2026-04-20 |
| — | INTOOL merger narrative | Removed — verified as Gemini hallucination | No public record of any Polish industrial tools distributor named INTOOL. No M&A filings. Narrative removed from all grant/strategy planning documents. | 2026-04-19 |

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

## PRE-PILOT TECHNICAL DECISIONS (2026-04-17)

| # | Decision | Choice | Rationale | Date |
|---|---|---|---|---|
| D-75 | PDF adapter routing | Docling (TableFormer ACCURATE) for industrial catalogs; PyMuPDF retained for simple text PDFs | Standard PyMuPDF chunking splits table headers from values — causes hallucinations on parametric queries. Docling preserves table structure as Markdown. Pull-forward from Phase 2 triggered by HermesTools pilot (KOLVER/HAZET/CLECO catalogs with torque tables). | 2026-04-17 |
| D-76 | organization_id isolation timing | Implement NOW before Wojtek's first login | Avoids data migration later. bartek-playground and hermes-pilot get separate org_ids from day one. Half-day cost now vs. painful migration at 3+ clients. | 2026-04-17 |
| D-77 | Trial length | 14 days (not 7) | DR-9 confirms: 14 days is B2B SaaS standard in Poland. 7 days insufficient for low-digital-maturity sector — trial expires unused before user sees value. Onboarding must be active, not self-serve. | 2026-04-17 |
| D-78 | Bielik-11B | Research item for Phase 2 — NOT a current architecture decision | No hosted API exists. Self-hosting requires GPU (not available on Hetzner). Phase 1 stays on Claude Sonnet. Experiment: after 4 weeks of Wojtek pilot, run 50 real queries through Bielik-11B on RunPod vs Claude Sonnet. Switch if quality is comparable. 83% cost reduction at scale is significant. Speakleash team has large PL community reach — potential co-marketing if built on Bielik. | 2026-04-17 |
| D-79 | ColPali / Vision RAG | Research item for Phase 2 Sprint 2 — NOT now | ColPali is state-of-art for rasterized table retrieval (prevents 40% information loss vs OCR). Most HermesTools catalogs are native PDFs — Docling handles these. ColPali relevant when scanning reveals >20% of catalogs are scanned/rasterized. Assess after Wojtek uploads first batches. | 2026-04-17 |
| D-80 | HermesTools ERP angle | Long-term strategic position — not disclosed to Wojtek yet | HermesTools runs a 10-year-old custom ERP, nobody wants to touch it, new build stalled. Compilore sits alongside as intelligence layer now. If deeply integrated (live inventory overlay on search results), Compilore becomes de facto interface to their data — making old ERP even more isolated. Natural position for Phase 3. Do not mention this to Wojtek or his management at this stage. | 2026-04-17 |
| D-81 | Polish UI | Hard requirement for Phase 2 launch — not optional | DR-9 confirms: English-only UI = fatal adoption friction in tier-2/3 Polish cities. HermesTools is Bielsko-Biała. Wojtek is tech-savvy (exception), but his colleagues in technical dept are not. Full Polish UI from day one of Phase 2. | 2026-04-17 |
| D-82 | Biała Lista VAT | Bartek (Headframe Sp. z o.o.) must update bank account with US before first paying client | Polish SME CFOs verify all vendors on Biała Lista before signing. Missing bank account = vendor flagged as high-risk, procurement stalls. Action: send NIP-2 update to US with correct bank account. Timeline: 1-7 business days processing. Must complete before HermesTools company account proposal. | 2026-04-17 |
| D-83 | EU grants as GTM lever | Research item — grant-eligible client pathway per program-specific PKD rules. Program map and HermesTools fit codified in **D-85**; see §"EU Grants as GTM Lever" in 02_STRATEGY.md. | Grants can reduce client out-of-pocket by 50%, eliminating budget objection. Partner with grant writer (Channel 0, **D-84**) rather than writing applications in-house. Assess after first paying client is secured. | 2026-04-17 (updated 2026-04-20) |
| D-94 | HermesTools ERP angle — disclosure timing (supersedes D-80; IDs D-84–D-86 reassigned 2026-04-20) | Trigger-based disclosure: (1) During 8-week pilot — ERP angle remains private, Compilore positioned as advisor productivity tool. (2) If pilot metrics hit success gate (≥80% query citation accuracy + Wojtek recommendation to management) — disclose ERP intelligence layer angle to HermesTools management as part of regional RPO / business-transformation grant narrative (coordinate with POST-BEACHHEAD **D-85** EU pathways; Dig.IT is not pursued for HermesTools). (3) If pilot fails — keep ERP angle permanently private, no grant path pursued at HermesTools. | Reason: FE Śląskie 1.8-class narratives require "zasadnicza zmiana procesu biznesowego". Keeping ERP angle private AND claiming business transformation in grant creates internal contradiction. Decision: link disclosure to pilot outcome so narrative is authentic either way. Grant application without demonstrated pilot success has ~12% historical success rate — disclosure timing must match evidence. | 2026-04-19 |
| D-95 | Audit-deadline-driven positioning (deferred; was D-85 pre-2026-04-20) | Deferred decision. Core pilot positions Compilore as technical advisor productivity tool. POST-pilot, if three conditions all hold — (a) Wojtek pilot Week 3-4 audit-bundle test question resolves positively, (b) HermesTools management confirms calibration + OEM integration revenue dominant vs pure distribution, (c) HermesTools has real aerospace client footprint — then activate repositioning toward "audit-deadline compliance insurance" with premium pricing tier (3,500-8,000 PLN/mo) and `adapters/audit_compliance/` buildout. | DR-14 regulatory facts (IATF 7.5.3.2.1, VW Formel Q 15-year D/TLD, Stellantis 48h window) establish external non-discretionary deadline-driven demand pattern that matches Polish B2B deadline-buying behavior (DR-9). Not activated now because: (1) insufficient pilot signal yet, (2) risk of premature product scope expansion, (3) aerospace customer footprint unverified. See DR-14 RESULTS in 08_RESEARCH.md and 10_GRANTS.md Option D. | 2026-04-19 |
| D-96 | Cross-tenant data isolation — explicit NO cross-client learning (was D-86 pre-2026-04-20) | Hard architectural rule: Compilore does NOT build cross-tenant knowledge graphs, does NOT anonymize-and-share knowledge between `organization_id` boundaries, does NOT use one client's documents to improve responses for another client. | Polish Ustawa 2018 (trade secrets) + standard OEM Tier 1 supplier contracts prohibit "derivative use" of shared data even under anonymization. Enforcement: `organization_id` isolation already implemented (D-73); this decision promotes it from technical convenience to strategic commitment. Marketable feature: "Your data never trains models, never crosses tenant boundaries, never informs another customer's answers." See DR-14 RESULTS Trap #2 in 08_RESEARCH.md. | 2026-04-19 |
| D-97 | AI Act ICP — IT consultancies | Add Polish IT consultancies (10-100 person, building RAG/AI for clients) as second ICP alongside B2B distribution. Activation trigger: August 2026 enforcement deadline. Do NOT pivot primary beachhead — HermesTools/distribution pilot continues as planned. IT consultancy ICP = parallel track, first outreach Q3 2026 after pilot validates core product. | DR-15 confirms: Art. 25 Provider Trap creates genuine urgency, August 2026 deadline is hard, gap in Polish market confirmed, PARP Ścieżka SMART (Sekcja J/M) enables grant-subsidized sale. | 2026-04-22 |
| D-98 | Fine amount correction — remove €750k from all materials | Replace all instances of "€750,000 AI Act fine" with "up to €15M or 3% of global turnover" — the €750k cap applies exclusively to EU institutions (Art. 100), not private firms. | DR-15 Hallucination Guard: REFUTED. Using wrong number in pitch materials = credibility risk with any legally aware buyer. | 2026-04-22 |
| D-99 | Three-track AI Act revenue sequence | Launch order: Track C (Regulatory Intelligence API) first, Track B (content portal) parallel, Track A (Compilore compliance tier) after distribution validation. | DR-18 confirms KRiBSI enforcement probability against SMEs is 10%. Direct fear-of-fine is not the primary trigger. Enterprise downstream pressure is. API feed can generate revenue in 4-6 weeks without 90-180 day sales cycle. Content portal builds authority for Track A. | 2026-04-22 |
| D-100 | Regulatory Intelligence API as adjacent product | Build Polish AI Act regulatory intelligence feed (machine-readable, structured, EUR-Lex + KRiBSI + UODO) for sale to international GRC platforms and enterprise law firms. Target price: $1,000-3,000 USD/msc. Build using existing n8n + Firecrawl infrastructure. | Clausematch and Archer precedent confirmed. Near-zero marginal cost. No Polish competitor identified. Does not require enforcement to materialize — GRC platforms need Polish coverage regardless. | 2026-04-22 |

---

## POST-BEACHHEAD STRATEGY DECISIONS (2026-04-20)

Context: Following analysis of two external deep research reports 
(Polish SME KM buying triggers; Global AI KM competitive landscape) 
and grant-program PKD verification. Multi-turn strategy session led 
to the following codifications.

*Renumbering (2026-04-20): former PRE-PILOT **D-84** (ERP disclosure), **D-85** (audit deferral), **D-86** (cross-tenant isolation) moved to **D-94–D-96** (see SUPERSEDED table) so this post-report block can use **D-84–D-88** as originally drafted.*

| # | Decision | Choice | Rationale | Date |
|---|---|---|---|---|
| D-84 | Grant writer partnership channel | Formalize Channel 0: non-exclusive partnerships with Polish grant consulting firms. Referral fee: 5% recurring revenue share, first 24 months per referred client. No territorial exclusivity. No upfront cash. First 5 outreach: Strategor, Grants.Capital, All-Grants, DotacjeDlaKażdego, Najda Consulting. | Grant writers already hold MŚP trust relationships; operate on success-fee (zero client upfront cost); need AI/digitization projects to increase grant value. Compilore for them = higher success fees + competitive differentiation. For Compilore = pre-qualified leads with 50% budget already covered. Model mirrors standard grant-consulting industry economics. 5% recurring (vs one-time cut) aligns incentives: partner is motivated to refer clients who STAY, not just close. | 2026-04-20 |
| D-85 | EU grant pathways — program correction (2026-04-20) | **Ścieżka SMART:** rejected as client path (B+R + 3M PLN minimum; wrong fit). **Dig.IT:** production MŚP (Sekcja C) only — HermesTools disqualified (PKD 47.99.Z, Sekcja G); secondary PKDs 28.29.Z / 33.20.Z do not override main PKD in ARP assessment. **Do NOT pursue Dig.IT for HermesTools.** **Regional RPO** (e.g. FE Śląskie 1.3): primary path for distributors / Sekcja G. Navigate programs via grant writer Channel 0 (**D-84**). | Consolidates PKD verification and removes incorrect DR-11 assumptions. Avoids 3-month rejection cycle on mis-matched Dig.IT applications; energy better spent on RPO + partner-led routing. | 2026-04-20 |
| D-86 | Medical/Chemical verticals — deferred without design partner | Medical Devices and Chemical/Food Ingredients adapters NOT built until (a) design partner from that vertical is secured AND (b) Compilore has 3+ paying clients in primary beachhead. Regulatory tailwinds (MDR 2026-2028, CLP Nov 2026) acknowledged but not actionable without insider champion. POLMED membership rejected (budget constraint). Acqui-hire rejected (equity constraint). | Without a design partner, adapters built from regulatory specs alone produce unusable output. Cold outreach to regulatory affairs specialists has unknown response rate in Polish medical/chemical. Sales cycle in these sectors is 6-12 months (vs 3-4 for HVAC). Attempting these verticals pre-HermesTools proof = resource dilution. Parking. | 2026-04-20 |
| D-87 | Sales narrative hierarchy | Primary pitch = time-savings (35% advisor time = €1,000+/mo drain = 5x ROI). Secondary amplifier = institutional knowledge succession risk (56% of Polish SMEs rank retention as #1 challenge per external research). Do NOT lead with succession narrative — it is hypothetical and loses to quantified time-savings for risk-averse Polish SME owner. Deploy succession only in specific scenarios: owner-near-retirement, post-departure wounded prospects, second-call CFO conversations. | Analysis 2026-04-20: while external report (Raport 1) ranks "key person leaving" as trigger #1 frequency, methodology is not disclosed (academic papers mix macro trend with buying trigger). Quantified time-savings is falsifiable in 30 seconds by buyer; succession is hypothetical scenario. For risk-averse Polish SME, concrete beats abstract. Succession narrative remains useful as amplifier, not lead. | 2026-04-20 |
| D-88 | BUR registration as permanent infrastructure play | After HermesTools pilot validation, register Headframe Sp. z o.o. as service provider in Baza Usług Rozwojowych (BUR). Not a grant per se — positions Compilore onboarding + training as qualified for KFS (Krajowy Fundusz Szkoleniowy) refund for any future client, any PKD. One-time registration cost; trailing benefit. | BUR works across PKD restrictions. Training refund (50-80% by voivodeship) covers onboarding, not software license — but reduces net client cost of full implementation package (license + training + deployment). Channel-independent permanent infrastructure. | 2026-04-20 |

---

## STRATEGIC ADDITIONS (2026-04-29)

| # | Decision | Choice | Rationale | Date |
|---|---|---|---|---|
| D-98 | Long-term synthesis ambition | Compilore Phase 3 = synthesis layer for SME, vertical-specific, not horizontal platform | Hyperspell/Glean target enterprise with horizontal synthesis. Compilore's advantage is vertical depth: known source types, known conflict patterns, hardcoded authority hierarchy for technical B2B distribution. Synthesis only after Phase 2 live ingest validated in production. Horizontal synthesis explicitly rejected - cannot compete with Glean/Notion AI on resources. | 2026-04-29 |
