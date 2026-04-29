from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.lib.auth import TenantContext, get_current_tenant_id
from src.lib.supabase import create_supabase_client

wiki_router = APIRouter()


class WikiPageListItem(BaseModel):
    id: str
    slug: str
    title: str
    page_type: str
    frontmatter: dict[str, Any]
    confidence: float
    status: Optional[str]
    updated_at: str


class WikiPagesResponse(BaseModel):
    pages: list[WikiPageListItem]


@wiki_router.get("/pages", response_model=WikiPagesResponse)
async def list_wiki_pages(
    tenant: TenantContext = Depends(get_current_tenant_id),
) -> WikiPagesResponse:
    """Return all wiki pages for the current tenant (lightweight list for sidebar/nav)."""
    tenant_id = tenant["tenant_id"]
    client = create_supabase_client()
    result = (
        client.table("wiki_pages")
        .select("id, slug, title, page_type, frontmatter, confidence, status, updated_at")
        .eq("tenant_id", tenant_id)
        .order("page_type", desc=False)
        .order("title", desc=False)
        .execute()
    )
    rows = getattr(result, "data", None) or []
    pages = [
        WikiPageListItem(
            id=str(row["id"]),
            slug=str(row["slug"]),
            title=str(row["title"]),
            page_type=str(row["page_type"]),
            frontmatter=row.get("frontmatter") or {},
            confidence=float(row.get("confidence") or 0),
            status=str(row["status"]) if row.get("status") is not None else None,
            updated_at=str(row["updated_at"]),
        )
        for row in rows
    ]
    return WikiPagesResponse(pages=pages)
