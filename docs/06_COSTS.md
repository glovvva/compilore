# 06 — COSTS
## Compilore: Cost Model, LLM Routing, Estimates

**Last updated:** 2026-04-11

---

## Key Insight

The original brief estimated $30–40/month for personal use. This was calibrated
for MPZP-scale documents (50K+ tokens each). For personal use with articles,
YouTube transcripts, and Instagram Reels, the real cost is **$2–8/month** —
depending on LLM routing strategy.

---

## LLM Routing — Three Configurations

### Config A — All API (Current, as built)
Every operation uses Anthropic/OpenAI APIs.

| Operation | Model | Cost per operation |
|---|---|---|
| Compile | Claude 3.7 Sonnet | ~$0.07/doc (article avg) |
| Query synthesis | Claude 3.7 Sonnet | ~$0.012/query |
| Gatekeeper | Claude Haiku 4.5 | ~$0.002/query |
| Embeddings | text-embedding-3-small | ~$0.001/doc |
| **Monthly (50 docs, 200 queries)** | | **~$10–14** |

### Config B — Hybrid (Recommended — after Gemma 4 local setup)
Compile stays on Sonnet (quality permanent). Everything else → local Gemma 4 31B.

| Operation | Model | Cost per operation |
|---|---|---|
| Compile | Claude 3.7 Sonnet | ~$0.07/doc |
| Query synthesis | Gemma 4 31B Dense (local) | ~$0 |
| Gatekeeper | Gemma 4 31B Dense (local) | ~$0 |
| Embeddings | text-embedding-3-small | ~$0.001/doc |
| **Monthly (50 docs, 200 queries)** | | **~$3.60** |

### Config C — Fully Local (For private/sensitive use)
All operations local. Lower quality on compile.

| Operation | Model | Cost per operation |
|---|---|---|
| All | Gemma 4 31B Dense (local) | ~$0 |
| Embeddings | text-embedding-3-small | ~$0.001/doc |
| **Monthly (50 docs, 200 queries)** | | **~$0.05** |

**Recommendation:** Config B. Compile quality is permanent and worth $0.07/doc.
Query responses are ephemeral — local is fine.

---

## Cost per Operation — Detailed Breakdown

### Compile (Claude 3.7 Sonnet)

Pricing: $3.00/MTok input, $15.00/MTok output

| Document type | Input tokens | Output tokens | Cost |
|---|---|---|---|
| Short article (1,500 words) | 4K | 2K | **$0.042** |
| Medium article (3,000 words) | 6K | 3K | **$0.063** |
| YouTube 30-min transcript | 10K | 4K | **$0.090** |
| YouTube 2-hour transcript | 25K | 6K | **$0.165** |
| Research paper (10-20 pages) | 15K | 5K | **$0.120** |
| Instagram Reel transcript | 2K | 1.5K | **$0.028** |
| Pasted text snippet | 2K | 1.5K | **$0.028** |
| MPZP document (Phase 2) | 50K | 15K | **$0.375** |

### Query (Config B — Gemma 4 local)

| Component | Cost |
|---|---|
| Embedding query | ~$0.0001 |
| Gemma 4 synthesis (local) | ~$0 |
| Gatekeeper (local) | ~$0 |
| If answer saved — embed new output page | ~$0.0001 |
| **Total per query** | **~$0.0002** |

### Lint (on-demand, Claude Sonnet)
~$0.40/run (full contradiction check on medium-size Wiki).
Orphan detection and stale detection = $0 (RegEx + date comparison).

### Embeddings (OpenAI text-embedding-3-small)
$0.020/MTok → ~$0.001 per average document, ~$0.0001 per query.

---

## Monthly Cost Estimates

### Bartek personal use — mixed sources
50 articles/transcripts + 200 queries/month

| Config | Monthly cost |
|---|---|
| All API | ~$12 |
| Hybrid (recommended) | **~$4** |
| Fully local | ~$0.05 |

### Beta tester (friend/żona) — light use
20 documents + 50 queries/month

| Config | Monthly cost |
|---|---|
| All API | ~$4 |
| Hybrid | **~$1.50** |

### Phase 2 client — MPZP heavy use
50 MPZP documents + 500 queries/month

| Config | Monthly cost |
|---|---|
| All API (Sonnet compile + Haiku query) | ~$25–30 |
| Hybrid | **~$22** |
| At Phase 2 pricing (200 PLN/mo Starter) | Margin: ~60–70% |

---

## Infrastructure Costs

| Item | Cost | Notes |
|---|---|---|
| Hetzner VPS (shared with GapRoll) | €0 incremental | Already running |
| Supabase (free tier) | €0 | Up to 500MB DB, 1GB storage |
| Supabase Pro (when needed) | $25/mo | At ~100+ users |
| n8n self-hosted | €0 | On existing VPS |
| LangSmith | $0 (free tier) | Up to 5K traces/month |
| Gemma 4 31B (local) | ~$0.0007/article in electricity | M3 Max |

**Total infrastructure: €0 incremental for Phase 1**

---

## Cost Anomalies to Watch

### 1. Lint loop budget creep
Each full lint (contradiction check) costs ~$0.40. Never run autonomously.
n8n: gate lint triggers behind manual approval or weekly schedule + cost alert.

### 2. Output page accumulation
Output pages saved by Gatekeeper cost to embed. If output pages exceed 25% of Wiki,
auto-archive lowest-confidence ones. Page ratio monitored by `token_tracker.py`.

### 3. Long document compile
A 100K-token document (large MPZP, book chapter) costs ~$0.75 to compile. For Phase 1
personal use, this is unlikely. Monitor `wiki_log` for outlier compile costs.

### 4. Gatekeeper hallucination check
Pre-check requires one embedding (~$0.0001). This is negligible. Do not skip it to
save money — the cost of duplicate output pages over time is much higher.

---

## Phase 2 Pricing Model

Usage-based. NOT flat-rate.

| Tier | Price (PLN/mo) | Margin at current costs |
|---|---|---|
| Starter: 20 docs, 200 queries | ~200 | ~65% |
| Professional: 100 docs, unlimited queries | ~600 | ~70% |
| Enterprise: unlimited, daily Lint, API | 2,500+ | negotiate per usage |

Value metric: documents processed + Wiki size.
Per-seat pricing = wrong metric. Knowledge compounds across the team.

---

## Cost Monitoring

Every API operation logs to `wiki_log` table:
```sql
operation TEXT,     -- ingest | compile | query | lint | gatekeeper | decay
tokens_used INT,
cost_usd NUMERIC(10,6)
```

`token_tracker.py` aggregates:
- Daily/weekly/monthly spend by operation type
- Page ratio (concept/entity/output/source)
- Alert if output pages > 25%
- Weekly Slack report (planned Sprint 3)
