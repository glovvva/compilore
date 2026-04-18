"""LangGraph: **Ingest** → **Compile** pipeline.

Nodes: read_document → compile_wiki → store_to_supabase → write_wiki_files →
git_commit → log_operation (second commit for ``log.md`` only). Uses ``MemorySaver`` until
PostgresSaver is wired. After ``store_to_supabase``, ``embed_and_store_chunks`` writes ``document_chunks``
for hybrid / full-text retrieval.
"""

from __future__ import annotations

import os
import uuid
from decimal import Decimal
from pathlib import Path
from typing import Any, Optional, TypedDict

from git import Repo
from git.exc import GitCommandError
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from src.lib.supabase import (
    create_supabase_client,
    insert_document_row,
    insert_wiki_pages_for_document,
)
from src.modules.compile.index_manager import append_compiled_pages_to_index
from src.modules.compile.models import WikiPage
from src.modules.compile.embed_chunks import embed_and_store_wiki_pages_chunks
from src.modules.compile.wiki_generator import (
    DEFAULT_MODEL,
    compile_wiki_pages,
    schedule_wiki_generator_compile_log,
)
from src.modules.compile.wiki_log import append_compile_cost_line
from src.modules.compile.wiki_storage import write_wiki_page_files
from src.modules.ingest.markdown_adapter import MarkdownIngestAdapter
from src.modules.ingest.models import (
    IngestResult,
    ingest_result_from_mapping,
    ingest_result_to_mapping,
)
from src.modules.ingest.pdf_router import extract_pdf
from src.modules.ingest.text_adapter import TextIngestAdapter
from src.modules.ingest.text_paste_adapter import paste_to_ingest_result
from src.modules.ingest.url_adapter import extract_url


class IngestCompileState(TypedDict, total=False):
    """LangGraph state (JSON-serializable values for ``MemorySaver``)."""

    max_retries: int
    compile_retry_count: int
    temp_path: str
    source_url: str
    paste_body: str
    paste_title: str
    original_filename: str
    tenant_id: str
    ingest: dict[str, Any]
    document_title: str
    wiki_pages: list[dict[str, Any]]
    document_id: str
    claude_input_tokens: int
    claude_output_tokens: int
    claude_cost_usd: float
    wiki_paths_written: list[str]
    wiki_page_ids_by_slug: dict[str, str]
    chunks_embedded: int
    error: Optional[str]


def _ingest_adapter_module(doc_type: str) -> str:
    """``documents.module`` — matches ingestion adapter module names."""
    return {
        "markdown": "markdown_adapter",
        "text": "text_adapter",
        "pdf": "pdf_router",
        "url": "url_adapter",
        "paste": "text_paste_adapter",
    }.get(doc_type, "unknown_adapter")


def resolve_wiki_root() -> Path:
    raw = os.environ.get("WIKI_REPO_PATH", "wiki")
    root = Path(raw)
    if not root.is_absolute():
        root = Path.cwd() / root
    return root.resolve()


def _default_tenant_id() -> str:
    tid = os.environ.get("COMPILORE_DEFAULT_TENANT_ID", "").strip()
    if not tid:
        msg = "COMPILORE_DEFAULT_TENANT_ID is not set"
        raise RuntimeError(msg)
    return tid


def node_read_document(state: IngestCompileState) -> dict[str, Any]:
    if state.get("error"):
        return {}
    paste_body = state.get("paste_body")
    if paste_body is not None:
        try:
            ingest = paste_to_ingest_result(
                str(paste_body),
                state.get("paste_title") or "Pasted Text",
            )
        except ValueError as exc:
            return {"error": str(exc)}
        return {
            "ingest": ingest_result_to_mapping(ingest),
            "document_title": ingest.display_title(),
        }

    url = (state.get("source_url") or "").strip()
    if url:
        try:
            ingest = extract_url(url)
        except (OSError, RuntimeError, ValueError) as exc:
            return {"error": f"URL ingest failed: {exc}"}
        except Exception as exc:
            return {"error": f"URL ingest failed: {exc}"}
        return {
            "ingest": ingest_result_to_mapping(ingest),
            "document_title": ingest.display_title(),
        }

    temp = state.get("temp_path")
    if not temp:
        return {"error": "Missing temp_path or source_url for ingest"}
    path = Path(temp)
    if not path.is_file():
        return {"error": f"Upload file not found: {temp}"}
    suffix = path.suffix.lower()
    try:
        if suffix == ".md":
            ingest = MarkdownIngestAdapter().extract(path)
        elif suffix == ".txt":
            ingest = TextIngestAdapter().extract(path)
        elif suffix == ".pdf":
            chunks = extract_pdf(path)
            body = "\n\n".join(c["text"] for c in chunks).strip()
            if not body:
                return {"error": "PDF contained no extractable text"}
            ingest = IngestResult(
                body=body,
                frontmatter={
                    "adapter_used": (
                        chunks[0].get("adapter_used", "unknown")
                        if chunks
                        else "unknown"
                    ),
                    "tables_extracted": sum(
                        1 for c in chunks if c.get("chunk_type") == "table"
                    ),
                },
                source_path=path.resolve(),
                doc_type="pdf",
            )
        else:
            return {
                "error": f"Unsupported file type for ingest: {suffix} (use .md, .txt, or .pdf)",
            }
    except OSError as exc:
        return {"error": f"Failed to read file: {exc}"}
    except Exception as exc:
        return {"error": f"Ingest failed: {exc}"}
    return {
        "ingest": ingest_result_to_mapping(ingest),
        "document_title": ingest.display_title(),
    }


def node_compile_wiki(state: IngestCompileState) -> dict[str, Any]:
    err_existing = state.get("error")
    if err_existing and not str(err_existing).startswith("Compile failed:"):
        return {}
    max_r = int(state["max_retries"]) if state.get("max_retries") is not None else 3
    if err_existing and str(err_existing).startswith("Compile failed:"):
        if int(state.get("compile_retry_count") or 0) >= max_r:
            return {}
    try:
        ingest = ingest_result_from_mapping(state["ingest"])
        pages, in_tok, out_tok, cost = compile_wiki_pages(ingest)
    except Exception as exc:
        new_count = int(state.get("compile_retry_count") or 0) + 1
        return {"error": f"Compile failed: {exc}", "compile_retry_count": new_count}
    return {
        "wiki_pages": [p.model_dump(mode="json") for p in pages],
        "claude_input_tokens": in_tok,
        "claude_output_tokens": out_tok,
        "claude_cost_usd": float(cost),
        "error": None,
        "compile_retry_count": 0,
    }


def route_after_compile(state: IngestCompileState) -> str:
    """After compile: continue, retry compile, or stop (no infinite compile loop)."""
    err = state.get("error")
    if not err:
        return "store_to_supabase"
    err_s = str(err)
    if err_s.startswith("Compile failed:"):
        max_r = int(state["max_retries"]) if state.get("max_retries") is not None else 3
        cnt = int(state.get("compile_retry_count") or 0)
        if cnt >= max_r:
            return "abort"
        return "compile_wiki"
    return "abort"


def node_store_to_supabase(state: IngestCompileState) -> dict[str, Any]:
    if state.get("error"):
        return {}
    try:
        client = create_supabase_client()
        tenant_id = state.get("tenant_id") or _default_tenant_id()
        ingest = ingest_result_from_mapping(state["ingest"])
        pages = [WikiPage.model_validate(p) for p in state["wiki_pages"]]
        metadata: dict[str, Any] = {
            "original_filename": state.get("original_filename"),
            "frontmatter": ingest.frontmatter,
        }
        file_path = state.get("temp_path")
        if ingest.doc_type == "paste":
            file_path = None
        elif ingest.doc_type == "url":
            su = ingest.frontmatter.get("source_url")
            if isinstance(su, str) and su.strip():
                file_path = su.strip()
        doc_id = insert_document_row(
            client,
            tenant_id=tenant_id,
            title=state["document_title"],
            doc_type=ingest.doc_type,
            file_path=file_path,
            metadata=metadata,
            module=_ingest_adapter_module(ingest.doc_type),
        )
        slug_to_id = insert_wiki_pages_for_document(
            client,
            tenant_id=tenant_id,
            document_id=doc_id,
            pages=pages,
        )
    except Exception as exc:
        return {"error": f"Supabase persist failed: {exc}"}
    pdf_extract_log = None
    if ingest.doc_type == "pdf":
        fm = ingest.frontmatter or {}
        pdf_extract_log = {
            "adapter_used": fm.get("adapter_used", "unknown"),
            "tables_extracted": int(fm.get("tables_extracted", 0)),
        }
    schedule_wiki_generator_compile_log(
        tenant_id=tenant_id,
        document_id=doc_id,
        pages=pages,
        input_tokens=int(state.get("claude_input_tokens", 0)),
        output_tokens=int(state.get("claude_output_tokens", 0)),
        cost_usd=float(state.get("claude_cost_usd", 0)),
        pdf_extract_log=pdf_extract_log,
    )
    return {"document_id": doc_id, "wiki_page_ids_by_slug": slug_to_id}


def node_embed_and_store_chunks(state: IngestCompileState) -> dict[str, Any]:
    if state.get("error"):
        return {}
    try:
        client = create_supabase_client()
        tenant_id = state.get("tenant_id") or _default_tenant_id()
        doc_id = state["document_id"]
        pages = [WikiPage.model_validate(p) for p in state["wiki_pages"]]
        slug_map = state.get("wiki_page_ids_by_slug") or {}
        n = embed_and_store_wiki_pages_chunks(
            client,
            tenant_id=tenant_id,
            document_id=doc_id,
            pages=pages,
            slug_to_wiki_page_id=slug_map,
        )
    except Exception as exc:
        return {"error": f"Embed / chunk store failed: {exc}"}
    return {"chunks_embedded": n}


def node_write_wiki_files(state: IngestCompileState) -> dict[str, Any]:
    if state.get("error"):
        return {}
    wiki_root = resolve_wiki_root()
    pages = [WikiPage.model_validate(p) for p in state["wiki_pages"]]
    try:
        written = write_wiki_page_files(wiki_root, pages)
        append_compiled_pages_to_index(
            wiki_root,
            pages,
            document_title=state["document_title"],
        )
    except OSError as exc:
        return {"error": f"Wiki file write failed: {exc}"}
    return {"wiki_paths_written": written}


def node_log_operation(state: IngestCompileState) -> dict[str, Any]:
    if state.get("error"):
        return {}
    wiki_root = resolve_wiki_root()
    try:
        append_compile_cost_line(
            wiki_root,
            document_title=state["document_title"],
            cost_usd=Decimal(str(state.get("claude_cost_usd", 0))),
            input_tokens=int(state.get("claude_input_tokens", 0)),
            output_tokens=int(state.get("claude_output_tokens", 0)),
            page_count=len(state.get("wiki_pages") or []),
            model=DEFAULT_MODEL,
        )
        repo = Repo(wiki_root)
        repo.index.add(["log.md"])
        try:
            repo.index.commit(f"log: compile cost — {state['document_title']}")
        except GitCommandError as exc:
            err = str(exc).lower()
            if "nothing to commit" in err or "no changes" in err:
                return {}
            return {"error": f"Git log commit failed: {exc}"}
    except OSError as exc:
        return {"error": f"Wiki log append failed: {exc}"}
    except Exception as exc:
        return {"error": f"Wiki log / git failed: {exc}"}
    return {}


def node_git_commit(state: IngestCompileState) -> dict[str, Any]:
    if state.get("error"):
        return {}
    wiki_root = resolve_wiki_root()
    title = state["document_title"]
    try:
        repo = Repo(wiki_root)
        rels = list(state.get("wiki_paths_written") or [])
        for extra in ("index.md",):
            if extra not in rels:
                rels.append(extra)
        staged = [rel for rel in rels if (wiki_root / rel).is_file()]
        if not staged:
            return {"error": "Git commit skipped: no wiki files were written to stage"}
        repo.index.add(staged)
        try:
            repo.index.commit(f"compile: {title}")
        except GitCommandError as exc:
            err = str(exc).lower()
            if "nothing to commit" in err or "no changes" in err:
                return {}
            return {"error": f"Git commit failed: {exc}"}
    except Exception as exc:
        return {"error": f"Git commit failed: {exc}"}
    return {}


def build_ingest_compile_graph() -> Any:
    """Compile the ingest→compile graph with in-memory checkpointing."""
    builder = StateGraph(IngestCompileState)
    builder.add_node("read_document", node_read_document)
    builder.add_node("compile_wiki", node_compile_wiki)
    builder.add_node("store_to_supabase", node_store_to_supabase)
    builder.add_node("embed_and_store_chunks", node_embed_and_store_chunks)
    builder.add_node("write_wiki_files", node_write_wiki_files)
    builder.add_node("log_operation", node_log_operation)
    builder.add_node("git_commit", node_git_commit)

    builder.add_edge(START, "read_document")
    builder.add_edge("read_document", "compile_wiki")
    builder.add_conditional_edges(
        "compile_wiki",
        route_after_compile,
        {
            "store_to_supabase": "store_to_supabase",
            "compile_wiki": "compile_wiki",
            "abort": END,
        },
    )
    builder.add_edge("store_to_supabase", "embed_and_store_chunks")
    builder.add_edge("embed_and_store_chunks", "write_wiki_files")
    builder.add_edge("write_wiki_files", "git_commit")
    builder.add_edge("git_commit", "log_operation")
    builder.add_edge("log_operation", END)

    memory = MemorySaver()
    return builder.compile(checkpointer=memory)


def run_ingest_compile(
    *,
    temp_path: Path,
    original_filename: str,
    tenant_id: str | None = None,
) -> tuple[list[WikiPage], str | None]:
    """Execute the graph once; return ``(pages, error_message)``."""
    graph = build_ingest_compile_graph()
    tid = (tenant_id or "").strip() or _default_tenant_id()
    thread_id = f"ingest-{uuid.uuid4()}"
    out: IngestCompileState = graph.invoke(
        {
            "temp_path": str(temp_path.resolve()),
            "original_filename": original_filename,
            "tenant_id": tid,
            "error": None,
            "max_retries": 3,
            "compile_retry_count": 0,
        },
        config={"configurable": {"thread_id": thread_id}},
    )
    err = out.get("error")
    if err:
        return [], str(err)
    raw_pages = out.get("wiki_pages") or []
    pages = [WikiPage.model_validate(p) for p in raw_pages]
    return pages, None


def run_ingest_compile_from_url(
    *,
    url: str,
    tenant_id: str | None = None,
) -> tuple[list[WikiPage], str | None]:
    """Execute ingest→compile for a remote URL (``read_document`` uses URL adapter)."""
    graph = build_ingest_compile_graph()
    tid = (tenant_id or "").strip() or _default_tenant_id()
    thread_id = f"ingest-url-{uuid.uuid4()}"
    raw_url = url.strip()
    out: IngestCompileState = graph.invoke(
        {
            "source_url": raw_url,
            "original_filename": raw_url,
            "tenant_id": tid,
            "error": None,
            "max_retries": 3,
            "compile_retry_count": 0,
        },
        config={"configurable": {"thread_id": thread_id}},
    )
    err = out.get("error")
    if err:
        return [], str(err)
    raw_pages = out.get("wiki_pages") or []
    pages = [WikiPage.model_validate(p) for p in raw_pages]
    return pages, None


def run_ingest_compile_from_paste(
    *,
    content: str,
    title: str = "Pasted Text",
    tenant_id: str | None = None,
) -> tuple[list[WikiPage], str | None]:
    """Execute ingest→compile for raw pasted text (no file upload)."""
    graph = build_ingest_compile_graph()
    tid = (tenant_id or "").strip() or _default_tenant_id()
    thread_id = f"ingest-paste-{uuid.uuid4()}"
    out: IngestCompileState = graph.invoke(
        {
            "paste_body": content,
            "paste_title": title,
            "original_filename": "paste.txt",
            "tenant_id": tid,
            "error": None,
            "max_retries": 3,
            "compile_retry_count": 0,
        },
        config={"configurable": {"thread_id": thread_id}},
    )
    err = out.get("error")
    if err:
        return [], str(err)
    raw_pages = out.get("wiki_pages") or []
    pages = [WikiPage.model_validate(p) for p in raw_pages]
    return pages, None
