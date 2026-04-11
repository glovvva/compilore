# Compilore

**Agentic Knowledge Compiler** — turns unstructured text and Markdown into a **Git-versioned Markdown Wiki** backed by Supabase (PostgreSQL + pgvector), with retrieval and synthesis that **compound** over time instead of behaving like stateless “chat over PDFs.”

The architecture follows **Karpathy’s four-loop pattern** (see project brief):

| Loop | Role |
|------|------|
| **Ingest** | Read uploads; adapters normalize text (Phase 1: Markdown, plain text; optional native-digital PDF text via PyMuPDF). |
| **Compile** | LLM builds and updates Wiki pages, cross-links, and the master index; embeddings and DB rows follow. |
| **Query** | Hybrid search → synthesis with citations → **Gatekeeper** decides whether to persist to `wiki/outputs/`. |
| **Lint** | On-demand audits: orphans, staleness, dedup signals, contradictions (no tight autonomous agent loop). |

**Phase 1** (current): personal playground — **text and Markdown only** (no scans, no VLM). **Phase 2** (deferred): industry adapters under `src/modules/adapters/architect/`.

Authoritative decisions, schema, cost model, and sprint plan: [`COMPILORE_PROJECT_BRIEF_v2.md`](COMPILORE_PROJECT_BRIEF_v2.md).

## Repository layout

- `src/modules/` — business logic: `ingest/`, `compile/`, `query/`, `lint/`, `adapters/`
- `src/lib/` — Supabase, Anthropic, OpenAI, token tracking
- `src/graphs/` — LangGraph definitions for the three orchestrated pipelines
- `src/config/prompts/` — versioned `.md` system prompts (loaded by code, not duplicated as giant strings)
- `wiki/` — **nested Git repository** (its own `.git`); `index.md`, `log.md`, and folders `concepts/`, `entities/`, `sources/`, `outputs/`. If this folder lives inside another Git repo, treat the nested layout deliberately (e.g. submodule or documented ignore rules) so the outer project and `wiki/` do not fight over history.
- `.cursor/rules/compilore.mdc` — Cursor rules for this codebase

**Rule:** every Wiki write is an **atomic Git commit**.

## Quick start (scaffold)

Python **3.12+** recommended.

```bash
cd /path/to/Compilore
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
PYTHONPATH=. uvicorn src.main:app --reload
```

Health check: `GET /health` → `{"status":"ok"}`.

## Deployment (Docker + Coolify)

Stack target: **Hetzner VPS + Coolify** in the EU; **do not** deploy on Vercel (brief §2 / §3.3).

### Image

- `Dockerfile`: **Python 3.11-slim**, installs deps from `requirements.txt`, copies `src/`, `wiki/`, `scripts/`. **No `.env` or API keys** are copied (see `.dockerignore`).
- Wiki Git identity inside the container: `compilore@docker.local` / `Compilore` (local `wiki/.git/config` on start). Override by mounting a preconfigured `wiki/` volume.
- Keep the image lean: expect **well under 500MB** with `python:3.11-slim` + pip installs; verify with `docker images`.

### Local Docker Compose

```bash
cp .env.example .env   # fill in keys + COMPILORE_DEFAULT_TENANT_ID + SUPABASE_DB_URL as needed
docker compose up --build
```

- **`./wiki:/app/wiki`** persists the nested Git wiki across restarts (empty host dir gets `git init` on first container start).
- Health probe helper: `scripts/healthcheck.sh` (expects `curl` and the API on port 8000).

### Coolify

1. Create a **Docker Compose** or **Dockerfile** resource pointing at this repository (same layout as `docker-compose.yml` / root `Dockerfile`).
2. In Coolify **Environment**, set variables from `.env.example` (Supabase URL + service role key, `COMPILORE_DEFAULT_TENANT_ID`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc.). **Do not** bake secrets into the image.
3. Attach a **persistent volume** mounted at **`/app/wiki`** so compiles, query outputs, and `log.md` survive redeploys (matches compose).
4. Expose **port 8000** (or map reverse proxy → 8000). CORS is currently **allow all origins** for Phase 1; restrict `allow_origins` in `src/main.py` for Phase 2 / production.
5. Optional health check: HTTP GET `/health` or `curl -sf http://127.0.0.1:8000/health` inside the container.

### SQL migrations

Apply `sql/001_initial_schema.sql`, then `002_hybrid_search_with_tenant.sql`, then `sql/003_seed_tenant.sql` in Supabase before relying on ingest/query.

## Status

Phase 1 playground: ingest, compile (with chunk embeddings), query + gatekeeper, minimal static UI — see sprint notes in the project brief.
