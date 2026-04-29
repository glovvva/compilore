# 02 — STRATEGY
## Compilore: Market, GTM, Pricing, Risks

**Last updated:** 2026-04-22

---

## Two-Phase Strategy

### Phase 1 — Personal Playground (NOW, active)
**Goal:** Validate the 4-loop architecture on my own knowledge management.
**Documents:** Text and Markdown only — articles, strategy notes, research, transcripts.
**Interface:** Web UI (localhost:8001), path to Hetzner deploy.
**Success criteria:** Am I using it daily? Does the Wiki compound? Go/No-Go for Phase 2.
**Decision gate:** End of Sprint 4 — honest self-assessment before writing a single line of Phase 2 code.

### Phase 2 — Architect SaaS (AFTER Phase 1 validation)
**Goal:** Productize for Polish architectural firms (biura projektowe).
**Trigger:** Phase 1 decision gate passed + Phase 2 validation metrics met (see §8.3 of brief).
**Key additions:** Docling PDF parser, MPZP adapters, VLM fallback, PII middleware, Next.js UI, Kinde auth, legal docs.

---

## Target Market (Phase 2)

### PIVOT DECISION (2026-04-16): B2B Technical Distribution — PRIMARY beachhead

Previous beachhead (architectural firms / MPZP) is SUPERSEDED. See D-70 in 04_DECISIONS.md.

**New beachhead:** Polish B2B technical distribution companies — HVAC, electrical wholesale, industrial automation, medical devices, chemical/food ingredients, automotive spare parts.

**Why pivot:**
- Architects = vitamin (convenience). Distribution advisors = painkiller (10–20h/week lost per person, €1,000+/msc/employee cost).
- No existing relationships or distribution built for architect market — zero switching cost.
- B2B distribution has clear, quantified ROI: 35% of technical advisor time wasted on manual PDF search.
- Higher defensible ARPU: €100–250/user/msc (vs 200–600 PLN for architects).
- Wojtek (pilot user, technical advisor) = direct line to first paying corporate client.

**Pilot user:** Wojtek — technical advisor, already onboarding. Will upload full working folder set over 1–2 months. First signal: does Compilore answer parametric technical questions from manufacturer PDFs with correct citations?

**Conversion path:** Wojtek (free pilot) → internal champion → company buys Team/Company tier → adjacent companies in same vertical.

---

### Segment Map (B2B Distribution)

| Segment | Key Role | Time Lost/Week | Estimated ARPU | Priority |
|---|---|---|---|---|
| HVAC & Construction Supply | Technical Sales Advisor, Presales Engineer | 10–15h | 600–1,500 PLN/msc | **PRIMARY** |
| Electrical & Industrial Automation | Systems Integrator, Presales Support | 12–15h | 600–1,500 PLN/msc | **PRIMARY** |
| Medical Devices | Field Technical Specialist, Regulatory Affairs | 15–20h | 1,200–2,500 PLN/msc | Secondary |
| Professional Consulting Firms | Compliance Officer, Senior Consultant | 16h per audit event | 2,500–5,000 PLN/msc | Secondary |
| IT Consultancies (AI builders) | CTO, Head of Engineering | 64h per compliance audit event | 3,500–5,000 PLN/msc | Secondary — activate Q3 2026 |
| Chemical & Food Ingredients | Product Specialist, Formulation Advisor | 16–18h | 1,200–2,500 PLN/msc | Secondary |
| Automotive Spare Parts | Parts Advisor, Technical Counterperson | 10–12h | 400–800 PLN/msc | Tertiary |

**HVAC + Electrical = first two verticals.** Identical document structure (parametric PDFs, engineering tables, multi-language catalogs). Wojtek's vertical is the entry point.

**Consulting trigger note:** surprise vendor compliance audits from enterprise clients (banks, insurers, multinationals). Key pain: 44,800 PLN total cost per audit event (4 seniors × 16h, PLN 200/h labor + PLN 500/h opportunity cost). Compilore as audit bundle generator eliminates crisis response entirely.

**IT consultancy trigger note:** Art. 25 "Provider Trap" — firms building RAG or fine-tuning models for clients are legally reclassified as AI providers. August 2, 2026 enforcement deadline. PARP Ścieżka SMART (Sekcja J/M) covers up to 75% of software cost.

---

## Distribution (Phase 2)

### GTM reality for Polish B2B distribution sector

This market does NOT respond to LinkedIn-first, build-in-public, or standard SaaS marketing. Trust is built physically and through industry-specific channels.

### Channel 0 — Grant writer partnerships (fastest scale vector)

Polish grant consulting firms operate on success-fee model: client pays 
nothing upfront, consultant takes commission (5-15%) from awarded grant. 
Consultant's fee is itself a qualified project cost, so client effectively 
pays zero out-of-pocket for grant-writing services. This creates a natural 
alliance: grant writers need AI/digitization projects for their clients 
(higher grant value = higher success fee), Compilore needs leads with 
pre-existing trust and 50% subsidized willingness-to-pay.

**Referral structure (D-84):** 5% recurring revenue share for the first 
24 months of each referred client's subscription. No territorial 
exclusivity. No upfront cash. Non-exclusive, multi-partner from day one.

**First 5 outreach targets:**
- Strategor (Warsaw, 27+ years, CEE consulting platform)
- Grants.Capital (multi-million grant portfolio)
- All-Grants (Katowice/Śląsk — geographically near HermesTools)
- DotacjeDlaKażdego (explicit success-fee model)
- Najda Consulting (active in Dig.IT / Ścieżka SMART communications)

**Qualification filter per partner call:** ask for 2 recent successful 
MŚP projects under Dig.IT or FENG. "Bought hardware" = poor fit. 
"Implemented ERP with AI module" = good fit.

**Sales-cycle tradeoff:** Grant application window + processing is 
3-6 months. Client will not implement Compilore until grant is awarded. 
Long TTM, but post-grant close rate approaches 100%.

**Churn risk flag:** client who buys to "spend grant money" churns in 
month 13. Screen every referred prospect with Compilore-led discovery 
call before accepting partner-sourced lead.

### Channel 1 — Champion-led (primary, first 12 months)
- Wojtek = pilot champion → introduces to company decision-maker (owner or head of presales/engineering)
- Pattern: 1 engaged user per firm → internal demo → company purchase
- Replicate: identify 3–5 firms in same vertical as Wojtek through him directly

### Channel 2 — Trade shows (HVAC + Electrical verticals)
- Warsaw HVAC Expo (February, annual) — 60,000 visitors, 450 exhibitors, exact target buyer
- International Trade Fair for Industrial Automation (May, Ptak Warsaw Expo) — 13,000+ visitors, 200+ exhibitors
- Positioning: NOT "AI startup". Exhibit as "technical catalog search tool". Demo live on the floor using PDFs from exhibitors at the same event.

### Channel 3 — Trade press
- Rynek Instalacyjny — dominant HVAC monthly, digital portal
- Energia Elektryczna / Portal Elektryka — electrical wholesale community
- MM Magazyn Przemysłowy — broad industrial B2B management
- Format: case study ("How [firm] reduced RFQ turnaround by 50%"), NOT product announcement

### Channel 4 — Trade associations
- POLMED (medical devices) — largest distributor chamber, €2.3B export footprint
- Eurovent (HVAC standards body) — dictates specs Polish advisors search for daily
- KIG (National Chamber of Commerce) — broad B2B

### What NOT to do (yet)
- No LinkedIn "build in public" for this vertical — wrong audience
- No cold email blasts — trust deficit is real (17% cite distrust as primary barrier)
- No "AI" or "LLM" in any marketing copy — use: "automated catalog search", "instant technical answer with source citation", "eliminate RFQ bottlenecks"

---

## EU Grants as GTM Lever

Grant-funded sales eliminate budget objection for Polish SMEs. This is 
channel accelerant, not standalone strategy — complements Channel 0 
(grant writer partnerships) and requires a grant-eligible client.

**Program fitness map:**

| Program | Grant size | Fit for Compilore | Blocker |
|---|---|---|---|
| Ścieżka SMART (PARP) | 3M+ PLN min | Does NOT fit | Requires B+R component; minimum project size 3M PLN; innovative at national level required |
| Dig.IT (ARP) | 150K-850K PLN, 50% funded | Fits for Sekcja C (production) MŚP | Wiodący PKD must be manufacturing (przetwórstwo przemysłowe) or production services. Distributors with Sekcja G main PKD (like HermesTools, PKD 47.99.Z) are disqualified. |
| Regional RPO (e.g. FE Śląskie 1.3) | Varies | Likely fits for distributors | Requires voivodeship-specific research; window timing variable |
| BUR (Baza Usług Rozwojowych) | 5K-20K PLN training refund | Fits any PKD | Only covers training, not software license. Register Headframe as BUR service provider to enable for any future client. |

**HermesTools specific (D-85):** PKD 47.99.Z main = disqualified from 
Dig.IT (Sekcja C production MŚP only). Secondary codes 28.29.Z and 
33.20.Z do not override main PKD in ARP assessment — near-certain Dig.IT 
rejection. Use regional RPO path instead.

**Strategic use:**
- Primary beachhead (HVAC distributors): regional RPO path via grant 
  writer partnership (Channel 0)
- Clients #3-10 if shifted to production MŚP (Sekcja C — electrical 
  equipment manufacturers, component producers): Dig.IT June 2026 
  window, full grant-writer-driven sale

**What Compilore does NOT do:** write grant applications in-house. 
Grant writing is grant writer's job. Compilore provides product, ROI 
calculator, technical specification, and case study material.

---

## Pricing (Phase 2)

**Model:** Team-tier flat fee (NOT per-seat, NOT usage-only flat-rate).
**Rationale:** Per-seat in SME triggers sticker shock. Flat team fee anchors on headcount, not individual. Usage-based component only kicks in above tier limits.
**Value metric:** Documents processed + Wiki size per organization.
**Payment stack:** Fakturownia + Przelewy24. Stripe is BANNED — no JPK_FA support.

| Tier | Price | Users | Docs/msc | Queries | Notes |
|---|---|---|---|---|---|
| **Solo** | 300–400 PLN/msc | 1 | 50 | 500 | Freelancer / independent advisor |
| **Team** | 1,200–1,800 PLN/msc | 2–10 | 300 | Unlimited | Shared org Wiki, 1 admin panel |
| **Company** | 3,500–5,000 PLN/msc | 10–50 | Unlimited | Unlimited | API access, dedicated onboarding |
| **Enterprise** | Custom 8,000+ PLN/msc | 50+ | Unlimited | Unlimited | On-premises option, SLA |

**Deferred pricing consideration (activation trigger: pilot success + D-95 activation):** Research indicates that audit-deadline-driven positioning (48h Stellantis response, 15-year VW D/TLD retention, IATF 16949 retention compounding) may support a premium tier priced as "compliance insurance" rather than productivity tooling. Early estimate 3,500–8,000 PLN/mo for organizations with material OEM audit exposure. Do not introduce this tier before 8-week pilot validation of core catalog search + audit-bundle test question. See D-95 and 10_GRANTS.md Option D.

**ROI framing for sales (quantified, source-backed):**
- Technical advisor costs ~€2,950/msc gross (Poland 2026)
- 25-30% of their week = searching for information (IDC/McKinsey data)
- 18 minutes = average time to find one document (Gartner)
- 440 hours/year = 11 full work weeks per advisor lost to search
- For a 5-person technical team: 55 weeks/year = over 1 full FTE equivalent
  spent on being a human search engine
- Team tier at 1,500 PLN/msc = cost of ~0.5 hours of the problem per week
- Primary pitch: "Compilore recovers 11 weeks of revenue-generating capacity
  per advisor per year. It costs less than one afternoon of the problem."
- Secondary pitch: "New hire reaches full productivity in 2 weeks instead
  of 4 months — institutional knowledge is queryable from Day 1."
- Source: DR-19

**Trial:** 14-day free trial per organization (not per user). Pilot users (like Wojtek) = extended manual pilot tracked separately.

---

## Competitive Positioning

**Frame:** "Your technical advisors spend 35% of their time being a human search engine. Compilore eliminates that."

**Not competing with:** ERP systems (Comarch, Asseco) — we integrate alongside them, not replace them. Buyer anchors our price against ERP/WMS cost (~$100–500/user/msc) — we fit inside that range.

**Competing against:** Excel spreadsheets, CTRL+F in PDFs, phone calls to manufacturer reps, human memory and experience.

**Moat:** Compiled organizational Wiki. After 3 months of use, a firm has a proprietary, structured knowledge base of every manufacturer catalog they work with. New employee onboarding = query the Wiki instead of sitting next to a senior advisor for a year. Churn = losing that institutional memory. Data lock-in is a feature, framed as "your firm's technical memory."

**AI Act compliance trail:** Polish firms deploying or advising on AI systems (EU AI Act, effective July 2024) must maintain documented decision frameworks and data lineage. Fines up to €15M or 3% of global turnover (Art. 6-50 EU AI Act). Compilore's citation trail and Wiki audit history = AI governance infrastructure.

**Trust mechanism:** Every answer must include exact source citation (document name + page number). No citation = answer not shown. This is non-negotiable in this sector — one wrong recommendation = structural failure, chemical hazard, or MDR violation. Citation trail is the product, not a UX nicety. For automotive and aerospace clients specifically, citation trail is not just a trust mechanism — it is the legal artifact needed to satisfy IATF 16949 clause 7.5.3.2.1 retention obligations and VW Formel Q D/TLD 15-year archival requirements. Every Compilore answer with full citation trail is, by construction, audit-ready. This is a structural competitive advantage over proprietary vendor silos (ToolsTalk 2, VPG+) which do not natively produce human-readable cited artifacts. (See DR-14 RESULTS in 08_RESEARCH.md for regulatory detail.)

### Compliance & Trust Moat (packaged as one)

Individual architectural decisions across the project — when packaged 
together — form a defensible moat against Western horizontal competitors 
(Glean, Harvey) who cannot localize fast enough:

1. **Polish UI from day one** (D-81) — fatal adoption friction in 
   tier-2/3 cities without this
2. **Polish retrieval stack ready** (D-78 — Bielik-11B Phase 2 
   experiment) — morphological accuracy Western models lose
3. **KSeF + Biała Lista VAT compliance** (D-82) — procurement-grade 
   from first invoice
4. **RODO-native architecture** — Hetzner EU, PII stripping, ZDR 
   endpoints, tiered sensitivity routing
5. **Comarch integration path** (trust signal even without deep 
   integration — ~80,000 Polish SMEs on Comarch Optima)
6. **Regulatory awareness** — F-Gas EU 2024/573, EPBD 2025 (HVAC), 
   REACH/CLP Nov 2026 (chemical), MDR 2026-2028 phased (medical)

This package is the real moat — not "we have a compiled wiki" (every 
vendor will have that in 12 months per Karpathy pattern diffusion). 
Pitch as "Compilore is the only knowledge system built for Polish 
B2B compliance from architecture up", not as feature list.

### Provider Trap Selling Scenario

Polish IT consultancies that build RAG systems, white-label models, or fine-tune APIs for industrial clients legally become AI "providers" under EU AI Act Art. 25 — not deployers. Provider obligations include: full Annex IV technical documentation, conformity assessment, 6-month operational log retention, post-market monitoring plan. Most Polish consultancies are unaware of this reclassification. Compilore's citation trail + git_commit_hash + audit history = structural compliance with Art. 12 (log-keeping) and Art. 14 (human oversight). Pitch: "Your RAG built for a client makes you a regulated AI provider in August 2026. Compilore is your compliance infrastructure — costs 94% less than manual QMS setup."

### Sales Narrative — Primary + Amplifier

**Primary pitch (always lead with this):** "Your technical advisors spend 
35% of their time being a human search engine. Compilore eliminates that. 
ROI: advisor costs €2,950/mo gross; 35% waste = €1,000+/mo drain per 
person. Team tier at 1,500 PLN/mo for 5 advisors = 5x ROI minimum."

This is quantifiable, falsifiable, and the Polish SME owner can calculate 
it in 30 seconds. This wins.

**Three validated purchase triggers (ranked by frequency in Polish SME distribution):**
1. **Onboarding acceleration** — new employee needs 4 months to reach
   productivity; owner realizes they cannot absorb this lag. Compilore
   compresses to 2 weeks. Trigger: recent hire or upcoming hire planned.
2. **Specification error prevention** — one wrong quote cost the firm a
   client or required expensive rework. 1% error rate on technical specs
   = catastrophic downstream liability. Trigger: recent painful error.
3. **Senior advisor capacity cap** — best engineer spending 30% of day
   answering basic catalog questions from juniors. Owner sees revenue cap.
   Trigger: visible bottleneck in quote turnaround time.

Note: succession risk (key person leaving) is a secondary amplifier,
not a primary trigger — per D-87.
Source: DR-19

**Secondary amplifier (use in specific scenarios):** institutional 
knowledge succession risk. Per 2026 external research (Polish SME buying 
triggers, Raport 1), 56% of Polish SMEs rank retention as #1 five-year 
challenge (69% in manufacturing). When a senior advisor exits, firm loses 
unwritten SOPs permanently. Compilore's compile-to-Wiki mechanism captures 
this knowledge before exit. Do NOT lead with this — it is hypothetical 
for most buyers and loses to quantified time-savings. Deploy in:
- Owner-approaching-retirement scenarios (generational transition)
- Post-departure "wounded prospect" conversations  
- Second-meeting conversations with CFO/owner after time-savings 
  established interest

### Messaging by Segment

- **B2B Distribution:** "Eliminate the 35% of advisor time lost to manual catalog search"
- **Accounting firms (biura rachunkowe):** "Prove where your responsibility ends — documented, cited, timestamped"
- **Consulting firms:** "One audit crisis costs PLN 44,800. Compilore costs PLN 3,500/msc."
- **Automotive supply chain:** "48-hour Stellantis window. Be ready in 2 hours, not 64."

## Long-Term Product Vision: From Access to Synthesis

Compilore's long-term trajectory follows a four-phase evolution:

**Phase 1 (current):** Static corpus, manual ingest, B2B PL technical distributors.
Core loop: ingest PDF artifacts -> compile -> query with citations.
Validation gate: Wojtek pilot success metrics (`09_PILOT.md`).

**Phase 2 (10+ paying clients):** Live ingest via n8n connectors (Slack, email, ERP webhooks),
freshness-aware confidence decay (page_type-aware per D-97), first conflict signals observed
in production data.

**Phase 3 (25+ paying clients):** Synthesis layer - conflict resolution between sources,
identity resolution (same entity across fragmented mentions), source authority hierarchy
(contract > CRM > Slack), continuously updated company worldview.
Target: "Company Brain for SME" - solving the synthesis problem at SME scale, not enterprise.

**Phase 4:** Executable layer - AI agents operate autonomously on the knowledge base.

**Competitive frame vs. Company Brain players (Hyperspell, Glean, Notion AI):**
They solve the synthesis problem for companies drowning in digital exhaust (Slack-heavy,
VC-backed, English-speaking, 50-200 person startups). We solve the access problem first
for companies whose knowledge is locked in analog artifacts - PDFs, phone calls, human memory -
then grow into synthesis as we accumulate production data and client understanding.
Different market entry, different physics, same destination.

**Why vertical synthesis beats horizontal synthesis:**
Compilore will never attempt horizontal synthesis (any company, any stack). That is Glean's
fight with 100x more resources. Compilore's synthesis layer will be vertical-specific:
known source types (Comarch Optima, manufacturer PDFs, B2B email), known conflict patterns,
hardcoded authority hierarchy for technical B2B distribution. Depth beats breadth.

**Architectural note:** Several Phase 3 foundations are already laid:
- authority_tier column in documents table -> source authority hierarchy
- page_type-aware confidence decay (D-97) -> freshness tracking
- Persistent wiki as knowledge store -> synthesis target
- Multi-tenant isolation (D-96) -> hermetic per-client worldview

## Three-Track AI Act Revenue Strategy

**Track C — Regulatory Intelligence API (launch first, Q3 2026)**  
Machine-readable Polish AI Act change data via API. Target: international GRC platforms (Vanta, Drata), law firms, enterprise compliance teams lacking Polish coverage. Price: $1,000-3,000 USD/msc. Pipeline: n8n + EUR-Lex ELI + Ministerstwo Cyfryzacji BIP + UODO scraper. Build cost: 4-6 weeks. Precedent: Clausematch, Archer.

**Track B — AI Act Content Portal (launch parallel, Q3 2026)**  
Weekly "AI Compliance Signals" digest + programmatic SEO for Art. 25 / KRiBSI / Annex III queries. Model: GDPR.pl (Omni Modo) — survive post-enforcement cliff by pivoting to operational tools + training + white-label. Content formats: interactive Art. 25 reclassification decision tree, fine calculator, Art. 25 self-assessment checklist. Authority signal: visible partnership with PTI AWSI certified auditor.

**Track A — Compilore as AI Act compliance infrastructure (activate Q4 2026+)**  
Target: Polish IT consultancies 20-100 employees building AI for clients. Sales trigger: NOT direct KRiBSI fear (10% probability) but enterprise client downstream pressure (65% scenario). Framing: "Your enterprise clients will require AI governance proof. We are the infrastructure." Sales cycle: 90-180 days. PARP Ścieżka SMART eligible (Sekcja J/M, up to 75% co-financing).

**Priority sequence: C → B → A. Do not reverse.**

---

## Adjacent Verticals

B2B technical distribution verticals share identical document structure — 
new vertical = new adapter, not new core engine.

### Phase 2 secondary (evaluated post-HermesTools proof point)

| Vertical | Adapter needed | Entry strategy | ARPU potential |
|---|---|---|---|
| Medical devices | `adapters/medical_device/` | DEFERRED — requires design partner; no cold entry. See D-86. | High |
| Chemical / food ingredients | `adapters/chemical/` | DEFERRED — same constraint as medical (D-86). Regulatory push (CLP Delegated Act deadline Nov 1, 2026) noted but not actionable without insider champion. | High |

**Rationale for deferral:** Both verticals have strong regulatory 
tailwinds (MDR 2026-2028 phased deadlines; REACH/CLP Nov 2026 
classification update). But Compilore has zero existing relationships, 
zero POLMED membership, zero compliance credibility in these sectors. 
Building adapter without design partner produces generic, unusable output. 
Acqui-hire of regulatory affairs partner rejected (no budget for equity 
dilution). Re-evaluate after HermesTools pilot produces case study + 
Compilore reaches 3+ paying clients in primary beachhead.

### Phase 3+ verticals (deferred)

| Vertical | Adapter needed | Signal |
|---|---|---|
| Automotive spare parts | `adapters/automotive/` | Thin margins, medium ARPU |
| Tax advisory (biura rachunkowe) | `adapters/tax_law/` | GapRoll distribution channel |
| Legal firms | `adapters/legal/` | Similar doc structure to technical catalogs |
| Environmental consultants | `adapters/environmental/` | — |

HVAC + Electrical + Industrial Assembly Tools (HermesTools) are Phase 2 
beachhead. Medical + Chemical are Phase 2 secondary, deferred until 
primary proof point lands.

**Pending Deep Research (scheduled):**
- DR-8: B2B distribution SaaS pricing & team model mechanics
- DR-9: Polish B2B distribution buyer journey & procurement (who signs PO, how long)
- DR-10: Competitive landscape — catalog search tools in HVAC/electrical distribution

---

## Team Model — Open Architecture Questions

These must be resolved before first corporate client onboarding:

| Question | Impact | Status |
|---|---|---|
| `organization_id` as hard DB boundary | Data isolation between firms — CRITICAL | 🔲 Not yet implemented |
| Admin panel for org manager | User management, upload oversight, billing view | 🔲 Deferred to Phase 2 |
| Data ownership on employee exit | Wiki stays with org, not user — must be in ToS | 🔲 Legal / ToS |
| Multi-language corpus (PL/EN/DE catalogs) | Mixed language in single org Wiki | 🔲 Test with Wojtek |
| Bulk upload + concierge onboarding | Low-tech users won't self-onboard 300 PDFs via drag-and-drop | 🔲 Phase 2 consideration |

---

## Key Risks

**AI Act enforcement note (SME IT segment):** KRiBSI operational capacity constraint: projected 70 employees, 27M PLN annual budget by 2027. Direct SME enforcement probability: 10%. Primary demand trigger for SME IT segment: downstream compliance pressure from enterprise clients, not direct KRiBSI audits. Same mechanism as Stellantis→Tier 1/2 in automotive. Sales framing must reflect this.

| Risk | Impact | Mitigation |
|---|---|---|
| Hallucination amplification | Wrong info cascades through Wiki | Gatekeeper + confidence decay + git version control |
| Knowledge rot | Stale pages served confidently | Confidence decay (-5%/mo) + event-driven recompilation + quarterly audit |
| State space explosion | Output pages drown source pages | Page ratio monitoring (max 20%) + auto-pruning |
| INDEX.md scaling | Model can't navigate >5000 pages | Hierarchical indexes at 2000+; hybrid search as primary routing |
| Semantic drift / Model Collapse | Wiki diverges from reality over 6 months | Git diffing, quarterly baseline audit, human review triggers |
| VLM cost explosion (Phase 2) | Margin death on MPZP processing | Docling as default ($0), VLM only for scans/maps (~20-30% of pages) |
| RODO / data privacy (Phase 2) | Legal exposure sending docs to US API | PII stripping + ZDR endpoints + tiered sensitivity routing |
| Trade secret invalidation (Phase 2) | Clients legally can't use the tool | DPA + ZDR + "Tajemnica Przedsiębiorstwa" toggle |
| AI hallucination liability (Phase 2) | Architect builds on wrong parameter | Art. 473 KC liability cap + mandatory verification clause + citations in every answer |
| Platform risk (Anthropic/OpenAI builds this) | Commoditization | Vertical depth (Polish MPZP), proprietary compiled data, workflow lock-in, regulatory moat |
| Docling RAM crash (Phase 2) | OOM on Hetzner | OMP_NUM_THREADS=1, page-by-page, gc.collect(), OCR offload to VLM API |
| OnGeo pivot | OnGeo lub AnalizaChlonnosci.AI dodaje OUZ Predictor | Buduj brand + case studies + Harvey-style partnership zanim to zrobią |
| Licencja zawodowa | Wysoki — nieadresowany: system interpretowany jako „opinia urbanistyczna” wymagająca uprawnień architekta/urbanisty | UI disclaimer mandatory + konsultacja prawna przed launch |
| EGiB data staleness | Średni — zarządzalny: budynki w EGiB opóźnione 6–18 msc → błędny wynik OUZ | Timestamp widoczny dla użytkownika + ostrzeżenie >180 dni |
| GML data quality | Wysoki — pewny: 20–40%+ wadliwych plików GML w pierwszej fali | Pipeline defensywny: ST_MakeValid() + logowanie + fallback |
| API availability | Wysoki — prawdopodobny: Rejestr Urbanistyczny nie gotowy przed sierpniem 2026 | Trzy źródła danych z failover (D-47) |

---

## GapRoll Synergies

| GapRoll Asset | Compilore Use |
|---|---|---|
| Hetzner VPS + Coolify | Shared hosting infrastructure |
| n8n VPS (37.27.14.41) | Workflow orchestration for all loops |
| Viktor.ai (Slack) | Phase 1 interface |
| Cloudflare | DNS |
| LangGraph expertise | Agent framework for all 4 loops |
| PostgresSaver pattern | Proven checkpointing for LangGraph |
| Supabase RLS patterns | Multi-tenant isolation |
| LangSmith | Token cost monitoring |
| Instantly.ai | Phase 2 architect outreach sequences |
| Biura rachunkowe network | Phase 2 referral distribution |
| LinkedIn "Build in Public" | Dual content: GapRoll PH + Compilore validation |

---

## Legal Requirements (Phase 2, before first paying client)

- [ ] ZDR application to OpenAI (start early — approval takes weeks)
- [ ] DPA (Umowa Powierzenia Przetwarzania Danych) — with lawyer
- [ ] DPIA (Ocena Skutków dla Ochrony Danych) — internal, documenting all data flows
- [ ] Regulamin Świadczenia Usług — with Art. 473 KC liability cap (12 months subscription)
- [ ] Privacy Policy (Polityka Prywatności)
- [ ] OC Zawodowe IT insurance (1–3M PLN, covering AI hallucinations + data breach)
- [ ] Landing page trust signals: "Twoje dane nie trenują AI" + "100% danych w UE" + "Tajemnica Przedsiębiorstwa" toggle

**DPA is a feature, not a checkbox.** Show it from the first contact with any prospect.
Architects are trained to protect client confidentiality. This is a conversion lever.
