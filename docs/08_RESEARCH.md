# 08 — RESEARCH
## Compilore: Deep Research Findings & Implications

**This is a living document.** Each Deep Research session adds a new dated section.
Findings here directly inform decisions logged in 04_DECISIONS.md.

**Last updated:** 2026-04-27

---

## DR-15 RESULTS: EU AI Act as Compilore Buying Trigger (2026-04-22)

**Source:** Gemini Deep Research — "EU AI Act Compliance as a Software Buying Trigger for Polish Professional Services"  
**Verification status:** High. Primary sources cited: EUR-Lex Regulation 2024/1689, artificialintelligenceact.eu, PARP program documentation, EY/PwC Polish market reports.

### Hallucination Guard — corrections to previous claims

| Previous claim | Verdict | Correction |
|---|---|---|
| "AI Act fines up to €750,000" | REFUTED — applies to EU institutions only (Art. 100) | Private firms: up to €15M or 3% global turnover for high-risk non-compliance |
| "Whistleblower tool enables unannounced audits" | PARTIALLY CONFIRMED | Art. 74 grants surveillance authorities unannounced inspection rights. Whistleblower Tool exists but is separate mechanism |
| "Third-party conformity assessments mandatory before placement" | PARTIALLY CONFIRMED | Mandatory only if harmonized standards not applied, or for Annex I product safety components. Annex III (employment, legal) = internal control pathway permitted |
| "AI Act obligations extend to firms 'advising on' AI" | REFUTED | Pure advisory = outside scope. Firms that supply components or integrate code = reclassified as provider under Art. 25 |

### Enforcement Timeline (verified)
- February 2, 2025: prohibited AI practices + AI literacy obligations enforceable
- August 2, 2025: GPAI rules, penalty frameworks, governance structures enforceable
- August 2, 2026: HIGH-RISK AI (Annex III) fully enforceable — the critical deadline for our ICP
- August 2, 2027: Article 6(1) safety components (Annex I products)

### Polish Regulatory Architecture
- New regulator: KRiBSI (Commission for Development and Safety of AI) — centralized, sweeping enforcement powers
- Dual oversight: KRiBSI (technical AI compliance) + UODO (data privacy aspects) — creates complexity for Polish firms
- KRiBSI has authority to impose turnover-based fines on private operators

### "Provider Trap" — Art. 25 (key sales insight)
Polish IT consultancies that white-label models, fine-tune on client data, or substantially modify API outputs are legally reclassified from "deployer" to "provider" under Art. 25. Provider obligations = full Annex IV technical documentation + conformity assessment + post-market monitoring. Most Polish consultancies are unaware of this reclassification. This is the primary selling trigger for the IT consultancy ICP.

### Documentation burden (Art. 11, Annex IV — verified)
Providers must maintain before market placement and keep continuously updated:
- System architecture description (logic, algorithms, design rationale)
- Data governance documentation (training data provenance, labeling, outlier detection)
- Validation and testing procedures with metrics (accuracy, robustness, bias assessment)
- Dated and signed test logs
- Post-market monitoring plan (Art. 72)
- Operational logs retained minimum 6 months (Art. 26, deployers)

### "Computational Audit Bundle" — industry term for Annex IV package
Industry practitioners use this term for the exportable package of: system architecture + data provenance + validation metrics + version-controlled logs. This is what must be producible on demand for KRiBSI inspection. Compilore's citation trail + git_commit_hash + Wiki audit history = structural implementation of this requirement.

### Cost of compliance without tooling (CEPS estimates)
- Annual compliance cost per high-risk AI system: ~€52,000
- Initial QMS setup for 30-100 person consultancy: €193,000-330,000
- Annual maintenance: ~€71,400
- Per conformity assessment: €5,000-50,000 (manual documentation prep = 40% of cost)

### Polish market data
- Only 5.9% of Polish firms used AI entering 2024 (second lowest in EU) — but rapidly accelerating
- 58% of Polish organizations have already initiated AI Act compliance processes (EY 2025)
- 44% already using AI agents in some capacity (PwC 2025)

### PARP Ścieżka SMART — re-evaluation for IT/consulting segment
Previous decision D-85 rejected Ścieżka SMART for HermesTools (PKD Sekcja G). DR-15 reveals: PARP has allocated 1.3 billion PLN under FENG 1.1 for AI adoption, co-financing up to 75% for micro/small firms, 50% for medium. Intake: February-May 2026. Eligible sectors include Sekcja J (IT) and Sekcja M (consultancy) — i.e. the IT consultancy ICP. This creates a viable grant-subsidized sales path for the second ICP. Does NOT change D-85 for HermesTools specifically.

### Competitive landscape
- Vanta/Drata/Secureframe: checklist overlay, no runtime model observability, no RAG integration
- Enzai/eyreACT: AI-native but no Polish localization, targeting enterprise
- Productive24: audit trail + versioning but BPA tool, not RAG knowledge management
- Gap confirmed: no platform combines RAG retrieval + citation trail + Annex IV export for Polish SME professional services

### Strategic synthesis
AI Act creates a genuine, time-bounded buying trigger with hard August 2026 deadline. Commercial opportunity window: Q2-Q3 2026. PARP grant applications must be built Q1 2026. Compilore's citation-hard architecture + git_commit_hash versioning + audit history = structural implementation of Art. 12 (log-keeping) and Art. 14 (human oversight) requirements. This positions Compilore not as productivity tool but as regulatory compliance infrastructure.

---

## DR-16 RESULTS: AI Act Content Portal Feasibility (2026-04-22)

**Source:** Gemini Deep Research — "Polish B2B AI Compliance Content Portal Feasibility Study"  
**Verification status:** High. Primary sources verified: gov.pl, pti.org.pl, ey.com/pl_pl, uodo.gov.pl, gdpr.pl, techspresso.cafe.

### Polish AI Act information landscape — confirmed gaps

Current sources mapped:
- EY Polska: C-level legal overviews, no engineering guidance
- PTI AWSI: High depth, IT-professional focused, limited reach
- UODO: GDPR×AI Act intersection, regulatory language
- Techspresso.cafe: Journalistic, zero implementation guidance
- Ministerstwo Cyfryzacji: Official announcements only
- GDPR.pl (Omni Modo): High depth, compliance professionals
- PARP: SME-focused but basic

**Confirmed white space:** Zero Polish-language resources providing practical, engineering-centric AI Act compliance guidance for CTO of 20-100 person software house. Art. 25 Provider Trap covered by ONE article (EY Law, Sept 2025) focused on public procurement — not commercial software houses.

### SEO opportunity
- "Art 25 AI Act re-klasyfikacja dostawcy" — Very Low competition. Massive opportunity.
- "Kary AI Act Polska" — Medium competition. Interactive calculator angle.
- "Wymogi bezpieczeństwa AI Act NIS2" — Low competition.
- Programmatic SEO viable: Annex III category × Polish industry sector × compliance requirement matrix.

### GDPR.pl (Omni Modo) as blueprint
Survived post-enforcement cliff via: pivot to operational tools, DPO training certification, white-label compliance templates for law firms, retainer model for ongoing monitoring. This is the mandatory pivot plan for any AI Act portal.

### Content format recommendations
- Weekly digest (not daily) — regulatory cadence insufficient for daily content without dilution
- Interactive formats: risk classification decision tree, fine calculator, Art. 25 self-assessment
- AI-bot-optimized structure (entity-based, citable) — AI Overviews already dominant

### Agentic pipeline sources confirmed
- EUR-Lex: ELI system + CELEX 32024R1689 + RSS via "Mój EUR-Lex" dashboard ✓
- Ministerstwo Cyfryzacji: BIP + Dane.gov.pl + public consultation boards (scraper needed) ✓
- UODO: uodo.gov.pl — bi-weekly/monthly AI-relevant guidance ✓
- KRiBSI: Not yet operational (est. 2026). Route via MC until independent domain. ✓
- Frequency: Weekly digest feasible. Daily = content dilution risk.

### Lead gen funnel (validated from KSeF/RODO precedents)
Stage 1: Awareness (free calculator/checklist) → Stage 2: Education (gated guide) → Stage 3: Demo request (3-6 month cycle) → Stage 4: PoC → Stage 5: Contract

### Build-in-Public caveat
Polish B2B compliance buyers require institutional authority signals. Build-in-Public must be paired with visible expert partnerships (PTI certified auditor, named legal partner) to offset startup perception risk.

---

## DR-18 RESULTS: Strategic Viability and Go-To-Market Conditions (2026-04-22)

**Source:** Gemini Deep Research — "Strategic Viability and Go-To-Market Conditions for AI Compliance SaaS in Poland: The Compilore Case"  
**Verification status:** High for structural analysis. Named Polish SaaS ARR figures flagged where unverified.

### CRITICAL: KRiBSI enforcement capacity — 70 people, 27M PLN budget

This single fact changes the enforcement probability calculation fundamentally. KRiBSI cannot meaningfully audit Polish SME IT sector with 70 staff. Enforcement against SMEs will be indirect — via enterprise client requirements flowing downstream.

### Enforcement probability distribution (Gemini assessment)
- Scenario A (mass SME fines by Q2 2027): 10%
- Scenario B (KRiBSI focuses on large enterprises + public sector): 65% — MOST LIKELY
- Scenario C (further delays mirroring KSeF): 25%

**Strategic implication:** AI Act is NOT a direct fear-of-fine trigger for Polish SME IT. It IS a downstream compliance pressure trigger — enterprise clients requiring their IT vendors to prove AI governance. Same mechanism as Stellantis → Tier 1/2 suppliers. This is the correct sales framing.

### Moat analysis — optimal combination confirmed
Best defensible position for bootstrapped founder:
1. Regulatory locale depth (KRiBSI-specific workflows, UODO jurisprudence) — HIGH achievability, LOW cost, HIGH defense vs Vanta/Drata
2. Switching costs from compiled organizational wiki — HIGH achievability, MODERATE cost, HIGH defense vs all competitors
3. Grant writer channel distribution (PARP Ścieżka SMART) — MODERATE achievability, HIGH defense vs global GRC

**Weakest moats:** Network effects (need 100s of clients), compliance templates alone (trivially cloned by incumbents).

### Default alive threshold
- Required MRR: 18,000-22,000 PLN gross
- Required customers at 1,500 PLN/msc ARPU: 12-15 clients
- Achievable. Does not require viral growth or VC.

### Polish SaaS ARR benchmarks (honest assessment)
- NO verified Polish compliance SaaS reached 1M PLN ARR in 24 months bootstrapped
- Autenti (e-signature): years + VC funding
- Pergamin (contracts): years + enterprise partnerships
- 1M PLN ARR in 24 months = statistically anomalous without enterprise pivot or viral adoption

### Sales cycle reality
- Average B2B SaaS sales cycle globally: 134 days
- Polish IT compliance tool: 90-180 days realistic
- With PARP grant co-financing: add 3-6 months (reimbursement model = bridge financing needed by client)
- DMU: 6-10 stakeholders (CEO, CTO, DPO/legal counsel)
- Annual churn risk: post-audit abandonment if tool = one-time Annex IV generator only

### Adjacent revenue streams — priority ranking
1. **Regulatory Intelligence API** — HIGH viability, precedent (Clausematch, Archer), $1,000-3,000 USD/msc, enterprise GRC buyers, near-zero marginal cost. Build in 4-6 weeks using existing n8n + EUR-Lex pipeline.
2. **Certification marketplace** (connecting firms to KRiBSI-approved auditors) — MODERATE viability, referral fee model, Europrivacy precedent.
3. **White-label infrastructure for law firms** — MODERATE viability, scales via partner channel.
4. **Compliance data products** — LOW viability until 100s of clients.

### Acquisition path — concrete
Target acquirers: Vanta, Drata, OneTrust. Precedent: Drata acquired SafeBase $250M. OneTrust acquires localized compliance engines.  
Acquisition-attractive assets to build:
1. Base of Polish SME IT clients with proven retention
2. KRiBSI-specific procedural workflows in software
3. Regulatory intelligence feed (machine-readable Polish AI Act changes)

### Post-deadline sustainability — confirmed architectural advantage
AI Act mandates CONTINUOUS obligations (not one-time):
- Art. 72: Post-market monitoring — ongoing, cannot be done once
- Art. 43(4): New conformity assessment on substantial modification
- Art. 26: 6-month minimum log retention, rolling
- KRiBSI: Annual reporting obligations
Compilore git-commit versioning + citation trail = structural solution to these continuous requirements. Demand cliff is neutralized by operational dependency.

---

## DR-18: ProcessOS × Compilore — Context Engineering Synergy (2026-04-27)

**Source:** External deep research report — "Architectural Synergy and Market
Positioning: Context Engineering as a Joint Product Layer for Knowledge and Operations"

**Findings accepted:**

**1. knowledge_class taxonomy (Explicit_Normative vs Empirical_Descriptive)**
Frontmatter separation between normative documents (official catalogs, regulatory
text) and descriptive documents (AI synthesis, ProcessOS playbooks) is a correct
and necessary architectural primitive. Implemented as D-99. Useful independently
of ProcessOS: enables trust tiering in query responses.

**2. Organizational Pathology Alert**
When Lint detects conflict between a `knowledge_class: explicit_normative` page and a
`knowledge_class: empirical_descriptive` page on the same topic → surface as "Pathology
Alert" for human review. Do NOT auto-merge. This is a Phase 3 product feature but
architecture must accommodate it from Phase 1 frontmatter schema.
Example value: official Daikin warranty = 14-day processing. ProcessOS playbook shows
actual handling = 3-day informal process. Alert flags compliance gap for management.

**3. ProcessOS dual-layer architecture**
Headless-only ProcessOS (no UI) rejected after debate: process visualization
(swimlanes, timelines, bottleneck heatmaps) is fundamentally non-textual and
requires dedicated rendering. BUT ProcessOS must NOT have its own knowledge base
or query engine — that fragments corpus. Resolution: minimal visualization UI +
Markdown artifact output to Compilore git repo. Decision: D-101.

**4. M365 Graph API as Minimal Viable Integration**
Single OAuth connector to Microsoft 365 Graph API (email metadata + calendar events)
→ primitive "Communication Playbook" Markdown artifact → ingested to Compilore with
`knowledge_class: empirical_descriptive`. Avoids complexity of Comarch ERP connector.
Candidate Phase 2 sprint item. Activation trigger: post-pilot, if client has M365.

**5. 20+ employee inflection point for ProcessOS**
ProcessOS adds zero value at <5 employees (processes are tacit, event logs sparse).
Value inflection at 20+ employees where Comarch/M365 event logs become dense enough
for pattern detection. Use as product qualifier for ProcessOS upsell conversation.

**6. ProcessOS activation triggers (all four required)**
- Compilore has 3+ paying clients
- MRR > 15,000 PLN
- At least one client has 20+ employees
- That client explicitly requests workflow bottleneck visibility

**Findings rejected:**

- "Direct ingestion into single flat wiki is unequivocally superior": federated
  corpora with strict frontmatter tagging is safer until conflict resolution is
  production-proven. D-101 allows separate git namespace (`wiki/processes/` vs
  `wiki/catalog/`) within same repo.
- Celonis as primary ProcessOS competitor: Celonis is 6-figure EUR enterprise.
  Actual competitor = ClickUp + Notion AI used ad hoc, or nothing.

**DR-18 → Decisions logged:** D-99, D-101

---

## DR-17: Pre-Mortem — 12 Failure Scenarios Assessment (2026-04-27)

**Source:** External deep research report — "Pre-Mortem Analysis of Compilore:
Architectural, Market, and Regulatory Failure Modes in Polish B2B Technical Distribution"

**Scenario triage:**

**ACTIONABLE — correct diagnosis, mitigation adopted:**

*Scenario 11 (Confidence Decay Miscalibration):*
Report correctly identifies flat -5%/month as producing alert fatigue and unsafe
archival of valid engineering data. D-97 locked: page_type-aware decay. Engineering
catalog pages = 0% decay.

*Scenario 10 (Onboarding Cliff):*
Confirmed existential risk. PyMuPDF will fail on scanned tabular PDFs. D-98 locked:
30-document scope gate for Wojtek pilot (modern PDFs only). Docling timeline unchanged.

*Scenario 2 (Knowledge Rot — confidence score gaming):*
Report identifies `last_verified` updating on query citation without actual human
review. Valid gap. Mitigation: reinforcement score requires explicit user
verification flag, not just citation occurrence. Add to gatekeeper backlog.

*Scenario 12 (Context Engineering Ceiling):*
Parallel sub-agent decomposition (Agent A + B → synthesis Agent C) is valid and
native to LangGraph. Real risk for Bartek's setup: thermal throttling on MacBook
M4 Pro 24GB under 3 parallel Gemma 4 27B instances. Mitigation: sequential
decomposition as fallback; full parallel reserved for Hetzner production.

*Scenario 7 (RODO — silent API fallback):*
Confirmed RODO vector. D-100 locked: API fallback must be explicit, logged, and
user-acknowledged. Never silent.

**PARTIALLY CORRECT — calibration required:**

*Scenario 5 (Market Size Illusion):*
Report used single PKD 46.74.Z (1,210 firms). Compilore TAM spans 5+ PKD codes.
DR-11 SAM = 35M PLN/yr for HVAC alone. Report's median net profit argument
applies to microfirms (<5 employees) which are not Compilore's target. OEM
white-label mitigation proposed by report = 12-24 month enterprise sales cycle,
not viable pre-revenue. Existing TAM model in DR-11 is more accurate.

*Scenario 4 (Enterprise Displacement — NotebookLM):*
Real risk is perception/positioning, not technical displacement. "NotebookLM does
the same thing" is a buyer objection, not an architectural problem. Polish compliance
stack (KSeF/JPK_FA awareness), ERP trust signal, citation trails, RODO-native
infrastructure, and multi-tenant isolation are not replicable by NotebookLM.
Mitigation: sharpen positioning language to lead with compliance moat, not AI capability.

*Scenario 6 (Grant Channel Collapse):*
Report's math is correct (75 PLN/month = no behavioral change for advisor).
Proposed fix (100% first 3 months + 2K PLN bounty) still treats advisors as SaaS
sales reps. Correct model: advisors earn from grant value, not SaaS subscription.
D-102 locked.

**INCORRECT — rejected:**

*Scenario 1 mitigation (ERP integration as pilot prerequisite):*
ERP API integration is Phase 3, not a pilot prerequisite. Wojtek's value moment =
correct technical answer from catalog in <30 seconds. Pivot to "quote acceleration
engine with Comarch API" before pilot validation is premature scope expansion that
would kill the solo founder (solo founder wall = Scenario 3 in the same report).

*Scenario 9 (Commoditization — switching cost = zero):*
Report ignores data lock-in. After 3 months: compiled wiki of 300 catalogs,
wikilinks between pages, query history, confidence scores. Migration = multi-week
effort. Not ERP-class lock-in, but not zero either.

**Top 3 existential risks confirmed (report's ranking partially accepted):**

1. Onboarding Cliff (Scenario 10) — existential, actionable NOW → D-98
2. Confidence Decay Miscalibration (Scenario 11) — existential at 6 months → D-97
3. RODO silent fallback (Scenario 7) — legal, actionable NOW → D-100

Report's #1 pick (Market Size Illusion) demoted: TAM analysis was based on single
PKD code. Not existential given correct multi-PKD TAM model.

**DR-17 → Decisions logged:** D-97, D-98, D-100, D-102

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

## DR-13 RESULTS: HermesTools Company Facts & EU Grants Reality Check (2026-04-19)

**Source:** Claude session + live web verification (KRS registry, official PARP/ARP/FE Śląskie documentation). Supplements the Gemini Deep Research output which contained factual errors.

### HermesTools company facts (verified against KRS)

| Fact | Verified value | Source |
|---|---|---|
| Legal name | HERMESTOOLS SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALNOŚCIĄ | KRS 0000187483 |
| KRS number | 0000187483 | rejestr.io |
| NIP | 547-19-89-332 | official |
| REGON | 072886045 | official |
| Registered 1994 (brand) / 2004 Jan 14 (as sp. z o.o.) | ✅ 21+ years as sp. z o.o. | KRS |
| HQ | Sarni Stok 73a, 43-300 Bielsko-Biała | hermestools.eu |
| Branches | Poland + Czech Republic + Slovakia | hermestools.eu |
| Share capital | 50,000 PLN | KRS |
| Board | Barbara Bohatyrewicz (Prezes), Andrzej J. Murawski (Prokurent) | KRS |
| Main PKD | **46.14.Z** — Agents involved in wholesale trade of machinery, industrial equipment, ships, and aircraft | aleo.com |
| Additional PKD | 47.91.Z (non-specialized retail), 82.99.Z (business support), 95.29.Z (repair/maintenance) | aleo.com |
| Exclusive distribution (Poland) | KOLVER, APEX/Cleco, SCS Concept, Recoules, HAZET, Lobster, Sturtevant Richmont, Pop Avdel, Lubbering, Dotco, Hios, Koken, Fein, Doga, AMT, n-gineric | hermestools.eu + LinkedIn |
| Offers ISO 6789 torque tool calibration services | ✅ Confirmed | hermestools.eu |

### INTOOL merger — DEBUNKED

The "INTOOL absorption in February 2026" mentioned in Gemini DR-13 briefing is a **hallucination**. No evidence of any Polish industrial tools distributor named INTOOL exists. No M&A public filings found. This means:

- The "post-merger data fragmentation crisis" narrative from Gemini's grant strategy is fabricated
- Alternative "transformation trigger" narrative needed for any grant application (see 10_GRANTS.md)
- Do not reference INTOOL in any pitch, application, or strategic doc

### EU Grants — corrected parameters (post web verification)

**FE Śląskie 1.8 "Innowacje cyfrowe w MŚP" — actual parameters (NOT what Gemini report stated):**
- Maximum subsidy: **up to 60%** (not 70% as in Gemini report) — for medium enterprises
- Minimum project dofinansowanie: **500,000 PLN** (confirmed)
- Minimum company age: **3 completed financial years** — HermesTools satisfies (21+ years)
- Sectoral rule: trading/wholesale firms **are admissible** (confirmed in official FAQ), but production firms are preferenced in scoring
- Implementation period: 1 year from signing
- Eligible costs: WNiP (intangible assets), fixed assets, training
- Next expected window: monitor funduszeue.slaskie.pl — historical pattern is Q2/Q4 annual

**Dig.IT (ARP, FENG 2.21) — actual parameters:**
- Next nabór: **June 2026** (confirmed by biznes.gov.pl and arp.pl)
- Subsidy: **up to 50%** of net costs (de minimis aid)
- Grant range: **150,000–850,000 PLN** (not 300k as in Gemini report)
- Sectoral rule: **section C PKD (manufacturing) or "usługi produkcyjne"** — repair/maintenance/conservation services to third parties qualify
- Company age: 5 completed financial years required — HermesTools satisfies
- **HermesTools qualification question:** Main PKD is 46.14.Z (section G — trade), which is standard disqualification. BUT HermesTools offers ISO 6789 calibration services (repair/maintenance/conservation of precision tools for third parties), which fits the "usługi produkcyjne" definition. Qualification depends on **what % of revenue comes from calibration + assembly station design vs pure distribution trade**. This is a hard open question — must ask Wojtek/HermesTools management. Decision rule:
  - Revenue from production-adjacent services >50%: real Dig.IT opportunity
  - 30–50%: high application risk, low probability of formal acceptance
  - <30%: Dig.IT path closed

**Ścieżka SMART (PARP/NCBR, FENG 1.1):**
- 2026 MŚP nabór: February–April 2026 (ending 23 April 2026, may be closed by the time this is read)
- Additional 2026 naborów Q3
- Minimum project cost for MŚP: **3,000,000 PLN** — structurally unsuitable for Compilore-scale implementation at HermesTools, unless as part of a 3M+ bundle that includes genuine R&D component
- **Not recommended** for this pilot path — reference only for strategic future

**Kredyt Technologiczny:**
- Requires patented or own IP-backed technology; commercial SaaS adoption does not qualify
- **Not applicable** for this case

### Polish grant strategy reality check

Minimum viable FE Śląskie 1.8 project (500k PLN) requires bundling Compilore with:
- 3-year pre-paid license as WNiP (capital-ized intangible asset): ~150k PLN
- Hardware integration (workstations, scanners, infrastructure): ~100–150k PLN
- ERP interoperability / intelligence layer integration: ~150–200k PLN (aligns with D-80 if disclosed)
- Training + change management for technical advisor team: ~50–100k PLN

The Compilore SaaS fee alone cannot sustain a grant application — bundling is mandatory.

### New "transformation trigger" narratives (replacement for debunked INTOOL)

Three viable options for justifying "zasadnicza zmiana procesu biznesowego":

1. **Regulatory documentation explosion** — IATF 16949 revision 2025, AS9100→IA9100 transition 2026-2027, F-Gas EU 2024/573 torque calibration requirements, Industry 4.0 telemetry archiving mandates. Non-discretionary compliance pressure on HermesTools' end-clients.
2. **Succession / institutional knowledge capture** — 30+ year company, senior advisors likely approaching retirement. Compilore as enterprise-scale institutional memory. Requires verification: average age of technical advisors at HermesTools.
3. **ERP modernization prep** — 10-year-old custom ERP as data silo (per D-80). Compilore as intelligence layer = first step toward eventual ERP replacement. Best fit for FE Śląskie 1.8 "zasadnicza zmiana" requirement. Depends on D-80 rekalibration (see updated D-80).

**Recommendation:** Option 3 is strongest but depends on D-80 disclosure decision. Option 1 is safest regardless of D-80.

### Pending verification (to ask Wojtek / HermesTools management)

- [ ] What % of HermesTools revenue comes from calibration services + assembly station design + integration work vs pure distribution trade?
- [ ] Current headcount (to confirm MŚP classification — medium = up to 250 employees)
- [ ] Is there an existing active digitalization strategy or documented digital maturity assessment?
- [ ] Is anyone at HermesTools aware of Dig.IT or FE Śląskie 1.8 opportunity?
- [ ] Age distribution of technical advisor team (for succession narrative option)
- [ ] Annual revenue range (to estimate grant ceiling)

## DR-14 RESULTS: Industry 4.0 Documentation Standards & Audit Compliance Angle (2026-04-19)

**Source:** Gemini Deep Research output "Strategiczna Analiza: Rozszerzenie Architektury AI Compilore Poza Wyszukiwanie Katalogowe" + Claude session live verification against primary regulatory sources (IATF official portal, VW Formel Q konkret, Stellantis QRS documents).

**Verification status:** Unlike DR-13 which contained significant hallucinations (INTOOL merger, grant parameter errors), DR-14 core regulatory claims are verified accurate. This is the first DR cycle in this series where downstream decisions can be anchored directly to Gemini's output without heavy correction.

### Verified regulatory facts (usable as-is in grant applications, pitches, client docs)

**IATF 16949 clause 7.5.3.2.1 (Record Retention):**
Records (PPAP, tooling records, product/process design records, contracts and amendments) must be retained "for the length of time that the product is active for production and service requirements, plus one calendar year" — unless customer or regulatory agency specifies otherwise. 

Critical nuance that amplifies the urgency: retention clock starts at END of active production. For currently-produced automotive models (platforms often run 7-10 years), the effective retention period for a Tier 1/2 supplier is production period + service life + 1 year — commonly 15–30 years total. (Sources: advisera.com/16949academy, Elsmar Quality Forum clause 7.5.3.2.1 discussions, preteshbiswas.com, 16949store.com, IATF official portal)

**VW Formel Q konkret — D/TLD part retention:**
For parts classified as D (Dokumentationspflichtig) or TLD (Technische Lieferbedingungen Dokumentation) — i.e. safety-critical components — Volkswagen Group mandates 15-year retention "after last production" per VDA Volume 1. Covers drawings, production release docs, test specifications, sample reports, quality records including torque data for safety-critical fasteners. Also requires yearly D/TLD supplier self-audit conducted by VDA 6.3 certified auditors. (Sources: SMR Automotive Appendix P VW CSR 2024-07-30, Henniges Automotive SQA QRL, Ajka Solution training materials, automotivequal.com, Navistar supplier portal Formel Q konkret)

**Stellantis QRS — 48-hour response window:**
For audit contexts involving ISO/IATF regulatory/certification bodies, Stellantis reduces the maximum response time for supplier data submission to 48 hours. Failure to submit within window triggers incident reporting and penalties applied against supplier. (Source: Stellantis CSR IATF 16949 v1 June 2025 official publication via iatfglobaloversight.org; Huf Group supplier CSR document)

**NADCAP AC7116 / AC7117 (Aerospace special processes):**
Audit Criteria series AC7116 governs nonconventional machining/holemaking (relevant to RECOULES tool line distributed by HermesTools). AC7117 covers surface enhancement. Both require documented process parameter compliance (SFM/IPR/RPM) with zero-tolerance for deviations. Non-conformance reports trigger production stoppage and potential certification suspension. (Source: raport Gemini DR-14 — primary verification deferred but aligns with known PRI NADCAP structure)

**ISO 6789-2:2017 calibration re-trigger rules:**
Recalibration required maximum every 12 months OR 5,000 cycles (whichever comes first). Immediate recalibration triggered by any overload, impact, or misuse. Certificate must include expanded relative uncertainty, per-point uncertainty ranges, and accredited laboratory signature (ISO 17025 scope). HermesTools offers this service per PN/ISO/DIN — already captured in 02_STRATEGY.md.

### The underlying strategic thesis

HermesTools is uniquely positioned because three of its business lines (distribution + calibration + assembly station engineering) each generate or touch high-value document corpora:

1. **PFMEA + Control Plans + PFDs** — generated by HermesTools' engineers during assembly station design for OEM clients (VW Poznań, Stellantis Gliwice, Tier 1 suppliers). These are contractually the property of the end-client, but HermesTools retains working-copy knowledge.
2. **ISO 6789-2:2017 calibration history** — archived by HermesTools after every mobile calibration service at client sites. Represents 30 years of per-tool measurement data.
3. **Network integration manuals** — KOLVER KDU ↔ Siemens S7-1500 via PROFINET, Modbus TCP register mappings, OPC-UA configurations, IEC 62443 cybersecurity requirements.

These three corpora are **materially different in value from the product catalog corpus** currently targeted by the Compilore pilot. They are the basis for a potential second product segment (not second product — see Trap #1 below).

### Three strategic traps DR-14 report glosses over (must be respected)

**Trap #1 — Telemetry ingestion is not Compilore's fight.** 
The report suggests Compilore can ingest time-series torque curves from MSSQL/Oracle backends of ToolsTalk 2 / VPG+ / SCS VPG+. This conflates two fundamentally different system categories:
- Compilore = hybrid search over text (vector + BM25 + RRF)
- Telemetry analytics = time-series statistical process control over high-frequency sensor data

Adding time-series ingestion pulls Compilore into MES/MOM category, competing with Siemens Opcenter, Rockwell FactoryTalk, AspenTech. This is not our fight. 

**Correct interpretation:** Compilore does NOT read torque curves. Compilore provides interpretive context around torque curves — the PFMEA explaining what should happen, the calibration certificate proving tool validity, the OEM CSR explaining the audit boundary. The human (or ToolsTalk 2) reads the curve; Compilore reads everything around it.

**Trap #2 — Cross-client knowledge graph is a legal minefield.**
DR-14 sections 4.3 and 4.4 suggest building an anonymized cross-tenant knowledge graph where knowledge from Stellantis Gliwice can help a future VW supplier query. In practice:
- Polish Ustawa 2018 on trade secrets (implementing EU 2016/943) classifies PFMEA, torque programs, and process parameters as protected
- Standard OEM Tier 1 contracts contain clauses prohibiting "use of supplier data to train AI models" or "any derivative use beyond the named project"
- Anonymization techniques offer no legal safe harbor from OEM counsel demands
- First lawsuit from an OEM would kill HermesTools-Compilore relationship permanently

**Correct interpretation:** Compilore enforces hard `organization_id` isolation (already D-73). No cross-tenant learning. Each client's knowledge base is hermetic. This is a feature for procurement buyers, not a limitation to work around. Logged as D-96.

**Trap #3 — HermesTools is vendor, not OEM.**
Report occasionally implies Compilore should sell directly to VW Poznań or Stellantis Gliwice. This is a 12–18 month procurement cycle with OEM risk tolerance near zero. HermesTools is our direct client (Phase 2 beachhead per D-70). If Compilore delivers value to HermesTools, HermesTools can position themselves as "Compilore-enhanced service provider" to their OEM clients — but Direct-to-OEM sales is Phase 3+ at earliest.

### The "audit-deadline-driven" sales insight (new — not yet in 02_STRATEGY)

Polish B2B sectoral buying behavior (per DR-9 conservative buyer research) is deadline-driven, not productivity-driven. DR-14 regulatory facts reveal that HermesTools' clients face regular, predictable, externally-imposed deadlines:

- Stellantis 48h window (for audit data) = recurring monthly/quarterly pressure
- VW D/TLD annual self-audit by VDA 6.3 certified auditor = yearly compliance event
- ISO 6789 recalibration every 12 months / 5000 cycles = continuous rolling demand
- AS9100 / NADCAP surveillance audits = semi-annual for aerospace Tier 1/2
- IATF 16949 retention clock running for decades post-production

This creates a deferred but potentially powerful repositioning of Compilore from "productivity tool for technical advisors" (current: 1,200–1,800 PLN/mo) to "audit-deadline insurance for compliance managers" (potential: 3,500–8,000 PLN/mo). See D-95 for decision framework.

### What belongs in current (pilot-phase) activity

**Do now:**
- Week 3-4 pilot test: can Compilore generate audit-readiness bundle in <15 min (see 09_PILOT.md update)
- Ask Wojtek about aerospace footprint (RECOULES customers) during normal pilot feedback — do NOT conduct separate interview
- Log Option D (audit compliance pressure) as grant transformation narrative (see 10_GRANTS.md)
- Add `adapters/audit_compliance/` to backlog (see 07_SPRINTS.md)

**Do NOT do now:**
- Build telemetry ingestion
- Pitch Compilore to Stellantis or VW directly
- Design cross-client knowledge graph
- Launch Insurance pricing tier before pilot validates core premise

**Decision gate for audit-framing pivot:** End of 8-week Wojtek pilot. If pilot succeeds on core catalog search AND audit-bundle test question resolves positively AND HermesTools has real aerospace footprint, then activate D-95 audit-framing strategy.

## DR-12 + DR-13 + DR-14 — Scheduled (2026-04-19)

**Status:** DR-12 still pending execution. DR-13 executed with significant factual errors, superseded by DR-13 RESULTS (2026-04-19). DR-14 executed 2026-04-19, core regulatory claims verified accurate, findings captured in DR-14 RESULTS (2026-04-19) above — first research cycle in this series usable with minimal correction.
Prompts authored in Claude session 2026-04-19.

### DR-12: HermesTools Industry Deep Dive
**Scope:** Precision assembly tools distribution specifics —
document corpus anatomy, parametric query types, mandatory 
compliance docs (ISO 6789, ESD, aerospace AS9100), 
manufacturer portal limitations (KOLVER, APEX, CLECO, SCS), 
Industry 4.0 documentation burden, competitive landscape 
for this specific niche.

**Why:** Wojtek pilot test questions and onboarding framework 
need to be calibrated to actual HermesTools workflow, not 
generic HVAC/electrical assumptions.

### DR-13: EU Grants for HermesTools — Compilore Implementation
**Scope:** PARP Ścieżka SMART, Dig.IT, Kredyt Technologiczny, 
FE Śląskie regional funds. Specific to Śląskie voivodeship 
(Bielsko-Biała). Can SaaS subscription qualify as 
cyfryzacja? INTOOL absorption as transformation trigger. 
Headframe as consortium partner angle.

**Why:** If 50-85% of license cost is subsidized, entire 
sales conversation changes — from "kup narzędzie" to 
"pomożemy ci dostać grant na to". Eliminates budget 
objection entirely.

### DR-14: Industry 4.0 Smart Tools & Documentation Standards
**Scope:** IATF 16949 / AS9100 torque documentation requirements, 
smart tool data (KOLVER KDS torque curves, PROFINET/OPC-UA 
integration docs), RECOULES aerospace NADCAP angle, 
Desoutter/Atlas Copco competition, potential second use 
case for Compilore as "AI layer above torque data".

**Why:** HermesTools offers calibration services and assembly 
station design — they already touch process documentation. 
This may expand Compilore from catalog search into 
process knowledge compilation (higher ARPU, deeper moat).

**Pending actions after DR results:**
- [ ] Update 09_PILOT.md Week 1-2 test questions with 
      DR-12 findings
- [x] Assess grant feasibility for HermesTools (DR-13 RESULTS, 2026-04-19)
- [x] Evaluate Industry 4.0 as Phase 3 use case (DR-14 RESULTS, 2026-04-19 — logged as deferred decision D-95, activation trigger: end of Wojtek pilot)
- [x] Update 09_PILOT.md Week 3-4 test questions with DR-14 audit-bundle scenario (this session)

---

## DR-15: Strategic Synthesis — External Reports + EU Grants Verification (2026-04-20)

**Source 1:** External deep research report — "Product-Market Fit 
Analysis: B2B Knowledge Management Tools in the Polish SME Market"

**Source 2:** External deep research report — "Competitive Analysis 
of AI-Powered Knowledge Management and the 'Enterprise Brain': Global 
Landscape and CEE Market Dynamics"

**Source 3:** Verification web searches (PARP Ścieżka SMART 2026 
regulations, ARP Dig.IT PKD eligibility, REACH/CLP 2026 deadlines, 
MDR 2026-2028 timelines, Polish grant writer consultancy landscape, 
SaaS partner program models)

### Core findings that changed strategy

1. **Pivot to B2B distribution (D-70) is externally validated** — 
   both reports confirm painkiller framing over vitamin. Time-savings 
   ROI (€1,000+/mo drain per advisor) is quantifiable, sales-ready, 
   and falsifiable in 30 seconds. This beats abstract narratives.

2. **Citation-hard requirement (D-72) is moat-class architectural 
   choice** — not UX polish. Harvey AI at $1,200/user/msc still 
   hallucinates 1/6 complex queries. Compilore "no citation = no 
   display" is structural differentiator for compliance-sensitive 
   sectors. Frame this as Trust Guarantee in sales.

3. **Moat is shorter than 02_STRATEGY.md previously implied.** 
   "Compiled wiki" as lone moat will erode within 12 months as 
   Karpathy's pattern diffuses to open source (Axiom Wiki, Tanka AI, 
   pi-llm-wiki already emerging). Real moat = compliance + locale 
   package (D-81, D-78, D-82 + RODO-native + Comarch trust signal + 
   regulatory awareness). Now packaged as "Compliance & Trust Moat" 
   section in 02_STRATEGY.md.

### Regulatory tailwinds in adjacent verticals (noted, not actionable)

**Medical Devices (MDR EU 2017/745):**
- May 2026: Class III custom-made implantable deadline
- December 2027: Class III and Class IIb implantable (non-WET)
- December 2028: other Class IIb, Class IIa, Class Is/Im
- Poland penalty: up to 5,000,000 PLN fine + market withdrawal
- Distributor obligation: MDR Article 16 quality management for 
  relabel/repack; EUDAMED registration

**Chemical (REACH + CLP + SDS):**
- November 1, 2026: substances already on market must have updated 
  SDS + classification per CLP Delegated Act (EU 2023/707)
- Ongoing: SDS update obligation is continuous per REACH Art. 31(9) 
  — any change in classification, composition, new regulation, or 
  risk information triggers mandatory 12-month backward distribution 
  to all recipients of last 12 months
- Responsible party: producer, importer, AND distributor each liable

**Decision:** both sectors represent strong demand. Compilore product 
fit exists for retrieval use case (Use Case A: "find info under 
regulatory pressure"). Compilore product fit does NOT yet exist for 
compliance monitoring use case (Use Case B: event-driven SDS/technical 
file updates from ECHA/EUDAMED feeds — would be separate product). 
Both verticals deferred per D-86: no entry without design partner.

### EU grant landscape — corrections vs DR-11

**Ścieżka SMART (PARP):** rejected for Compilore clients. Requires 
obligatory B+R component, 3M PLN minimum project size, innovation at 
national level. Target: firms developing own R&D, not SaaS buyers. 
Previous entry in DR-11 was incorrect.

**Dig.IT (ARP):** fits production MŚP (Sekcja C — przetwórstwo 
przemysłowe and production services) only. 150K-850K PLN grant, 50% 
funded. Next window: June 2026. Main PKD restriction is strict — 
explicitly verified: standard office or accounting software excluded. 
Compilore must be framed as "AI/ML analytics" or "automated process 
knowledge" to qualify under program obszary. Disqualifies HermesTools 
(PKD 47.99.Z, Sekcja G). Eligible for downstream clients #3-10 if 
targeted to production-sector MŚP.

**Regional RPO (FE Śląskie 1.3 and equivalents):** most likely path 
for distributors and other Sekcja G PKD clients. Window timing 
voivodeship-dependent; to be verified via grant writer partner.

**BUR (Baza Usług Rozwojowych):** PKD-agnostic, covers training 
(not software license), 50-80% voivodeship-dependent refund. One-time 
registration of Headframe as BUR provider = permanent infrastructure 
for any future client (D-88).

### Buying triggers ranking — methodological caveat

Raport 1 ranks Polish SME KM buying triggers as:
1. Key person leaving (Highest Frequency)
2. Audit/Compliance deadlines (High)
3. New hire onboarding pain (Medium-High)
4. Sales/support latency (Medium)

**However:** report does not disclose ranking methodology, sample 
size, or distinguish macro retention trend from actual software 
buying triggers. Academic sources (IDEAS/RePEc, PJMS, Biblioteka 
Nauki, EBRD diagnostic) are about KM adoption generally, not 
empirical buying-trigger studies. Ranking is directional, not 
quantitative.

Strategic implication (D-87): do NOT narrative-shift primary pitch 
to succession. Quantified time-savings (trigger #4 by report ranking, 
but most falsifiable by buyer in 30 seconds) is the better lead for 
risk-averse Polish SME owner. Succession narrative = amplifier, not 
primary.

### Partnership channel discovery — grant writer success-fee model

Polish grant consulting industry standard: consultant charges nothing 
upfront, takes 5-15% commission on awarded grant as success fee, and 
the grant-writing service itself is a qualified project cost covered 
by the grant. Client out-of-pocket = zero. This creates natural 
alignment with Compilore (D-84):

- Grant writer wants high-value projects (AI SaaS > basic hardware)
- Grant writer already holds MŚP trust
- Compilore wants leads with pre-approved budget
- 5% recurring Compilore revenue share for 24 months aligns partner 
  incentive toward retention, not just close

**First 5 outreach targets identified** (see D-84 for list). Quality 
filter: partner must have 2+ recent successful MŚP projects under 
Dig.IT or FENG involving software (not hardware-only).

### Pending items for post-HermesTools re-evaluation

- Verify HermesTools revenue split by PKD code (47.99.Z vs 28.29.Z 
  vs 33.20.Z) to confirm D-85 Dig.IT disqualification
- Verify current Działanie 1.3 FE Śląskie state (or equivalent 
  regional RPO) — action for grant writer partner on first call
- Evaluate use-case A (retrieval under regulatory pressure) product 
  fit for medical/chemical after first design partner contact 
  (post D-86 release)
- Run DR-12/13/14 (scheduled 2026-04-19) — DR-15 does not replace 
  these, but recontextualizes DR-13 findings (EU grants fit) within 
  corrected program map above

**Decision trace:** `docs/04_DECISIONS.md` **D-84–D-88** (post-report 
strategy synthesis). Prior PRE-PILOT rows that occupied numeric slots 
D-84–D-86 (ERP disclosure, audit deferral, cross-tenant isolation) are 
**D-94–D-96** with SUPERSEDED cross-references.

---
