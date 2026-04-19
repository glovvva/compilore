# 02 — STRATEGY
## Compilore: Market, GTM, Pricing, Risks

**Last updated:** 2026-04-19

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
| Chemical & Food Ingredients | Product Specialist, Formulation Advisor | 16–18h | 1,200–2,500 PLN/msc | Secondary |
| Automotive Spare Parts | Parts Advisor, Technical Counterperson | 10–12h | 400–800 PLN/msc | Tertiary |

**HVAC + Electrical = first two verticals.** Identical document structure (parametric PDFs, engineering tables, multi-language catalogs). Wojtek's vertical is the entry point.

---

## Distribution (Phase 2)

### GTM reality for Polish B2B distribution sector

This market does NOT respond to LinkedIn-first, build-in-public, or standard SaaS marketing. Trust is built physically and through industry-specific channels.

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

**Deferred pricing consideration (activation trigger: pilot success + D-85 activation):** Research indicates that audit-deadline-driven positioning (48h Stellantis response, 15-year VW D/TLD retention, IATF 16949 retention compounding) may support a premium tier priced as "compliance insurance" rather than productivity tooling. Early estimate 3,500–8,000 PLN/mo for organizations with material OEM audit exposure. Do not introduce this tier before 8-week pilot validation of core catalog search + audit-bundle test question. See D-85 and 10_GRANTS.md Option D.

**ROI framing for sales:** Technical advisor costs ~€2,950/msc gross. 35% of time wasted = €1,000+/msc drain per person. Team tier at 1,500 PLN/msc for 5 advisors = 5x ROI minimum. Pitch: cost of the tool < cost of one hour of the problem per week.

**Trial:** 14-day free trial per organization (not per user). Pilot users (like Wojtek) = extended manual pilot tracked separately.

---

## Competitive Positioning

**Frame:** "Your technical advisors spend 35% of their time being a human search engine. Compilore eliminates that."

**Not competing with:** ERP systems (Comarch, Asseco) — we integrate alongside them, not replace them. Buyer anchors our price against ERP/WMS cost (~$100–500/user/msc) — we fit inside that range.

**Competing against:** Excel spreadsheets, CTRL+F in PDFs, phone calls to manufacturer reps, human memory and experience.

**Moat:** Compiled organizational Wiki. After 3 months of use, a firm has a proprietary, structured knowledge base of every manufacturer catalog they work with. New employee onboarding = query the Wiki instead of sitting next to a senior advisor for a year. Churn = losing that institutional memory. Data lock-in is a feature, framed as "your firm's technical memory."

**Trust mechanism:** Every answer must include exact source citation (document name + page number). No citation = answer not shown. This is non-negotiable in this sector — one wrong recommendation = structural failure, chemical hazard, or MDR violation. Citation trail is the product, not a UX nicety. For automotive and aerospace clients specifically, citation trail is not just a trust mechanism — it is the legal artifact needed to satisfy IATF 16949 clause 7.5.3.2.1 retention obligations and VW Formel Q D/TLD 15-year archival requirements. Every Compilore answer with full citation trail is, by construction, audit-ready. This is a structural competitive advantage over proprietary vendor silos (ToolsTalk 2, VPG+) which do not natively produce human-readable cited artifacts. (See DR-14 RESULTS in 08_RESEARCH.md for regulatory detail.)

---

## Adjacent Verticals (Phase 3+)

B2B technical distribution verticals share identical document structure — new vertical = new adapter, not new core engine.

| Vertical | Adapter needed | Entry signal | ARPU potential |
|---|---|---|---|
| Medical devices | `adapters/medical_device/` | POLMED association | High (regulatory complexity) |
| Chemical / food ingredients | `adapters/chemical/` | — | High (REACH/ECHA compliance) |
| Automotive spare parts | `adapters/automotive/` | — | Medium (thin margins) |
| Tax advisory (biura rachunkowe) | `adapters/tax_law/` | GapRoll distribution channel | Medium |
| Legal firms | `adapters/legal/` | Similar document structure | Medium |
| Environmental consultants | `adapters/environmental/` | — | Low/medium |

HVAC + Electrical are Phase 2 beachhead. Medical + Chemical are Phase 3 (higher regulatory complexity, longer sales cycle, higher ARPU).

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
