"""Supabase client for Compilore (service role — server-side only)."""

from __future__ import annotations

import asyncio
import os
import threading
from typing import Any, Literal, Optional, TypedDict

from supabase import Client, create_client

from src.modules.compile.models import WikiPage

_TENANT_FK_HINT = (
    "Ensure COMPILORE_DEFAULT_TENANT_ID matches a row in public.tenants "
    "(run sql/003_seed_tenant.sql, then SELECT id FROM tenants WHERE name = 'bartek-playground')."
)


class Department(TypedDict):
    """Department row returned by Supabase."""

    id: str
    tenant_id: str
    name: str
    slug: str
    visibility: Literal["private", "tenant_wide"]
    created_at: str


def get_supabase_service_key() -> str:
    """Resolve service key from env (supports legacy role key name)."""
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not key or not key.strip():
        msg = "Set SUPABASE_SERVICE_ROLE_KEY for server-side access"
        raise RuntimeError(msg)
    return key.strip()


def create_supabase_client(url: Optional[str] = None, service_key: Optional[str] = None) -> Client:
    """Return a Supabase client using the service key (bypasses RLS for backend jobs)."""
    resolved_url = (url or os.environ.get("SUPABASE_URL") or "").strip()
    if not resolved_url:
        msg = "SUPABASE_URL is not set"
        raise RuntimeError(msg)
    key = service_key or get_supabase_service_key()
    return create_client(resolved_url, key)


def ensure_tenant_exists(client: Client, tenant_id: str) -> None:
    """Raise a clear error if ``tenant_id`` is missing from ``public.tenants``."""
    tid = tenant_id.strip()
    if not tid:
        msg = "tenant_id is empty — set COMPILORE_DEFAULT_TENANT_ID in .env"
        raise RuntimeError(msg)
    res = client.table("tenants").select("id").eq("id", tid).limit(1).execute()
    rows = getattr(res, "data", None) or []
    if not rows:
        msg = (
            f"No tenant registered with id={tid!r}. {_TENANT_FK_HINT} "
            "Foreign-key errors on insert usually mean this id is wrong or seed SQL was not applied."
        )
        raise RuntimeError(msg)


def _translate_insert_error(exc: BaseException, *, context: str) -> RuntimeError:
    """Map PostgREST / Postgres errors to operator-friendly messages."""
    raw = str(exc).lower()
    if "foreign key" in raw or "23503" in raw:
        return RuntimeError(
            f"{context}: database rejected the row (foreign key). {_TENANT_FK_HINT} "
            f"Original error: {exc}",
        )
    return RuntimeError(f"{context}: {exc}")


def insert_document_row(
    client: Client,
    *,
    tenant_id: str,
    title: str,
    doc_type: str,
    file_path: Optional[str],
    metadata: dict[str, Any],
    module: Optional[str] = None,
    authority_tier: int = 3,
) -> str:
    """Insert a ``documents`` row; return new UUID string."""
    ensure_tenant_exists(client, tenant_id)
    row: dict[str, Any] = {
        "tenant_id": tenant_id,
        "title": title,
        "doc_type": doc_type,
        "file_path": file_path,
        "status": "compiled",
        "metadata": metadata,
        "authority_tier": authority_tier,
    }
    if module is not None:
        row["module"] = module
    try:
        res = client.table("documents").insert(row).execute()
    except Exception as exc:
        raise _translate_insert_error(exc, context="documents insert") from exc
    data = getattr(res, "data", None) or []
    if not data or not isinstance(data, list):
        msg = "Supabase documents insert returned no row"
        raise RuntimeError(msg)
    row_id = data[0].get("id")
    if not row_id:
        msg = "Supabase documents insert missing id"
        raise RuntimeError(msg)
    return str(row_id)


def insert_wiki_pages_for_document(
    client: Client,
    *,
    tenant_id: str,
    document_id: str,
    pages: list[WikiPage],
) -> dict[str, str]:
    """Insert wiki pages; return map ``slug -> wiki_page_id`` (UUID string)."""
    ensure_tenant_exists(client, tenant_id)
    slug_to_id: dict[str, str] = {}
    for page in pages:
        row: dict[str, Any] = {
            "tenant_id": tenant_id,
            "slug": page.slug,
            "title": page.title,
            "page_type": page.page_type,
            "content_markdown": page.content_markdown,
            "frontmatter": page.frontmatter,
            "source_documents": [document_id],
        }
        try:
            res = client.table("wiki_pages").insert(row).execute()
        except Exception as exc:
            raise _translate_insert_error(
                exc,
                context=f"wiki_pages insert (slug={page.slug!r})",
            ) from exc
        data = getattr(res, "data", None) or []
        if not data:
            msg = "wiki_pages insert returned no row"
            raise RuntimeError(msg)
        row_id = data[0].get("id")
        if not row_id:
            msg = "wiki_pages insert missing id"
            raise RuntimeError(msg)
        slug_to_id[page.slug] = str(row_id)
    return slug_to_id


def insert_document_chunk(
    client: Client,
    *,
    tenant_id: str,
    wiki_page_id: str,
    document_id: str,
    chunk_text: str,
    chunk_index: int,
    embedding: list[float],
    metadata: Optional[dict[str, Any]] = None,
) -> None:
    """Insert one ``document_chunks`` row (embedding dimension 1536)."""
    row: dict[str, Any] = {
        "tenant_id": tenant_id,
        "wiki_page_id": wiki_page_id,
        "document_id": document_id,
        "chunk_text": chunk_text,
        "chunk_index": chunk_index,
        "embedding": embedding,
        "metadata": metadata or {},
    }
    client.table("document_chunks").insert(row).execute()


def fetch_wiki_slugs_for_page_ids(
    client: Client,
    *,
    tenant_id: str,
    wiki_page_ids: list[str],
) -> dict[str, str]:
    """Return ``wiki_page_id -> slug`` for the given ids (same tenant)."""
    if not wiki_page_ids:
        return {}
    res = (
        client.table("wiki_pages")
        .select("id, slug")
        .eq("tenant_id", tenant_id)
        .in_("id", wiki_page_ids)
        .execute()
    )
    data = getattr(res, "data", None) or []
    out: dict[str, str] = {}
    for row in data:
        wid = row.get("id")
        slug = row.get("slug")
        if wid and slug:
            out[str(wid)] = str(slug)
    return out


def insert_wiki_page_row(
    client: Client,
    *,
    tenant_id: str,
    slug: str,
    title: str,
    page_type: str,
    content_markdown: str,
    frontmatter: dict[str, Any],
    source_documents: list[str],
) -> str:
    """Insert a single ``wiki_pages`` row; return new id."""
    row: dict[str, Any] = {
        "tenant_id": tenant_id,
        "slug": slug,
        "title": title,
        "page_type": page_type,
        "content_markdown": content_markdown,
        "frontmatter": frontmatter,
        "source_documents": source_documents,
    }
    res = client.table("wiki_pages").insert(row).execute()
    data = getattr(res, "data", None) or []
    if not data or not data[0].get("id"):
        msg = "wiki_pages insert failed"
        raise RuntimeError(msg)
    return str(data[0]["id"])


def insert_wiki_log_row(
    client: Client,
    *,
    tenant_id: str,
    operation: str,
    details: dict[str, Any],
    tokens_used: int = 0,
    cost_usd: float = 0.0,
    module: Optional[str] = None,
) -> None:
    """Append one row to ``wiki_log`` (best-effort callers should catch exceptions)."""
    ensure_tenant_exists(client, tenant_id)
    row: dict[str, Any] = {
        "tenant_id": tenant_id,
        "operation": operation,
        "details": details,
        "tokens_used": tokens_used,
        "cost_usd": cost_usd,
    }
    if module is not None:
        row["module"] = module
    client.table("wiki_log").insert(row).execute()


async def get_user_organization_id(user_id: str) -> Optional[str]:
    """
    Returns the primary organization_id for a given user.
    Phase 1: each user has exactly one org.
    Phase 2: will support multiple orgs per user.
    """
    client = create_supabase_client()

    def _query() -> list[dict[str, Any]]:
        result = (
            client.table("org_members")
            .select("organization_id")
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        return getattr(result, "data", None) or []

    rows = await asyncio.to_thread(_query)
    if rows:
        organization_id = rows[0].get("organization_id")
        if organization_id:
            return str(organization_id)
    return None


def schedule_insert_wiki_log_row(
    *,
    tenant_id: str,
    operation: str,
    details: dict[str, Any],
    tokens_used: int = 0,
    cost_usd: float = 0.0,
    module: Optional[str] = None,
) -> None:
    """Fire-and-forget ``insert_wiki_log_row`` (thread if no running asyncio loop)."""

    def _run() -> None:
        try:
            client = create_supabase_client()
            insert_wiki_log_row(
                client,
                tenant_id=tenant_id,
                operation=operation,
                details=details,
                tokens_used=tokens_used,
                cost_usd=cost_usd,
                module=module,
            )
        except Exception:
            pass

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop is not None:
        loop.create_task(asyncio.to_thread(_run))
    else:
        threading.Thread(target=_run, daemon=True).start()
