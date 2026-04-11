# 04 — DECISIONS
## Compilore: Decision Log

**Format:** Every significant decision is logged here with rationale and date.
When a decision is reversed, the old entry is marked SUPERSEDED and a new entry added.
This file answers "why did we do it this way?" forever.

**Last updated:** 2026-04-11

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
| D-33 | Presentation output format | Marp → PPTX (not Slidev) | Slidev requires Vue syntax — high LLM hallucination risk. Marp: pure Markdown with --- separators → PPTX/PDF. Export fidelity critical for enterprise use. | 2026-04-11 |
| D-34 | Lint contradiction check architecture | Gated 3-pass: Detect → Plan → Implement (HITL between each) | Single-pass prompts produce hallucinated contradictions. 3-pass: pass 1 lists conflicts, pass 2 proposes merges, pass 3 only after human approval. Reduces context bloat. | 2026-04-11 |
| D-35 | Format selection UX | Proactive suggestion chips + natural language (hybrid) | Rule-based heuristics evaluate answer shape after synthesis → suggest 1-2 relevant formats as clickable chips. User can also type format intent in natural language. Heuristics: ≥3 entities with parallel attributes → comparison_table; ≥4 wiki_pages of different types → mindmap; ≥3 sequential steps → protocol; single long content → card. Rule-based = $0, zero latency. LLM-based format evaluation deferred to Phase 2 when usage data exists. | 2026-04-11 |
| D-36 | Mind map renderer | Markmap (not Mermaid, not D3.js) | LLM outputs standard nested Markdown. Markmap renders as SVG. ~30 token cost, zero hallucination risk, zero extra LLM call. D3.js rejected: coordinate state persistence is unsolved engineering problem for dynamic AI-generated nodes. | 2026-04-11 |
| D-37 | Phase 2 UI paradigm | Wiki Graph Browser (not chat UI) | Spatial epistemology model (Heptabase). Concept pages as nodes, [[wikilinks]] as edges. Compounding must be visually explicit — this is Compilore's core differentiator vs RAG. | 2026-04-11 |
| D-38 | Response card design | F-pattern + atomic interactivity + delta-first | Cognitive load research: users scan F-pattern, atomic cards require no navigation, delta (change over time) is more actionable than raw scores. Every response card: conclusion headline, source chips, confidence delta, Save-to-Wiki toggle in-card. | 2026-04-11 |

---

## DEFERRED — Decisions Explicitly Not Made Yet

These are real questions, but not yet time to answer them:

| Topic | Why Deferred | When to Decide |
|---|---|---|
| Frontend UI design (Phase 2) | Depends on Phase 1 learnings | Phase 2 Sprint 0 |
| Payment integration | After first paying client | Phase 2 |
| Output formats: presentations, infographics | Validate basic query loop first | Sprint 4 |
| Mobile UX (PWA vs native) | Validate on desktop first | Sprint 4 |
| Phase 2 Go/No-Go | Decision gate at Sprint 4 | End of Sprint 4 |
| Public MPZP knowledge pool (data moat) | Phase 3 feature | Post-PMF |
| Fine-tuning on compiled Wiki data | Post-PMF | Post-PMF |
| Multiple industry adapters beyond architect | Phase 3+ | Post-PMF |
| Voice interface | Phase 4 | — |
| 385-document statistical validation | Phase 2 production | Phase 2 |
| Proactivity / push notifications | Phase 3 | — |

---

## SUPERSEDED — Changed Decisions

| # | Original decision | What replaced it | Why | Date changed |
|---|---|---|---|---|
| D-02-orig | Phase 1 interface = Viktor/Slack | Web UI (localhost → Hetzner) | Web UI built and working in Phase 1. Slack adds complexity without benefit for playground phase. | 2026-04-11 |
