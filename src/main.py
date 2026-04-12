"""Compilore FastAPI application entrypoint.

HTTP surface stays thin: business logic and agents live under ``src/modules/`` and
``src/graphs/``. See ``COMPILORE_PROJECT_BRIEF_v2.md`` for the four-loop design.
"""

from __future__ import annotations

import json
import logging
import os
import tempfile
import time
from pathlib import Path
from typing import Any

from fastapi import BackgroundTasks, FastAPI, File, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field, HttpUrl
from starlette.concurrency import run_in_threadpool
from starlette.requests import Request
from starlette.responses import Response

from src.graphs.ingest_compile_graph import (
    run_ingest_compile,
    run_ingest_compile_from_paste,
    run_ingest_compile_from_url,
)
from src.graphs.lint_graph import resume_lint, run_decay, run_lint
from src.graphs.query_graph import run_query
from src.modules.compile.models import WikiPage
from src.modules.lint.report_history import fetch_last_lint_report
from src.lib.response import AIContext, APIResponse, envelop
from src.lib.auth import get_current_tenant_id
from fastapi import Depends

from src.modules.query.format_analytics import log_format_chip_click
from src.modules.query.models import QueryResponseCard
from src.modules.query.output_formatter import transform_answer_to_format

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


@app.middleware("http")
async def inject_json_processing_time_ms(request: Request, call_next):
    """Measure request handling with ``perf_counter``; set ``meta.processing_time_ms`` on JSON bodies."""
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = round((time.perf_counter() - start) * 1000, 3)

    ct = response.headers.get("content-type") or ""
    if "application/json" not in ct.lower():
        return response

    body = b""
    async for chunk in response.body_iterator:
        body += chunk

    try:
        payload = json.loads(body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return Response(
            content=body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )

    if isinstance(payload, dict) and isinstance(payload.get("meta"), dict):
        payload["meta"]["processing_time_ms"] = elapsed_ms
        new_body = json.dumps(payload, default=str).encode("utf-8")
    else:
        new_body = body

    out_headers = {k: v for k, v in response.headers.items() if k.lower() != "content-length"}
    out_headers["content-length"] = str(len(new_body))

    return Response(
        content=new_body,
        status_code=response.status_code,
        headers=out_headers,
        media_type="application/json",
    )


_ALLOWED_UPLOAD_SUFFIXES = frozenset({".md", ".txt", ".pdf"})

_STATIC_DIR = Path(__file__).resolve().parent / "static"

_logger = logging.getLogger(__name__)


class HealthResponse(BaseModel):
    """Service liveness payload for orchestrators and load balancers."""

    status: str = Field(description="Application health indicator")


class IngestUrlRequest(BaseModel):
    """JSON body for URL-based ingest."""

    url: HttpUrl


class IngestPasteRequest(BaseModel):
    """JSON body for pasted text ingest."""

    content: str = Field(min_length=1)
    title: str = Field(default="Pasted Text")


class QueryRequest(BaseModel):
    """JSON body for Wiki-grounded Q&A."""

    question: str = Field(min_length=1)


class QueryFormatRequest(BaseModel):
    """Re-format a synthesized answer for alternate views."""

    model_config = ConfigDict(populate_by_name=True)

    answer_text: str = Field(min_length=1)
    source_chips: list = Field(default_factory=list)
    fmt: str = Field(
        min_length=1,
        alias="format",
        description="mindmap | graph | comparison_table | card | protocol | response_card",
    )
    query_text: str = ""
    answer_id: str | None = None


class FormatClickRequest(BaseModel):
    """Analytics: user tapped a format chip."""

    model_config = ConfigDict(populate_by_name=True)

    fmt: str = Field(min_length=1, alias="format")
    was_useful: bool | None = None
    answer_id: str | None = None


class LintResolveRequest(BaseModel):
    """Resume lint graph after HITL interrupt (``/lint/resolve``)."""

    thread_id: str = Field(min_length=1)
    decisions: dict[str, str] = Field(
        default_factory=dict,
        description='Per pair slug_a__slug_b → "approve" | "reject"',
    )


@app.get("/health", response_model=APIResponse[HealthResponse])
def health() -> APIResponse[HealthResponse]:
    """Liveness probe; no dependency checks in Phase 0 scaffold."""
    return envelop(HealthResponse(status="ok"))


@app.get("/")
async def serve_ui() -> HTMLResponse:
    """Minimal HTML playground (Phase 1 — Viktor/Slack alternative for local use)."""
    index = _STATIC_DIR / "index.html"
    if not index.is_file():
        raise HTTPException(status_code=404, detail="UI not found")
    html = index.read_text(encoding="utf-8")
    html = html.replace("%%SUPABASE_URL%%", os.environ.get("SUPABASE_URL", ""))
    html = html.replace("%%SUPABASE_ANON_KEY%%", os.environ.get("SUPABASE_ANON_KEY", ""))
    return HTMLResponse(content=html)


app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")


@app.post("/ingest", response_model=APIResponse[list[WikiPage]])
async def ingest_document(
    file: UploadFile = File(...),
    tenant_id: str = Depends(get_current_tenant_id),
) -> APIResponse[list[WikiPage]]:
    """Upload Markdown, plain text, or native-digital PDF; run ingest→compile graph."""
    filename = file.filename or "upload"
    suffix = Path(filename).suffix.lower()
    if suffix not in _ALLOWED_UPLOAD_SUFFIXES:
        raise HTTPException(
            status_code=400,
            detail="Supported uploads: .md, .txt, .pdf",
        )

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
    return envelop(pages)


@app.post("/ingest/url", response_model=APIResponse[list[WikiPage]])
async def ingest_url(
    body: IngestUrlRequest,
    tenant_id: str = Depends(get_current_tenant_id),
) -> APIResponse[list[WikiPage]]:
    """Ingest a web article by URL (trafilatura); same compile graph as file upload."""
    pages, err = await run_in_threadpool(
        run_ingest_compile_from_url,
        url=str(body.url),
        tenant_id=tenant_id,
    )
    if err:
        raise HTTPException(status_code=502, detail=err)
    return envelop(pages)


def _ingest_paste_background(content: str, title: str, tenant_id: str) -> None:
    """Run paste ingest after HTTP response (BackgroundTasks)."""
    pages, err = run_ingest_compile_from_paste(
        content=content,
        title=title,
        tenant_id=tenant_id,
    )
    if err:
        _logger.error("Paste ingest failed: %s", err)
    else:
        _logger.info("Paste ingest completed: %s wiki page(s)", len(pages))


@app.post("/ingest/paste", response_model=APIResponse[dict[str, Any]])
async def ingest_paste(
    body: IngestPasteRequest,
    background_tasks: BackgroundTasks,
    tenant_id: str = Depends(get_current_tenant_id),
) -> APIResponse[dict[str, Any]]:
    """
    Ingest raw pasted text directly.
    Expects JSON: {"content": "...", "title": "optional title"}
    """
    from src.modules.ingest.text_paste_adapter import paste_to_ingest_result

    content = body.content.strip()
    title = (body.title or "Pasted Text").strip() or "Pasted Text"
    if not content:
        raise HTTPException(
            status_code=400,
            detail="content field is required and cannot be empty.",
        )

    doc = paste_to_ingest_result(content=content, title=title)
    word_count = int(doc.frontmatter.get("word_count") or 0)

    background_tasks.add_task(_ingest_paste_background, content, title, tenant_id)
    payload: dict[str, Any] = {
        "status": "queued",
        "title": doc.display_title(),
        "word_count": word_count,
    }
    return envelop(payload)


@app.post("/query", response_model=APIResponse[QueryResponseCard])
async def query_wiki(
    body: QueryRequest,
    tenant_id: str = Depends(get_current_tenant_id),
) -> APIResponse[QueryResponseCard]:
    """Ask a question against the compiled Wiki; returns F-pattern ``response_card`` JSON."""
    result, err = await run_in_threadpool(run_query, body.question, tenant_id)
    if err or result is None:
        raise HTTPException(status_code=502, detail=err or "Query produced no result")
    ai = AIContext(
        ai_generated=True,
        cost_usd=result.cost_usd,
    )
    return envelop(result, ai_context=ai)


@app.post("/query/format", response_model=APIResponse[dict[str, Any]])
async def query_format(body: QueryFormatRequest) -> APIResponse[dict[str, Any]]:
    """Transform an answer into mindmap, graph, table, card, or protocol JSON."""
    try:
        out = await run_in_threadpool(
            transform_answer_to_format,
            answer_text=body.answer_text,
            source_chips=list(body.source_chips),
            query_text=body.query_text or "",
            format_id=body.fmt,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return envelop(out, ai_context=AIContext(ai_generated=True))


@app.post("/query/format_click", response_model=APIResponse[dict[str, bool]])
async def query_format_click(
    body: FormatClickRequest,
    tenant_id: str = Depends(get_current_tenant_id),
) -> APIResponse[dict[str, bool]]:
    """Log format chip interaction to ``wiki_log``."""

    def _do() -> None:
        log_format_chip_click(
            tenant_id,
            format_id=body.fmt,
            was_useful=body.was_useful,
            answer_id=body.answer_id,
        )

    await run_in_threadpool(_do)
    return envelop({"logged": True})


@app.post("/lint/run", response_model=APIResponse[dict[str, Any]])
async def lint_run(
    tenant_id: str = Depends(get_current_tenant_id),
) -> APIResponse[dict[str, Any]]:
    """Run full lint (orphans, stale, duplicates, contradictions pass 1–2); may pause for HITL."""
    report = await run_in_threadpool(run_lint, tenant_id)
    return envelop(report.to_dict())


@app.post("/lint/resolve", response_model=APIResponse[dict[str, Any]])
async def lint_resolve(body: LintResolveRequest) -> APIResponse[dict[str, Any]]:
    """Resume lint after interrupt: apply approved contradiction merges."""
    try:
        report = await run_in_threadpool(resume_lint, body.thread_id, body.decisions)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return envelop(report.to_dict())


@app.post("/lint/decay", response_model=APIResponse[dict[str, Any]])
async def lint_decay(
    x_lint_decay_token: str | None = Header(default=None, alias="X-Lint-Decay-Token"),
) -> APIResponse[dict[str, Any]]:
    """Monthly confidence decay (n8n / operator). Requires ``X-Lint-Decay-Token``."""
    secret = (os.environ.get("LINT_DECAY_WEBHOOK_SECRET") or "").strip()
    if not secret:
        raise HTTPException(
            status_code=503,
            detail="LINT_DECAY_WEBHOOK_SECRET is not configured.",
        )
    if (x_lint_decay_token or "").strip() != secret:
        raise HTTPException(status_code=403, detail="Invalid or missing X-Lint-Decay-Token.")
    tenant_id = os.environ.get("COMPILORE_DEFAULT_TENANT_ID", "").strip()
    if not tenant_id:
        raise HTTPException(status_code=500, detail="COMPILORE_DEFAULT_TENANT_ID not configured.")
    decay_report = await run_in_threadpool(run_decay, tenant_id)
    return envelop(decay_report.to_dict())


@app.get("/lint/status", response_model=APIResponse[dict[str, Any]])
async def lint_status(
    tenant_id: str = Depends(get_current_tenant_id),
) -> APIResponse[dict[str, Any]]:
    """Latest persisted lint report from ``wiki_log`` for the current tenant."""
    row = await run_in_threadpool(fetch_last_lint_report, tenant_id)
    if row is None:
        raise HTTPException(
            status_code=404,
            detail="No lint_run found in wiki_log for this tenant.",
        )
    return envelop(row)
