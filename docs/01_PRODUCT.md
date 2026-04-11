# 01 — PRODUCT
## Compilore: Agentic Knowledge Compiler

**Last updated:** 2026-04-11
**Status:** Phase 1 — Personal Playground (live, running locally)

---

## What Compilore Is

Compilore is an **Agentic Knowledge Compiler**. It transforms unstructured documents
into a living, self-maintaining Markdown Wiki that compounds knowledge with every
document ingested and every question asked.

**The core distinction — it is NOT standard RAG:**

| Standard RAG | Compilore |
|---|---|
| Re-discovers knowledge from scratch on every query | Compiles knowledge once into persistent structured Wiki pages |
| Amnesia — no memory between queries | Compounds — every query can add to the Wiki |
| Flat chunks in a vector DB | Interconnected concept/entity pages with cross-references |
| Search engine | Research librarian maintaining a Wiki |

Inspired by Andrej Karpathy's "LLM Knowledge Base" concept (April 2026) and
@hooeem's implementation guide.

---

## The 4 Loops

These are the only four operations the system performs. Everything else is
infrastructure serving these loops.

### Loop 1 — Ingest
**Trigger:** Document uploaded (URL, file, pasted text)
**Action:** Extract clean text from source. No LLM involved.
**Output:** Raw text stored in `documents` table, status = `ingested`

### Loop 2 — Compile
**Trigger:** After successful Ingest
**Action:** Claude Sonnet reads source text → generates structured Markdown Wiki pages:
- `source_summary` — one page per source document
- `concept` pages — key ideas, definitions, frameworks extracted
- `entity` pages — people, organizations, tools mentioned
- Updates `INDEX.md` with new cross-references
- Every compilation = atomic `git commit` in `wiki/`

**Output:** Wiki pages in Supabase (`wiki_pages` table) + Markdown files in `wiki/` + git commit

### Loop 3 — Query
**Trigger:** User asks a question
**Action:**
1. Embed question → hybrid search (pgvector cosine + BM25 RRF) against `document_chunks`
2. Claude synthesizes answer with `[[wikilink]]` citations
3. **Gatekeeper** evaluates answer on 3 criteria:
   - **Novelty** — does this synthesize something not already in concept pages?
   - **Necessity** — is this reusable globally, or hyper-specific/transient?
   - **Grounding** — are citations valid? Logic derived from sources, not hallucinated?
4. If all three pass → save to `wiki/outputs/` as new Wiki page + git commit
5. If any fail → serve answer, discard

**Gatekeeper pre-check (added 2026-04-09):** Before novelty evaluation, run
`hybrid_search` with the answer as query. If cosine similarity > 0.85 with an
existing page, Gatekeeper receives context "this knowledge already exists at [[X]]"
and can refuse to save. Cost: one additional embedding call (~$0.001).

**Output:** Answer with citations to user + optional new Wiki output page

### Loop 4 — Lint
**Trigger:** ON-DEMAND ONLY. Never autonomous background. Never scheduled without human intent.
**Action:** Audit Wiki for:
- Orphan pages (broken `[[wikilinks]]`) — RegEx, $0
- Stale pages (not updated > 30 days) — date comparison
- Contradictions between pages — Claude-powered, structured JSON output
- Duplicate pages (cosine similarity > 0.92 → suggest merge)

**HITL:** `interrupt_before` on contradiction resolution — human decides merge strategy.
Autonomous lint = "Agentic Loop of Death" = budget killer. This loop costs ~$0.40/run.

---

## Wiki Page Anatomy

Every compiled page follows this exact format:

```markdown
---
title: "Page Title"
date_created: 2026-04-11
date_modified: 2026-04-11
summary: "One sentence summary"
type: concept | entity | source_summary | output | index
status: draft | review | final | deprecated
confidence: 0.90
last_verified: 2026-04-11
git_commit_hash: "abc123def"
sources:
  - doc_id: "uuid"
    reference: "Section 2, paragraph 3"
related:
  - "[[related-page-slug]]"
tags:
  - tag1
context_hierarchy: "Category > Subcategory > Topic"
---

# Page Title

Content here...

## Sources
- Source Name (doc: uuid)

## Related
- [[related-page-slug]]
```

`git_commit_hash` in frontmatter enables rollback: `git checkout <hash> -- wiki/page.md`
+ re-embed. Agent does not resolve merge conflicts — human receives Slack diff and decides.

---

## Confidence Decay System

Every Wiki page has a `confidence` score (0.0–1.0):

| Event | Effect |
|---|---|
| Initial (concept page) | 0.90 |
| Initial (output page) | 0.80 |
| Monthly without access | -0.05 |
| Cited in query, user doesn't flag | `last_verified` updates, confidence holds |
| Falls below 0.30 | Move to `wiki/archive/`, exclude from INDEX.md and retrieval |

Monthly cron via n8n → `confidence_decay.py`

---

## Page Ratio Monitoring

Wiki health is monitored by page type ratios:

| Type | Target | Alert threshold |
|---|---|---|
| Raw source summaries | 5% | — |
| Concept + entity pages | 75% | — |
| Output pages (saved answers) | max 20% | >25% triggers auto-pruning |

`token_tracker.py` monitors ratios. If outputs > 25% → Slack alert + auto-archive
lowest-confidence outputs first.

---

## INDEX.md Scaling Strategy

| Wiki size | Strategy |
|---|---|
| < 2,000 pages | Flat INDEX.md passed in context |
| 2,000–5,000 pages | Category-level indexes (`concepts/_index.md`, `entities/_index.md`) + hybrid search as primary routing |
| > 5,000 pages | Full hybrid search primary, INDEX.md = high-level overview only |

Current state: flat INDEX.md (well below threshold).

---

## What Compilore Is NOT

- Not a chatbot over PDFs (no amnesia model)
- Not an autonomous agent that runs unsupervised (all loops except Compile are human-triggered or gated)
- Not a replacement for primary sources — every answer must cite its source document
- Not a real-time system — Compile takes 20-40 seconds per document, which is acceptable

---

## Output Formats

### Standard Answer (Live)
Default response. Markdown with [[wikilink]] citations. Raw but functional.

### Response Card (Sprint 4 — high priority)
Replaces raw Markdown for all query responses. Implements F-pattern and atomic
interactivity principles:
- Conclusion-first headline (not "Answer to:")
- Source chips as inline badges
- Confidence delta ("↑ 0.70→0.85") not raw score
- "Save to Wiki" toggle in-card (atomic — no navigation round-trip)
- Progressive disclosure for secondary context
Status: planned Sprint 4

### Mind Map — /mindmap (Sprint 4)
LLM outputs nested Markdown headings. Markmap renders as interactive SVG.
Zero extra LLM cost. Zero extra logic beyond renderer.
Trigger: user writes "mindmap", "mapa myśli", "pokaż relacje" in query.
Status: planned Sprint 4

### Mermaid Graph — /graph (Sprint 4)
Entity/concept relationship visualization. LLM generates Mermaid flowchart syntax.
Use case: "jak połączone są te koncepcje?", "pokaż mi strukturę tej encji".
Status: planned Sprint 4

### Comparison Table (Sprint 4)
Auto-detect "compare X with Y" intent. Output structured HTML table.
Status: planned Sprint 4

### Presentation Deck — /deck (Phase 2)
Marp Markdown → PPTX/PDF. LLM generates Markdown with --- slide separators.
Architects get editable PowerPoint. NOT Slidev (Vue syntax = hallucination risk).
Status: Phase 2

### Summary Card — /card (Sprint 4)
Visual distillation: key claim, 3 bullets, confidence bar, source chips.
Status: planned Sprint 4

### Protocol Plan — /protocol (Phase 2)
Gated execution: EXPLAIN → PLAN → IMPLEMENT.
For compliance-sensitive document analysis (MPZP parameters, permit requirements).
Status: Phase 2
