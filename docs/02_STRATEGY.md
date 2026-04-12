# 02 — STRATEGY
## Compilore: Market, GTM, Pricing, Risks

**Last updated:** 2026-04-12

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

### GIS Spatial Engine — Segmenty (priorytet)

**Segment 1 — Deweloperzy MŚP (PRIMARY, pierwsze 12 msc):**

- **Definicja:** firmy realizujące 5–50 projektów/rok, budżety 10–200M PLN
- **Liczba:** kilkaset do 2,000+ aktywnych podmiotów w Polsce
- **Decision maker:** właściciel lub Land Acquisition Manager
- **Cykl sprzedaży:** 1–3 tygodnie po demo
- **ARPU:** 2,000–4,000 PLN/msc
- **Pain:** ryzyko zakupu działki wyrzuconej poza OUZ, opóźnienia 7–21 dni przy manualnej analizie, koszt 30,000–200,000 PLN due diligence per zakup gruntu
- **Pitch:** „Tarcza chroniąca 10M PLN przed błędnym zakupem”

**Segment 2 — Fundusze PE / Family Offices (SECONDARY, 6–18 msc):**

- **Definicja:** portfele 50–500+ działek, zarządzane przez fundusze
- **Liczba:** 2,112 fundacji rodzinnych + 34 fundusze VC/PE (Q1 2025)
- **Decision maker:** zarząd/rada nadzorcza (długi procurement)
- **Cykl sprzedaży:** 3–6 miesięcy
- **ARPU:** 6,000–10,000 PLN/msc (Conflict Alert jako główny feature)
- **Pain:** portfel land-bankowy narażony na systemowe ryzyko POG, niemożność monitorowania 2,479 gmin manualnie
- **Pitch:** „Radar portfela — alarmuje gdy POG deprecjonuje Twój bank ziemi”

**Segment 3 — Rzeczoznawcy majątkowi (TERTIARY, model transakcyjny):**

- **Definicja:** 7,591 certyfikowanych rzeczoznawców
- **Model:** Pay-Per-Report (nie subskrypcja), 1 credit = 1 operat
- **ARPU:** 500–1,500 PLN/msc lub per-query
- **Pain:** weryfikacja planistyczna w każdym operacie szacunkowym, chaos w „interregnum” POG vs stare MPZP

**Compilore (architekci / PKB tekstowy)** pozostaje produktem równoległym (vitamin / edukacja rynku); GIS Engine jest **painkillerem** priorytetowym według DR-7 i D-45.

---

## Distribution (Phase 2)

### Primary — biura rachunkowe (accounting firms)
Leveraging GapRoll network of accounting firms as referral partners.
- Revenue share: 20% recurring
- Pitch to accountant: "healthy client stays longer"
- Pre-existing trust relationship with target firm

### Secondary — direct to architects
- LinkedIn "Build in Public" content (dual-use: GapRoll PH + Compilore validation)
- Hyper-personalized Loom demos: record Compilore parsing a real MPZP from the
  prospect's municipality. 3 demos, measure response rate before scaling.
- IARP (Izba Architektów RP) — potential partnership / endorsement channel
- Instantly.ai for outreach sequences (already in GapRoll stack)

### Validation first (before any outreach at scale):
1. 15 interviews with architects; 7/10 must cite MPZP chaos as burning pain
2. Landing page: architects upload real MPZP to join waitlist. Target: 5-10 docs
3. Pre-sale: 2 Letters of Intent for paid pilot (~$250 archive compilation)
4. 1 public case study with the hardest MPZP in Poland — posted publicly, stronger
   signal than private uploads

---

## Pricing (Phase 2)

**Model:** Usage-based, NOT flat-rate. API costs are variable; flat-rate = bankruptcy.
**Value metric:** Documents processed + Wiki size. NOT per-seat.

| Tier | Price | Includes |
|---|---|---|
| Starter | ~200 PLN/mo | 20 docs/mo, 200 queries, no Lint |
| Professional | ~600 PLN/mo | 100 docs/mo, unlimited queries, weekly Lint |
| Enterprise | Custom 2,500+ PLN/mo | Unlimited, daily Lint, API |

**Payment stack:** Fakturownia + Przelewy24. Stripe is BANNED — no JPK_FA support.
Polish B2B strongly prefers bank transfer / BLIK over card.

---

## Competitive Positioning

**Frame:** "Geoportal gives you the raw map. Compilore gives you the legal analysis layer on top."
Geoportal-krajowy.pl is the #1 tool for architects in Poland. Compilore positions as
the intelligence layer above raw regulatory data, not a replacement.

**Moat:** Compiled proprietary knowledge base. The longer a firm uses Compilore, the
more their specific Wiki compounds and diverges from generic tools. Data lock-in is
a feature, not a bug — framed as "your firm's institutional memory."

**Future moat (Phase 3, not now):** Optional anonymized public pool for public MPZP
documents. Public MPZPs are public domain (RODO does not restrict). Aggregate compiled
knowledge across clients = network effect. Noted, not implemented.

---

## Adjacent Verticals (Phase 3+)

The Adapter Pattern in architecture means new industries require only new adapters,
not core engine changes:

| Vertical | Adapter needed | Existing signal |
|---|---|---|
| Tax advisory firms (biura rachunkowe) | `adapters/tax_law/` | GapRoll distribution channel |
| Legal firms | `adapters/legal/` | Similar document structure to MPZP |
| Environmental consultants | `adapters/environmental/` | — |

Tax advisory is highest-priority Phase 3 target — distribution channel already exists.

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
|---|---|
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
