"""Compilore FastAPI application entrypoint.

HTTP surface stays thin: business logic and agents live under ``src/modules/`` and
``src/graphs/``. See ``COMPILORE_PROJECT_BRIEF_v2.md`` for the four-loop design.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, HttpUrl
from starlette.concurrency import run_in_threadpool

from src.graphs.ingest_compile_graph import run_ingest_compile, run_ingest_compile_from_url
from src.graphs.query_graph import run_query
from src.modules.compile.models import WikiPage
from src.modules.query.models import QueryResult

app = FastAPI(
    title="Compilore",
    description="Agentic Knowledge Compiler — Ingest, Compile, Query, Lint",
    version="0.1.0",
)

# Phase 1: open CORS for static UI + mobile browsers; tighten origins in Phase 2.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

_ALLOWED_UPLOAD_SUFFIXES = frozenset({".md", ".txt", ".pdf"})

_STATIC_DIR = Path(__file__).resolve().parent / "static"


class HealthResponse(BaseModel):
    """Service liveness payload for orchestrators and load balancers."""

    status: str = Field(description="Application health indicator")


class IngestUrlRequest(BaseModel):
    """JSON body for URL-based ingest."""

    url: HttpUrl


class QueryRequest(BaseModel):
    """JSON body for Wiki-grounded Q&A."""

    question: str = Field(min_length=1)


def _playground_tenant_id() -> str:
    tid = os.environ.get("COMPILORE_DEFAULT_TENANT_ID", "").strip()
    if not tid:
        raise HTTPException(
            status_code=500,
            detail="COMPILORE_DEFAULT_TENANT_ID is not configured.",
        )
    return tid


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Liveness probe; no dependency checks in Phase 0 scaffold."""
    return HealthResponse(status="ok")


@app.get("/")
async def serve_ui() -> FileResponse:
    """Minimal HTML playground (Phase 1 — Viktor/Slack alternative for local use)."""
    index = _STATIC_DIR / "index.html"
    if not index.is_file():
        raise HTTPException(status_code=404, detail="UI not found (missing static/index.html)")
    return FileResponse(index, media_type="text/html; charset=utf-8")


app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")


@app.post("/ingest", response_model=list[WikiPage])
async def ingest_document(file: UploadFile = File(...)) -> list[WikiPage]:
    """Upload Markdown, plain text, or native-digital PDF; run ingest→compile graph."""
    filename = file.filename or "upload"
    suffix = Path(filename).suffix.lower()
    if suffix not in _ALLOWED_UPLOAD_SUFFIXES:
        raise HTTPException(
            status_code=400,
            detail="Supported uploads: .md, .txt, .pdf",
        )
    tenant_id = _playground_tenant_id()

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp_path = Path(tmp.name)
    try:
        body = await file.read()
        tmp.write(body)
        tmp.flush()
        tmp.close()
        pages, err = await run_in_threadpool(
            run_ingest_compile,
            temp_path=tmp_path,
            original_filename=filename,
            tenant_id=tenant_id,
        )
    finally:
        tmp_path.unlink(missing_ok=True)

    if err:
        raise HTTPException(status_code=502, detail=err)
    return pages


@app.post("/ingest/url", response_model=list[WikiPage])
async def ingest_url(body: IngestUrlRequest) -> list[WikiPage]:
    """Ingest a web article by URL (trafilatura); same compile graph as file upload."""
    tenant_id = _playground_tenant_id()
    pages, err = await run_in_threadpool(
        run_ingest_compile_from_url,
        url=str(body.url),
        tenant_id=tenant_id,
    )
    if err:
        raise HTTPException(status_code=502, detail=err)
    return pages


@app.post("/query", response_model=QueryResult)
async def query_wiki(body: QueryRequest) -> QueryResult:
    """Ask a question against the compiled Wiki (hybrid search + synthesis + gatekeeper)."""
    tenant_id = _playground_tenant_id()
    result, err = await run_in_threadpool(run_query, body.question, tenant_id)
    if err or result is None:
        raise HTTPException(status_code=502, detail=err or "Query produced no result")
    return result
