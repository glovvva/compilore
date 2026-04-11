# docs/ — Compilore Project Documentation

This folder contains the living source of truth for the Compilore project.
All strategic, architectural, and research decisions are recorded here.

## Structure

| File | Contents | Update frequency |
|---|---|---|
| `01_PRODUCT.md` | What Compilore is, 4 loops, Wiki anatomy, confidence decay | Rare — product philosophy is stable |
| `02_STRATEGY.md` | Market, GTM, pricing, risks, legal requirements | Monthly — as strategy evolves |
| `03_ARCHITECTURE.md` | Tech stack, sacred rules, DB schema, module map | When architecture changes |
| `04_DECISIONS.md` | Log of every significant decision with rationale + date | Every decision |
| `05_INGESTION.md` | All adapters: status, method, cost, implementation notes | When new source added |
| `06_COSTS.md` | Cost model, LLM routing configs, monthly estimates | When models/pricing change |
| `07_SPRINTS.md` | Sprint status, what's done, what's next, backlog | Weekly during active development |
| `08_RESEARCH.md` | Deep Research session findings and implications | After each DR session |

## How to Use With Cursor

Reference these files in Cursor Composer with `@docs/filename.md`.

For architecture questions: `@docs/03_ARCHITECTURE.md`
For "why did we do X": `@docs/04_DECISIONS.md`
For sprint status: `@docs/07_SPRINTS.md`

## Update Protocol

When something changes in a chat session with Claude:
1. Claude prepares a Cursor Composer prompt at the end of the session
2. Paste the prompt into Cursor Composer (Agent mode)
3. Cursor updates the relevant file(s)
4. Commit the change: `git add docs/ && git commit -m "docs: update [topic]"`

**Never edit these files manually unless you're certain of the change.**
Use the Claude → Cursor Composer → commit pipeline to keep everything consistent.
