"""Department management HTTP router (tenant-scoped)."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from src.lib.auth import TenantContext, get_current_tenant_id
from src.lib.response import APIResponse, envelop
from src.lib.supabase import create_supabase_client

departments_router = APIRouter()


class DepartmentOut(BaseModel):
    id: str
    tenant_id: str
    name: str
    slug: str
    visibility: Literal["private", "tenant_wide"]
    created_at: str


class DepartmentCreateRequest(BaseModel):
    name: str = Field(min_length=1)
    slug: str = Field(min_length=1)
    visibility: Literal["private", "tenant_wide"] = "private"


@departments_router.get("", response_model=APIResponse[list[DepartmentOut]])
async def list_departments(
    tenant: TenantContext = Depends(get_current_tenant_id),
) -> APIResponse[list[DepartmentOut]]:
    client = create_supabase_client()
    tenant_id = tenant["tenant_id"]
    result = (
        client.table("departments")
        .select("id, tenant_id, name, slug, visibility, created_at")
        .eq("tenant_id", tenant_id)
        .order("created_at", desc=False)
        .execute()
    )
    rows = getattr(result, "data", None) or []
    payload = [DepartmentOut.model_validate(row) for row in rows]
    return envelop(payload, available_actions=["query", "ingest", "lint"])


@departments_router.post("", response_model=APIResponse[DepartmentOut])
async def create_department(
    body: DepartmentCreateRequest,
    tenant: TenantContext = Depends(get_current_tenant_id),
) -> APIResponse[DepartmentOut]:
    client = create_supabase_client()
    tenant_id = tenant["tenant_id"]
    row = {
        "tenant_id": tenant_id,
        "name": body.name.strip(),
        "slug": body.slug.strip(),
        "visibility": body.visibility,
    }
    try:
        result = client.table("departments").insert(row).execute()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Department create failed: {exc}") from exc

    data = getattr(result, "data", None) or []
    if not data:
        raise HTTPException(status_code=500, detail="Department create returned no data")
    department = DepartmentOut.model_validate(data[0])
    return envelop(department, available_actions=["query", "ingest", "lint"])


@departments_router.get("/{slug}", response_model=APIResponse[DepartmentOut])
async def get_department(
    slug: str,
    tenant: TenantContext = Depends(get_current_tenant_id),
) -> APIResponse[DepartmentOut]:
    client = create_supabase_client()
    tenant_id = tenant["tenant_id"]
    result = (
        client.table("departments")
        .select("id, tenant_id, name, slug, visibility, created_at")
        .eq("tenant_id", tenant_id)
        .eq("slug", slug)
        .limit(1)
        .execute()
    )
    rows = getattr(result, "data", None) or []
    if not rows:
        raise HTTPException(status_code=404, detail=f"Department {slug!r} not found")
    department = DepartmentOut.model_validate(rows[0])
    return envelop(department, available_actions=["query", "ingest", "lint"])

