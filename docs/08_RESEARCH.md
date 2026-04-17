# 08 — RESEARCH
## Compilore: Deep Research Findings & Implications

**This is a living document.** Each Deep Research session adds a new dated section.
Findings here directly inform decisions logged in 04_DECISIONS.md.

**Last updated:** 2026-04-17

---

## DR-1: GTM & Polish Architect Market (2026-04-09)

**Source:** Deep Research report on go-to-market strategy for Polish architectural firms.

### Confirmed (aligns with brief)
- Biura rachunkowe as distribution channel: confirmed independently. Revenue share 20%
  recurring. Pitch: "Zdrowy klient zostaje klientem dłużej."
- Zero competition in text-based legal analysis for architects.
- Pricing 200–600 PLN/mo confirmed as safe discretionary range.
- Fakturownia + P24 over Stripe: strongly confirmed. Polish B2B prefers bank transfer/BLIK.

### New Findings (not in original brief)

**Geoportal framing:** Geoportal-krajowy.pl is the #1 tool used by Polish architects.
Compilore should be positioned as: "Geoportal gives you the raw map. Compilore gives
you the legal analysis layer on top." This framing reduces explanation time and anchors
on a tool architects already trust.

**Shadow testing behavior:** Architects test new tools by running finished, known projects
through them to verify accuracy. One wrong answer = tool discarded permanently. This
makes citation trails a hard requirement for conversion, not a UX nicety. Every Compilore
answer must link to the source document + page/paragraph.

**Plan Ogólny reform (2026):** Poland's planning reform (replacing Studium with Plan Ogólny)
is creating active confusion. Architects who just received permit rejections due to the new
system are "active wounded" — highest conversion probability. This is a timing window.
Content and outreach should target this context now.

**DPA as feature:** Architects are professionally trained to protect client confidentiality.
Present the DPA/RODO compliance from first contact — it is a conversion lever, not a
legal checkbox.

**Concierge test for Phase 2 validation:** Instead of building Phase 2 immediately,
validate with a fake door: landing page + manual MPZP analysis by Bartek. Verify quality
and willingness to pay before writing a line of Docling code. This becomes Phase 2 Sprint 0.

### Implications for Architecture
- Add `adapters/architect/plan_ogolny_adapter.py` as distinct from `mpzp_parser.py`
  (different document structure from the reform)
- Add Citability as 4th Gatekeeper criterion for Phase 2 (verifiable source link to PDF page)

---

## DR-2: Gemini Analysis of Architecture (2026-04-09)

**Source:** Gemini's technical review of the original brief.

### Confirmed
- Docling OOM on 8GB Hetzner: confirmed risk, mitigations in brief are correct
  (OMP_NUM_THREADS=1, page-by-page, gc.collect())

### New Findings

**git_commit_hash in frontmatter:** Each `wiki_page` should store the `git_commit_hash`
of its last compilation in frontmatter. This enables rollback without new infrastructure:
`git checkout <hash> -- wiki/concepts/page.md` + re-embed. Agent does not resolve merge
conflicts — human receives Slack diff and decides (HITL). → Added to D-14.

**Gatekeeper pre-check for novelty:** The Gatekeeper evaluates novelty but had no
mechanism to actually check existing content. Fix: run `hybrid_search` with the answer
as query BEFORE novelty evaluation. If cosine similarity > 0.85 with existing page,
Gatekeeper receives "this knowledge already exists at [[X]]" and can refuse to save.
Cost: one extra embedding call (~$0.001). → Added to D-16.

**Gatekeeper blind spot at 3,000+ pages:** Without the pre-check above, at scale the
Gatekeeper will start creating duplicate output pages for questions that have been asked
before in different phrasings. The pre-check solves this.

**Gemini's suggestion (rejected):** `previous_version_cid` in Supabase for rollback.
Rejected: redundant with git_commit_hash in frontmatter. We already have Git.

**Public MPZP data moat (noted, deferred):** Multi-tenant architecture with optional
anonymous pool for public MPZP documents could create network effect. Public MPZPs
are public domain (RODO does not restrict). Noted as Phase 3 feature.

---

## DR-3: Multimodal Ingestion Pipeline (2026-04-11)

**Source:** Deep Research report — "Architectural Blueprint for a Multimodal,
GDPR-Compliant Knowledge Base Ingestion Pipeline"

### Extraction Tools

**Firecrawl vs trafilatura:**
Firecrawl (AGPL-3.0, self-hostable) natively handles JS rendering, recursive sitemap
discovery, and dynamic pagination. Outputs clean Markdown. Charges 1 credit/scrape;
100K pages for $83/mo via API, or $0 self-hosted. 4-5x cheaper than Jina Reader at scale.
Current trafilatura is fine for Phase 1. Upgrade to self-hosted Firecrawl at Phase 2
if signal/noise issues arise. → D-29.

**Kreuzberg for async PDF:**
Kreuzberg provides native async/await for PDF extraction with anyio worker pool offload.
Current PyMuPDF is synchronous — blocks FastAPI event loop on large PDFs. Not a problem
at Phase 1 volume. Replace at Phase 2 when MPZP processing is added. → D-21 (updated).

**GitHub via raw API:**
`raw.githubusercontent.com/{owner}/{repo}/main/README.md` = pure Markdown, zero noise,
zero auth required for public repos. Authenticated GitHub API = 5,000 req/hour.
Better than any scraping approach. → D (new adapter).

### Social Media

**SociaVault as unified social API:**
SociaVault provides dedicated REST endpoints for Instagram transcripts and Twitter/X threads.

Instagram: 1 credit = 1 transcript regardless of length. Growth pack $79/20K credits =
$0.004/transcript. 80x cheaper than GetTranscribe ($0.10–0.50/min). More reliable than
Apify (headless actors break when Meta updates DOM).

Twitter/X: Official API $100–5,000/mo. Apify fails on virtualized DOM lists >50 tweets.
SociaVault $29/6,000 credits, REST endpoint, automated proxy rotation.

No native n8n node for SociaVault but standard HTTP Request node with `x-api-key` header
is trivial. → D-22, D-23.

**TikTok JSON hydration:**
TikTok SPAs ship structured data in `<script id="__NEXT_DATA__">` tags. Parse with
BeautifulSoup → extract JSON dictionary → no browser required. Official TikTok Research
API is academic-only. → D (adapter approach).

**Substack paywalled:**
Two-step: Hidden JSON API to discover posts + cookie injection (`substack.sid` +
`substack.lli`) for paywalled full content. `scrape-substack` library handles both.
STRICT: own paid subscriptions only, private PKB use only, never redistribute. → D-27.

**Hacker News — Algolia, not Firebase:**
Firebase API: N+1 problem — 500 comments = 500 HTTP requests. Algolia HN API: single
GET, up to 1,000 items, nested hierarchy preserved. Hierarchy preservation critical:
LLM must understand parent/child comment relationships to synthesize debates properly.
Algolia is free, no API key required. → D-26.

### Audio & Transcription

**Faster-Whisper Large-v3 for Polish:**
Self-hosted Faster-Whisper (CTranslate2 engine) = 4x faster than original Whisper.
Large-v3 specifically handles:
- Polish diacritics (ą, ę, ł, ń, ó, ś, ź, ż) accurately
- PL/EN code-switching without breaking (Polish conversation + English technical terms)
Deployed on Hetzner = GDPR compliant (audio never leaves EU). $0/minute.
Deepgram Nova-3: $0.0043/min but "struggles" with similar languages/accents.
AssemblyAI: $0.21/hr, better multilingual but still less accurate than local Large-v3. → D-25.

NVIDIA Parakeet TDT 0.6B V3 (ONNX): achieves 30x real-time speed on CPU — useful if
GPU not available on Hetzner. Lower quality than Large-v3 but viable fallback.

**Spotify — no legitimate path:**
Spotify auto-generates transcripts (visible in UI) but exposes zero API endpoints for them.
Web API only returns show/episode metadata, duration, descriptions — never VTT/SRT.
Solution: locate podcast RSS feed (most non-exclusives have one) → download MP3 → local
Faster-Whisper. Spotify exclusives = impossible. Workaround: if podcast also on YouTube
→ YouTube adapter (most wellness podcasts are on both). → D-24.

### GDPR / Infrastructure

**PII scrubbing mandatory:**
Social media data inevitably contains PII. Must be scrubbed in memory BEFORE any
persistence to Supabase. n8n Code node with regex + optional local LLM. This is not
optional compliance — it is infrastructure. Supabase with unscrubbed PII triggers
GDPR subject access requests + right-to-be-forgotten mandates.

**n8n self-hosted = critical:**
Cloud n8n: €24/mo for 2,500 executions, up to €800/mo for enterprise.
Self-hosted: unlimited executions, only compute cost. Already running on GapRoll VPS.

---

## DR-4: Gemma 4 vs Claude Sonnet for Knowledge Compilation (2026-04-11)

**Source:** Deep Research report — "System Architecture and Performance Analysis:
Gemma 4 vs. Claude 3.7 Sonnet for Autonomous Knowledge Compilation"

### The Gemma 4 Family (Released April 2026)

Google released Gemma 4 in the first week of April 2026 under Apache 2.0 license
(full commercial use, no restrictions).

Four variants: E2B, E4B (edge/mobile), 26B A4B (MoE), 31B Dense.
All variants: multimodal (image input), 128K context (edge) or 256K (large models).

### 31B Dense vs 26B A4B MoE — Critical Distinction for Compilore

**31B Dense architecture:**
- 30.7B parameters, 60 layers
- Hybrid attention: alternates local sliding-window (512-1024 tokens) + full global attention
- Dual RoPE: standard RoPE for sliding, proportional RoPE for global layers
- Maintains entity relationships across 256K context without "lost in the middle"
- Dense = all 30B parameters active on every token

**26B A4B MoE architecture:**
- 25.2B total, but only 3.8B active per token (128 experts, 8 active + 1 shared)
- Fast but sparse routing loses track of syntactical boundaries during structured output
- Systematically produces malformed YAML/JSON: trailing garbage tokens, invalid escape
  sequences, broken schema
- Disabling thinking mode = model ignores formatting, outputs plain prose
- Enabling thinking mode = garbage tokens break parsers
- No winning configuration for structured output tasks

**Verdict for Compilore:** Use 31B Dense. Avoid 26B A4B for any loop that requires
structured output (compile, gatekeeper). → D-30.

### Benchmarks

| Metric | Gemma 4 31B Dense | Gemma 4 26B A4B MoE | Claude 3.7 Sonnet |
|---|---|---|---|
| IFBench (thinking mode) | **78.7%** | ~73% | 74.7% |
| IFBench (standard mode) | 73.5% | — | 73.8% |
| OmniDocBench (edit distance, lower=better) | **0.131** | 0.149 | N/A |
| Agentic simulation survival | **100%** | 60% | High |
| MMLU Pro | 85.2% | — | — |
| GPQA Diamond | 84.3% | — | — |
| Arena AI rank (open models) | **#3** | #6 | — |

31B Dense beats Sonnet on IFBench (78.7% vs 74.7%) and shows 100% reliability in
complex agentic simulations. 26B MoE at 60% survival = unacceptable for Compilore.

### Thinking Mode

For 31B Dense: thinking mode is a net positive. Model "calculates" cross-links between
documents in latent space before writing output. Uses `<|"|>` delimiter tokens to protect
string values in YAML from corruption.

For 26B MoE: thinking mode exacerbates broken schema. 3.8B active parameters insufficient
to simultaneously maintain reasoning state AND adhere to rigid formatting.

Multi-turn management: strip raw thoughts from conversation history between turns to
prevent context degradation. Exception: thoughts immediately before tool call / JSON
output MUST remain — model relies on this immediate reasoning state.

### Hardware — M4 Pro 24GB (Developer Machine)

**Actual hardware:** MacBook Pro 14", November 2024, Apple M4 Pro, 24GB RAM, macOS Sequoia

The DR-4 research was calibrated for M3 Max (36GB/96GB). Updated figures for M4 Pro 24GB:

| Variant | Quant | RAM needed | System overhead | Free buffer | Inference speed | Verdict |
|---|---|---|---|---|---|---|
| 27B Dense | Q4_K_M | ~16-17GB | ~4GB | ~3-4GB | ~12-18 t/s | ✅ Fits — monitor swap at 128K+ ctx |
| 12B Dense | Q4_K_M | ~8GB | ~4GB | ~12GB | ~25-35 t/s | ✅ Comfortable — recommended start |
| 31B Dense | Q4_K_M | ~17-20GB | ~4GB | 0-3GB | ~10-15 t/s | ⚠️ Too tight — avoid on 24GB |

**Note on 31B Dense:** The DR-4 recommendation of 31B Dense was for M3 Max 36GB+.
On 24GB M4 Pro, 31B Dense leaves insufficient buffer and risks OOM under load.
Use 27B Dense (same architecture family, fits safely) or 12B for comfort.

**M4 Pro vs M3 Max — relevant differences:**
- M4 Pro: higher per-core performance (+15-20% vs M3 Pro), comparable to M3 Max per-core
- M4 Pro 14": smaller thermal envelope → throttles faster under sustained inference load
- 24GB unified memory: sufficient for 27B Q4_K_M with care; 31B = too risky

**Thermal throttling (14" chassis):**
Under sustained load (10+ sequential queries), M4 Pro 14" throttles.
Inference speed drops from ~15 t/s to ~8-10 t/s after ~5-10 minutes of continuous use.
For personal playground use (queries spaced out) — not a practical problem.
For batch operations (linting with many contradiction checks) — use API, not local.

**Recommended config for Sprint 5:**
Start: `gemma4:12b-q4_k_m` — validate quality, zero RAM pressure
Upgrade path: `gemma4:27b-q4_k_m` — if 12B quality insufficient for synthesis

**Why not Q4_K_M for MoE:** MoE requires iMatrix quantization (IQ4_XS/IQ4_NL) to avoid
"lobotomizing" sparse expert routing weights. But iMatrix has poor Metal backend
optimization = slower inference AND still broken schema output. No benefit.

### Cost Comparison (M4 Pro 24GB)

| Config | Monthly cost (50 docs, 200 queries) |
|---|---|
| All API (current) | ~$10-14 |
| Hybrid: Compile=Sonnet, Query+Gate=local 12B | ~$0.50 |
| Hybrid: Compile=Sonnet, Query+Gate=local 27B | ~$0.50 |
| Fully local (12B compile — not recommended) | ~$0.05 |

Savings vs all-API: ~$10-13/month. Meaningful at personal scale; significant at Phase 2 client scale.

### Compile Stays on Sonnet

Despite Gemma 4 31B scoring slightly higher on IFBench, Sonnet remains for compile because:
1. Compile is one-time — quality is permanent in the Wiki
2. Current compile cost is acceptable: ~$0.07/doc at article volume
3. Sonnet has 200K context vs Gemma 4 31B's 256K — both sufficient for Phase 1
4. Risk of switching: any quality regression in compile output is costly to detect and correct
5. Revisit at Phase 2 scale when compile costs increase significantly

---

## Open Research Questions

Questions not yet answered — candidates for future Deep Research:

1. **Gemma 4 31B structured output quality vs Sonnet in practice:**
   Benchmarks say 31B > Sonnet on IFBench. But for Compilore's specific task
   (YAML frontmatter + interconnected Markdown pages from articles), how does
   actual output quality compare in blind evaluation?

2. **Response cards & visual output UX research:**
   What output formats (cards, mind maps, timelines, comparison tables) actually
   drive engagement in knowledge tools vs what users say they want?
   Notion AI, Perplexity, ChatGPT data.

3. **PKM tool retention drivers:**
   What makes Notion, Obsidian, Mem users retain vs churn?
   "Blank slate" problem: how do these tools onboard when the knowledge base is empty?

4. **Polish-language embedding quality:**
   text-embedding-3-small for Polish — any documented accuracy issues for semantic
   search in Polish? Is there a better multilingual embedding model at similar cost?

---

## DR-5: AI Output Formats, Cognitive Load & UX Design (2026-04-11)

**Source:** "The Architecture of AI-Generated Knowledge: Output Formats, Cognitive Load,
and System Design in 2026" — comprehensive report on knowledge compiler UX.

### Stated vs Revealed Preferences — Critical for Product Design

Users claim they want speed (stated preference). Behavioral data shows the actual
driver is avoiding compositional effort — the cognitive tax of structuring, linking,
and formatting information (revealed preference). Systems optimized for revealed
preferences achieve 61.3% satisfaction accuracy vs 57.7% for stated.

**Implication for Compilore:** Never sacrifice output structure for latency.
A well-structured response card with citations takes 3s longer and is worth it.
The compounding Wiki IS the revealed preference fulfillment — users won't articulate
this but it's why they'll stay.

### Response Card Architecture (F-Pattern + Atomic Interactivity)

Eye-tracking research confirms F-Pattern scanning. Users read the first words of
each line; the right side of cards is largely ignored. Key principles:

1. **Lead with conclusion** — not "Answer to your question" but the actual insight
2. **Delta over raw data** — "↑ confidence 0.70→0.85 after new document" not just "0.85"
3. **Source chips in-card** — not in a separate section below
4. **Atomic interactivity** — "Save to Wiki" toggle in the same card, not a separate action
5. **Progressive disclosure** — secondary data hidden until hover/click

### Diagram Generation — Mermaid + Markmap Architecture

LLM affinity by token cost: Markmap (~30 tokens) > Mermaid (~50) > PlantUML (~80) >>
Excalidraw (~500) >> draw.io (~1200).

Two distinct use cases:
- **Markmap** → `/mindmap` output: LLM generates nested Markdown headings.
  Markmap renders as SVG mind map. Zero extra logic. $0 extra cost.
- **Mermaid** → `/graph` output: relationship maps between Wiki pages, entity
  connections, concept hierarchies. Native to LLM training data.

Avoid D3.js for AI-generated diagrams — coordinate state persistence is a complex
engineering problem when LLM generates dynamic node sets.

### Presentation Output — Marp, Not Slidev

Slidev requires Vue component syntax → high hallucination risk in LLM output.
Marp: pure Markdown with `---` slide separators → compiles to PPTX/PDF.
Export fidelity is critical: beautiful HTML that breaks on export creates MORE work.

Decision: `/deck` output format = Marp → PPTX. LLM generates standard Markdown.
Marp handles compilation. Architects get editable PowerPoint. → D-39.

### Gated Execution for Lint Loop

Protocol: `<PROTOCOL:EXPLAIN>` → `<PROTOCOL:PLAN>` → `<PROTOCOL:IMPLEMENT>`
Applied to contradiction_checker.py:
- Pass 1: List all pages with potential conflicts (no resolving, just detection)
- Pass 2: For each conflict pair — show contradiction, propose merge strategy
- Pass 3: Only after human approval (HITL interrupt_before already in lint_graph.py)

Reduces context bloat in lint_contradiction.md prompt. Eliminates hallucinated
contradictions from single-pass prompts. → D-40.

### Phase 2 UI Vision — Wiki Graph Browser (Not Another Chat UI)

Heptabase model: knowledge as spatial canvas. Cards on whiteboards. Edges between nodes.

Compilore Phase 2 Next.js UI should NOT be a chat interface with a sidebar.
It should be a **Wiki Graph Browser** — concept pages as cards, [[wikilink]]
relationships as visible edges, knowledge growth visualized over time.
The compounding must be visible — this is the core differentiator.
Users need to see the Wiki growing to understand why Compilore is different from RAG.

### Format Selection UX (Hybrid — Gamma + Proactive Chips)

Avoid static UI dropdowns as the primary control. Two paths (see **D-41**):
1. **Natural language in query** — "show this as a mind map", "make a comparison table",
   "prepare slides from this" → `query_graph.py` / synthesizer parses `output_format` intent.
2. **Proactive suggestion chips** — rule-based `format_evaluator.py` inspects answer metadata
   after synthesis and offers 1–2 relevant formats as one-click chips (zero LLM cost).

LLM-based format evaluation deferred to Phase 2 when `wiki_log` chip-click data exists.

### Open Research Questions (Updated)

5. **Phase 2 UI — Wiki Graph Browser feasibility:**
   What JS library for knowledge graph visualization? vis.js vs Cytoscape.js vs
   react-force-graph? Performance at 500+ nodes? Integration with Next.js 15?

6. **Marp PPTX fidelity in practice:**
   Does Marp PPTX export maintain Polish character encoding (ą, ę, ł)?
   Does it handle long Polish regulatory text without overflow?

7. **Markmap in Next.js:**
   What is the cleanest integration of Markmap renderer in a Next.js 15 app?
   SSR implications?

---

## DR-8: Audio Output & Presentation Templates Research (2026-04-13)

### Podcastfy — Analysis and Rejection as Dependency

**Repo:** github.com/souzatharsis/podcastfy — Apache 2.0, pip installable.
**Latest version:** 0.4.1 (Dec 2025). Active but slowing — burst in Oct-Nov 2024.

**Architecture (2 steps):**
1. Transcript generation — any LLM (OpenAI, Anthropic, Google, local via Ollama)
2. TTS synthesis — OpenAI, Google, ElevenLabs, Microsoft Edge TTS

**Why rejected as a library dependency:**
- Optimized for dialogue (2-speaker), not monologue summary — single-speaker is secondary
- Single primary maintainer = abandonment risk for a production dependency
- Author admits OpenAI TTS output "does not sound that exceptionally great"
- ElevenLabs required for quality improvement — rejected on cost grounds
- Compilore already owns ingest + synthesis pipeline; Podcastfy duplicates it
- Adding Podcastfy = 100-150 lines of wrapper around what we can do in 100-150 lines natively

**Decision: build `audio_summary.py` natively → D-50**

### Audio Summary Implementation Plan

```python
# audio_summary.py — ~120 lines, no new dependencies
# Input: synthesizer output (already exists in query_graph.py)
# Step 1: Sonnet prompt → spoken-word transcript (no bullet points, no headers,
#         natural connective tissue between ideas, Polish or EN)
# Step 2: openai.audio.speech.create(model="tts-1", voice="onyx", input=transcript)
# Output: MP3 file + playback URL in QueryResponseCard
```

**Cost model:**
- Transcript generation (Sonnet): ~$0.01 per summary (same as query synthesis)
- TTS (OpenAI tts-1 standard): $15/1M chars ≈ $0.15 per 10K-char summary
- Monthly estimate at 50 summaries: ~$8 total
- TTS HD ($30/1M): double cost, marginal quality gain for briefings — use standard

**TTS provider comparison (single-speaker, Polish support):**
| Provider | Cost/1M chars | Polish quality | Notes |
|---|---|---|---|
| OpenAI tts-1 | $15 | Good | Recommended |
| OpenAI tts-1-hd | $30 | Good | Overkill for briefings |
| Google Neural | ~$16 | Good | Comparable, more setup |
| Microsoft Edge TTS | Free (unofficial API) | Mediocre on PL | No SLA, brittle |
| ElevenLabs | ~$180 | Excellent | Rejected — cost |

### Presentation Templates — McKinsey vs Accenture Design Philosophy

**McKinsey style:**
- Pyramid Principle: conclusion first, evidence below
- Action titles: full sentence stating the insight (not "Market Analysis" but "Market shrinks 12% YoY — repositioning required")
- One claim per slide, MECE structure
- Colors: white + navy blue, sparse accent
- Fonts: Georgia (headlines) + Arial (body)
- Data-heavy, chart-forward

**Accenture style:**
- Dark background (deep navy / near-black)
- Large iconography, more whitespace, infographic aesthetic
- "Insight box" — single highlighted takeaway in bottom-right corner
- Brand accent: purple (#A100FF), not blue
- More visual, less text-dense than McKinsey

**Six-template system for Compilore `/deck` → D-51:**

| Template ID | Use case | Core structure |
|---|---|---|
| `executive_brief` | Board / fast decision | SCQA + 1 recommendation slide |
| `data_story` | Results presentation, analysis | Context → Trend → Implication → So What |
| `status_update` | Project update | Status → Risks → Next Steps (RAG indicator) |
| `comparison` | Options / vendor selection | 2-3 column comparison → recommendation |
| `process_flow` | How something works | Swimlane or numbered step-by-step |
| `executive_summary` | Report distillation | 3-5 bullets + key metric + So What |

**LLM template selection:** intent parser detects query type → selects template → passes to Marp prompt. User can override via chip ("change to data_story"). Zero extra LLM call for selection (rule-based, same as format_evaluator.py pattern).

### Open Research Questions (Updated)

8. **Marp multi-template implementation:** How to cleanly implement 6 Marp templates as prompt variants? Single `format_deck.md` with conditional sections vs 6 separate prompt files?

9. **OpenAI TTS Polish quality in practice:** Does `tts-1` handle Polish diacritics correctly? Does it produce natural prosody for Polish regulatory terminology (MPZP, WZ, OUZ)?

---

## DR-6: Analiza Biznesowa GIS Engine — Dane Rynkowe (2026-04-12)

### Dane finansowe konkurencji (KRS)

- **OnGeo.pl** (lider raportów o terenie): przychód 2024 = 1.3M PLN, spadek 47% r/r, strata netto -177k PLN. Model transakcyjny (tanie raporty per-query) = udowodniony ślepy zaułek na polskim rynku.
- **Model B2B Enterprise subskrypcja** jest jedyną viable ścieżką. Precedens: **inFakt** (compliance podatkowy) → przejęty przez Visma przy wzroście 73.8% r/r. Identyczny model: deterministyczna automatyzacja chaotycznego polskiego prawa.

### Struktura kosztów biur architektonicznych

- **Revit:** 11,825 PLN netto/rok/stanowisko (do 35,480 PLN/3 lata)
- **ArchiCAD:** 854–1,465 PLN/msc/stanowisko
- **Małe biuro 5 osób:** 50,000–70,000 PLN/rok tylko na CAD
- **Implikacja:** subskrypcja 500–900 PLN/msc = „kolejna licencja”, nie osobna decyzja budżetowa. Ale musi mieć twardy ROI.

### Benchmarki cenowe globalne

- **Gridics** (USA, zoning analysis): $999/Property Zoning Report, $1,499/Development Feasibility Report, API $0.49–0.69/call
- **Harvey AI:** $100M ARR w 3 lata, 92% adopcji w licencjach
- **Spacemaker:** exit $240M do Autodesk. GTM: sprzedaż ROI bezpośrednio do deweloperów (nie architektów). +16% gęstość = miliony EUR dodatkowego zysku.

### TAM/SAM (bottom-up, konserwatywne)

- Deweloperzy MŚP ~4,000 × 12,000 PLN/rok = **48M PLN**
- Biura architektoniczne ~8,000 × 4,000 PLN/rok = **32M PLN**
- Eksperci ~5,000 × 2,000 PLN/rok = **10M PLN**
- **TAM łącznie:** ~90M PLN (~22.5M USD)
- Realistyczny SAM lata 1–2: ~5–10% TAM = **4.5–9M PLN**
- Sufit $100M ARR wymaga ekspansji EU (Niemcy XPlanung, Czechy, Rumunia) lub pivot do Transaction+Generative Design

### Scenariusze exit

- **$2M ARR** → wycena $10–16M USD (5–8x multiple, CEE PropTech)
- **$5M ARR** → wycena $25–40M USD
- **Potencjalni kupcy:** Visma, Autodesk, CoStar, Otodom/OLX, wetransform (XPlanung), Esri

### GTM — Harvey Playbook (kopiuj dosłownie)

- NIE skaluj do 8,000 biur architektonicznych na starcie
- Partnership z 1–2 największymi deweloperami jako co-builders
- „Zero training on customer data” jako feature, nie checkbox
- Metryki: X analiz chłonności/msc zamiast X tygodni pracy
- **Spacemaker lesson:** pitch do CFO/CEO przez PLN zysku z PUM, nie przez oszczędność czasu asystenta

### Ryzyka niezaadresowane przez raport

- **Licencja zawodowa:** GIS Engine musi być „narzędzie informacyjne”, NIE „opinia urbanistyczna” (wymaga uprawnień). Każda odpowiedź: disclaimer + „Pokaż Źródło” GML record.
- **EGiB quality fallback:** OpenStreetMap + ortofotomapa jako krzyżowa weryfikacja dla powiatów ze słabymi danymi EGiB
- **Okno konkurencyjne:** OnGeo jest finansowo słaby ale może dodać OUZ feature. Buduj brand i pierwsze case studies przed sierpniem 2026.

---

## DR-7: GIS Spatial Engine — Pełna Analiza Biznesowa (2026-04-12)

### Walidacja hipotezy: Painkiller vs Vitamin

- **GIS Engine (Produkt B) = Painkiller:** neutralizuje ryzyko utraty 10–15M PLN na błędnym zakupie działki. Kupuje się z budżetu operacyjnego bez negocjacji.
- **Compilore (Produkt A) = Vitamin:** usprawnia pracę, redukuje czas. Wymaga edukacji rynku i długiego cyklu sprzedaży.
- W B2B **Painkiller zawsze wygrywa** cenowo i sprzedażowo.

### Dane rynkowe (nowe, zweryfikowane)

- **Deweloperzy:** ~140,000 mieszkań/rok 2026 (PZFD). Sektor rośnie 34% w 10 lat, 8 nowych firm/dzień. Kilkaset do 2,000+ aktywnych MŚP deweloperskich (5–50 projektów/rok) = primary segment.
- **Fundusze:** 2,112 fundacji rodzinnych, 34 fundusze VC/PE Q1 2025, 4.3B EUR zainwestowane (Savills 2025) = secondary segment (dłuższy cykl sprzedaży, 3–6 miesięcy).
- **Rzeczoznawcy:** 7,591 certyfikowanych aktywnych. Niższe ARPU (500–1,500 PLN) ale masowy ruch. Model Pay-Per-Report.
- **Geoportal:** 6.1M sesji Q1–Q3 2025 (+kilkanaście % r/r). Potwierdza aktywny popyt bez podaży dobrego narzędzia.

### Ekonomika procesu due diligence (dane twarde)

Koszt manualnej analizy chłonności:

- Działka 500–5,000 m²: 3,750–5,000 PLN netto (0.75–1.00 PLN/m²)
- Działka 5,000–10,000 m²: 5,000–7,500 PLN netto (0.50–0.75 PLN/m²)
- Czas realizacji: 7–21 dni roboczych
- Cykl akwizycji jednej działki: 10–30 odrzuconych ofert przed wyborem jednej = koszt due diligence **30,000–200,000 PLN/zakup**
- ROI subskrypcji 3,000 PLN/msc: zwrot w pierwszym tygodniu

### Matematyka ARPU (potwierdzenie)

- 50,000 PLN MRR przy 900 PLN/msc = 55 klientów → śmierć przez support
- 50,000 PLN MRR przy 3,000 PLN/msc = 17 klientów → zarządzalne
- 50,000 PLN MRR przy 5,000 PLN/msc = 10 klientów → optymalne dla solo foundera

### Psychologia kupującego (Land Acquisition Manager)

Dwa motywatory: **chciwość** (być pierwszym na rynku, mieć przewagę informacyjną) i **strach** (zakupić działkę wyrzuconą poza OUZ = błąd kończący karierę).

**A-ha Moment w demo:** pokaż Conflict Alert na żywej działce z portfela klienta. Natychmiastowe uruchomienie obu motywatorów.

NIE pitch jako „narzędzie oszczędzające czas”. **PITCH jako „tarcza chroniąca 10M PLN kapitału”.**

### Ryzyka techniczne (Gemini + własna analiza)

1. **Jakość GML:** szacowane 20–40%+ wadliwych plików w pierwszej fali (błędy topologii, nakładające się poligony, NULL atrybuty, błędne kodowanie znaków). Pipeline musi być defensywny: `ST_IsValid()` + `ST_MakeValid()` + logowanie wszystkich napraw.
2. **Wersje XSD:** różne gminy używają różnych wersji schematu APP. Parser musi obsługiwać wersję 2.0 i wcześniejsze warianty.
3. **API resilience:** Rejestr Urbanistyczny może nie być gotowy przed deadline'm sierpień 2026. Potrzebne trzy źródła danych z automatycznym failover: Rejestr API → Geoportal WFS → BIP scraper per gmina.
4. **EGiB aktualność:** budynki w EGiB mogą być opóźnione o 6–18 msc. Każdy wynik OUZ musi pokazywać datę aktualizacji danych EGiB dla danego powiatu + ostrzeżenie jeśli dane starsze niż 180 dni.
5. **Kodowanie znaków:** ISO-8859-2 vs UTF-8 w atrybutach tekstowych. Wymagana normalizacja na wejściu pipeline.

### Decyzje produktowe wynikające z raportu

- **Primary segment:** deweloperzy MŚP (szybki cykl, właściciel decyduje)
- **Secondary segment:** fundusze PE/Family Offices (buduj pipeline, zamykaj po 6+ miesiącach)
- **Tertiary:** rzeczoznawcy (Pay-Per-Report, nie subskrypcja)
- **Pricing:** 2,000–4,000 PLN/msc (MŚP), 6,000–10,000 PLN/msc (Enterprise)
- **Walidacja:** concierge test (3–5 ręcznych analiz) **PRZED** budową produktu

---

## DR-8: Analiza Prawna — Bariery dla GIS Spatial Engine (2026-04-12)

### GREEN LIGHT — działania bezpieczne bez konsultacji prawnej

- Pobieranie i komercyjne przetwarzanie GML POG/MPZP (public domain, ustawa o otwartych danych Dz.U. 2023 poz. 1524)
- Odpytywanie ULDK API (GUGiK) po geometrii działki — bezpłatne i dozwolone komercyjnie
- Generowanie parametrów zabudowy z POG (PostGIS `ST_Intersects`)
- Obliczanie OUZ algorytmem geometrycznym
- Conflict Alert MPZP vs POG
- Sprzedaż jako „narzędzie informacyjne / Decision Support System”
- Brak wymogu uprawnień zawodowych: zawód urbanisty zderegulowany ustawą z 9 maja 2014 r. Analiza chłonności nie jest „samodzielną funkcją techniczną” w rozumieniu art. 12 Prawa budowlanego.
- EU AI Act: deterministyczne PostGIS SQL = **NIE** jest systemem AI w rozumieniu rozporządzenia 2024/1689. Zero wymogów certyfikacyjnych.

### RED LIGHT — absolutne zakazy

- Pobieranie numerów Ksiąg Wieczystych (NSA 2025–26: KW = dana osobowa, UODO aktywnie egzekwuje)
- Łączenie TERYT działki z danymi właściciela
- Generowanie wizualizacji brył architektonicznych (szara strefa art. 12 Prawa budowlanego)
- Terminologia: „opinia urbanistyczna”, „projekt architektoniczny”, „operat”, „ostateczna weryfikacja inwestycyjna”

### KLUCZOWE PODSTAWY PRAWNE

- **Art. 417 KC:** gmina odpowiada za błędne dane w GML (nie Compilore). Warunek: timestamp + source ID na każdym wyniku systemu.
- **Art. 473 § 1 KC:** Liability Cap skuteczny w B2B. Max roszczenie = 12 miesięcy subskrypcji. Wyłączenie *lucrum cessans*.
- **RODO:** dane planistyczne (geometria) poza RODO. Monitoring portfela klientów JDG = wymaga DPA jako załącznik do ToS.
- **PLD 2024/2853:** nowa dyrektywa o odpowiedzialności za oprogramowanie wchodzi do **9 grudnia 2026**. ToS musi być wdrożony przed tą datą.
- **AI Act art. 50:** tylko jeśli dodajesz LLM interfejs — wymóg transparency (komunikat że odpowiedź generowana maszynowo). **NIE** Annex III (High-Risk).

### WYMAGANY DISCLAIMER (wzór prawny)

Każdy wynik systemu musi zawierać:

> Zestawienie parametrów przestrzennych wygenerowane automatycznie na podstawie otwartych rejestrów publicznych [nazwa pliku GML, data pobrania, ID rekordu]. Dokument ma charakter wyłącznie informacyjny i nie stanowi opinii urbanistycznej ani dokumentacji projektowej. Wymagana weryfikacja przez uprawnionego specjalistę przed podjęciem decyzji inwestycyjnych. Odpowiedzialność za treść danych źródłowych ponoszą właściwe organy administracji publicznej (art. 417 KC).

### PRAWNIK WYMAGANY PRZED LAUNCH (lista)

1. ToS: Liability Cap + indemnification clause (art. 473 KC + PLD)
2. DPA dla funkcji monitoringu portfela
3. Potwierdzenie że pipeline nie pobiera KW
4. Disclaimer w formie prawnie skutecznej klauzuli umownej
5. AI Act art. 50 compliance jeśli LLM interfejs

**Szacowany koszt:** 3,000–8,000 PLN jednorazowo.

---

## DR-8: B2B Technical Distribution in Poland — Market Analysis (2026-04-16)

**Source:** External deep research report — "The Information Retrieval Burden and AI Adoption Gaps in Traditional Polish B2B Sectors"

### Core Finding

The information retrieval burden in Polish B2B distribution is structurally identical to the parametric PDF search problem Compilore solves. This is external validation of the core architecture, not just market research.

**Four pillars (from report) = Compilore's four design constraints:**
1. Large unstructured PDF corpus → Ingest + Docling
2. Parametric search need → hybrid search (pgvector + BM25)
3. Client-facing answer requirement → Query loop with citations
4. Safety and accuracy criticality → Gatekeeper + citation-hard requirement

### Quantified Pain (per vertical)

| Vertical | Time lost/week | Primary barrier to AI adoption |
|---|---|---|
| HVAC & Construction Supply | 10–15h/advisor | Liability fear, tables as raster images in PDFs |
| Electrical & Industrial Automation | 12–15h/engineer | Zero tolerance for hallucination, exact values required |
| Medical Devices | 15–20h/specialist | Regulatory auditing, data privacy mandates |
| Chemical & Food Ingredients | 16–18h/specialist | Chemical nomenclature complexity, REACH compliance |
| Automotive Spare Parts | 10–12h/advisor | Fragmented legacy data, visual exploded diagrams |

### Polish Market Specifics

- 49.15% of Polish enterprises use AI in some capacity — but skewed to marketing/HR in large firms
- Active AI adoption in construction/real estate: ~30%, mostly for basic data collection
- Primary adoption barriers: insufficient overview of suitable tools (26%), lack of training (18%), lack of trust (17%)
- Only 6% claim they don't understand AI — the problem is tool fit, not comprehension
- 60% of professionals in related sectors want to learn AI for their work — demand exists
- 85% of firms willing to pay 28% salary premium for AI-proficient candidates — budget exists, misdirected

### Pricing Validation

- Technical advisor salary: ~€2,950/msc gross (~€18.50–23/hr)
- 35% of time wasted = ~56h/msc = €1,000+/msc/employee drain
- AI tool at €100–250/user/msc = 4–10x ROI → justified
- WMS/ERP benchmark: $100–500/user/msc — Compilore fits inside existing software budget mental model
- Trial requirement: short freemium (7–14 days) critical to overcome trust deficit in B2B

### Sales & Buying Psychology

- SME (10–49 employees): budget holder = owner/founder. Avoid "AI/LLM/GenAI" language entirely. Use: "automated catalog search", "reduce RFQ turnaround", "eliminate engineering bottlenecks".
- Mid-market (50–250 employees): champion = Head of Presales / Sales Director. Economic buyer = CFO or IT Director. Integration with Comarch/Asseco is a procurement question.
- Key trust mechanism: live demo using the prospect's own PDFs. Immediate, visceral proof.

### GTM Channels Confirmed

- **Trade shows:** Ptak Warsaw Expo (153K sqm, 120+ fairs/year), Warsaw HVAC Expo (60K visitors, February), Industrial Automation Fair (13K visitors, May, Ptak Warsaw Expo)
- **Trade press:** Rynek Instalacyjny (HVAC), Energia Elektryczna (electrical), MM Magazyn Przemysłowy (broad industrial)
- **Associations:** POLMED (medical devices, €2.3B exports), Eurovent (HVAC specs), KIG (general trade)
- **Digital:** Technical SEO on Polish parametric queries, LinkedIn targeting Dyrektor ds. Technicznych / Kierownik Działu Ofertowania

### Structural Similarity Signal

All five verticals share identical workflow architecture → same Compilore engine, different adapters. Engineering investment for one vertical maps to all others with adapter-only changes. This is confirmation of the Adapter Pattern as the correct architectural choice.

### Pending Research (Scheduled)

- **DR-9:** Polish B2B distribution buyer journey & procurement mechanics — who signs PO, typical cycle length, Comarch integration feasibility
- **DR-10:** Competitive landscape — what catalog search tools exist in HVAC/electrical, why they fail, what Akeneo/Salsify/Syndigo offer vs what's missing

### Implications for Architecture

- `organization_id` hard isolation is now a Phase 2 prerequisite, not a nice-to-have (see D-73)
- Multi-language corpus (PL/EN/DE manufacturer catalogs) must be tested with Wojtek pilot
- Bulk upload flow needed — low-tech users will not self-onboard 300 PDFs via drag-and-drop
- Citation requirement (D-72) upgrades from "strong preference" to "hard requirement, no display without citation"
- VLM fallback priority increases: engineering tables in PDFs are frequently raster images (confirmed by report)

---

## DR-9: B2B SaaS Procurement in Polish SME Distribution (2026-04-17)

**Source:** Deep Research report — "Strategic Market Entry and 
Procurement Dynamics for B2B SaaS in the Polish HVAC and Electrical 
Wholesale Sectors"

### Procurement mechanics confirmed

- **Decision maker:** Owner (Właściciel) or Managing Director 
  (Prezes) — single-person call for 1,200–5,000 PLN/msc. No board 
  vote needed. CFO involved only in mid-market (150–250 employees).
- **Procurement cycle:** 1–3 months for SME; 3–6 months for 
  mid-market. Month 1 = demo + champion identified. Month 2 = trial 
  + ROI proof. Month 3 = owner review + sign.
- **Champion role:** Head of Presales cannot sign PO. Must be armed 
  with ROI calculator and Polish-language data security summary to 
  convince owner. Vendor must treat champion as extension of sales 
  force.
- **Comarch footprint:** ~80,000 Polish companies on Comarch ERP 
  Optima. "Integrates with Comarch" = massive trust signal even 
  without deep integration. Note: HermesTools does NOT use Comarch — 
  custom 10-year-old ERP (see D-80 for strategic angle).

### Critical new findings

**Biała Lista VAT (White List):** Every Polish SME accountant 
verifies vendor bank account on government registry before signing. 
Missing = high-risk flag, procurement stalls. Action logged as D-82.

**KSeF (e-invoicing mandate):** Headframe Sp. z o.o. as foreign 
vendor without Fixed Establishment in Poland = exempt from native 
KSeF XML. Can issue PDF invoices. BUT: PDF must include QR code for 
easy reconciliation in Comarch/Asseco by client's accountant. 
Without QR code = friction at reconciliation = churn risk. 
Verify Fakturownia template supports QR code.

**14-day trial standard:** B2B SaaS standard in Poland. 7 days 
insufficient — trial expires unused. Active onboarding mandatory 
(self-serve fails in low-digital-maturity sector). Updated D-77, 
09_PILOT.md.

**Polish UI mandatory:** English-only = fatal adoption friction 
outside Warsaw. HermesTools (Bielsko-Biała) = tier-2 city. 
Technical advisors in dept ≠ Wojtek (tech-savvy exception). 
Full Polish UI required Phase 2 day one. Logged as D-81.

**Annual contract incentive:** Start month-to-month (risk-averse 
owner). After 2–3 months successful use, offer annual with 
~15–20% discount ("2 months free"). Polish SMEs are highly 
sensitive to predictable OpEx optimization.

---

## DR-10: Competitive Landscape — Catalog Search in HVAC/Electrical (2026-04-17)

**Source:** Deep Research report — "The Knowledge Compiler Paradigm: 
Advanced Technical Document Search in the CEE HVAC and Electrical 
Wholesale Market"

### Market gap confirmed

No independent SaaS product in Poland or CEE offers agnostic, 
cross-catalog, parametric knowledge compiler for B2B technical 
distribution. Confirmed gap.

### Only relevant precedent: Grodno AiGRODNO

Grodno S.A. (major Polish electrical wholesaler) deployed AiGRODNO 
by Certusoft — AI purchasing assistant using LLMs + computer vision 
to read electrical diagrams from PDFs. Reduces offer preparation 
from hours to minutes (90% time reduction claimed). Grodno plans 
120M PLN investment over 5 years in AI.

**Key distinction:** AiGRODNO is proprietary to Grodno's inventory 
and portal. Does not solve the agnostic multi-brand search problem 
for independent distributors. This is exactly Compilore's gap.

### Why standard RAG fails on engineering tables (confirmed)

Five specific failure modes documented:
1. **Chunking artifacts** — table headers severed from values at 
   chunk boundary → LLM hallucinates
2. **Irrelevant Top-K** — "heat pump deployment" retrieves ML 
   deployment docs (semantic proximity, not technical match)
3. **Vocabulary mismatch** — "DTR for 15kW unit" vs manufacturer 
   calls it "Technical Operation Manual Model X15"
4. **Lost in the middle** — correct table retrieved but LLM ignores 
   values in center of context window
5. **Hierarchical flattening** — "values in Table 4 apply only 
   under conditions in Section 3.2" — flat extraction destroys 
   this dependency

Docling TableFormer solves failure mode #1. Our hybrid search 
(BM25 + vector RRF) partially addresses #2 and #3. #4 and #5 
are known risks at scale — mitigated by Gatekeeper grounding 
criterion.

### Architecture validation

Compilore's Agentic 4-loop + Gatekeeper = correct architecture 
for this problem. Raport confirms: "Agentic RAG provides the 
deterministic, multi-variable filtering required for strict 
engineering tasks." Our compiled Wiki (vs RAG amnesia) is 
identified as a structural architectural moat.

### New technology findings

**ColPali (Vision RAG):** Embeds entire PDF pages as images, 
bypasses OCR entirely. Prevents 40% information loss in 
technical schematics. Relevant when catalogs are scanned/rasterized. 
Logged as D-79 (Phase 2 Sprint 2 research item — assess after 
Wojtek uploads first catalog batches).

**Bielik-11B v3.0:** Polish-optimized open-source LLM. PLCC 
score 71.8 vs GPT-3.5 43.3. 83% cost reduction vs large API 
models. No hosted API yet — self-host only (requires GPU). 
Logged as D-78 (Phase 2 experiment after 4 weeks pilot data).

**Polish hybrid retrieval stack for maximum accuracy:**
- BM25 (lexical) + dense vector (semantic) + sparse vector 
  (SPLADE/ColBERT for Polish morphology)
- Reduces retrieval miss rate from 69% (standard ChatGPT stack 
  on Polish) to 6% (94% precision)
- Our current BM25 + pgvector RRF is correct foundation. 
  Adding SPLADE layer is Phase 2 enhancement.

---

## DR-11: HVAC Market Sizing — Poland & CEE (2026-04-17)

**Source:** Deep Research report — "Deep Market Analysis: Validating 
the Beachhead for AI-Powered Technical Search in the Polish and CEE 
HVAC/R Distribution Sector"

### Market size (Poland HVAC/R distribution)

- Active companies: 1,800–2,500 (80% confidence)
- Technical advisors/presales engineers: ~5,080 (75% confidence)
- Target tier (10–250 employees): ~660 companies = 35% of market

### TAM/SAM/SOM (HVAC + Electrical, Poland)

| | HVAC only | HVAC + Electrical |
|---|---|---|
| TAM | 60M PLN/yr | ~100M PLN/yr |
| SAM (35% maturity filter) | ~21M PLN/yr | ~35M PLN/yr |
| SOM (10% SAM, 36 months) | ~2.1M PLN ARR | ~3.5M PLN ARR |

**CEE regional TAM (HVAC + Electrical): ~273M PLN/yr**

Note: HermesTools is industrial assembly tools distribution 
(not HVAC) — smaller addressable market but identical workflow 
structure. Same TAM methodology applies.

### Regulatory tailwinds creating non-discretionary demand

**F-Gas Regulation EU 2024/573:** 55–60% effective reduction 
in F-gas quota 2025–2026. Engineers must now verify refrigerant 
type (R410A banned, R32 A2L, R290 A3 flammable) AND cross-reference 
minimum floor area calculations from safety manuals for every 
quote. Manual process = nightmare. AI catalog search = compliance 
necessity.

**EPBD:** From Jan 2025, fossil fuel boiler incentives banned. 
Distributors must re-educate sales force for heat pumps. Engineers 
must extract SEER ≥8.5 and SCOP ≥5.1 for A+++ certification from 
hundreds of databook pages.

**Industrial assembly tools analog (HermesTools):** ISO 6789 
calibration norm updates, PN/EN ESD safety standards, aerospace 
certifications (RECOULES → aerospace clients) — same non-discretionary 
compliance verification pressure, different documents.

### EU Grants as GTM lever

PARP Ścieżka SMART and NCBR STEP funding windows open in 2026. 
Grants can fully subsidize client's Compilore license, eliminating 
budget objection entirely. Implementation track (Cyfryzacja) 
covers software purchase. Application window: Apr–May 2026 (PARP). 
Logged as D-83. Assess after first paying client secured.

### Top 20 HVAC distributors in Poland (key names for BD)

Tier 1 (national/multinational): Sonepar Polska, Rexel Polska, 
Onninen (Kesko), Klima-Therm, Bims Plus, Wienkra, Schiessl Polska.
Tier 2 (national specialists): Systherm, Hydrosolar, Grodno S.A., 
TIM S.A., Alfa Elektro, Centrum Klima, Iglotech, Ventia, Alnor.
Tier 3 (regional): Dobra Klima, Klimat Komfort, Solar Polska.

---
