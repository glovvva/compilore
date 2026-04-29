"""Outputs API router (proposal generation)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from src.lib.auth import TenantContext, get_current_tenant_id
from src.lib.response import APIResponse, envelop
from src.modules.outputs.proposal_generator import (
    ProposalRequest,
    ProposalResponse,
    generate_proposal,
)

outputs_router = APIRouter()


@outputs_router.post("/proposal", response_model=APIResponse[ProposalResponse])
async def generate_proposal_endpoint(
    body: ProposalRequest,
    tenant: TenantContext = Depends(get_current_tenant_id),
) -> APIResponse[ProposalResponse]:
    """Generate a Markdown proposal using tenant Wiki context."""
    try:
        result = await generate_proposal(body, tenant["tenant_id"])
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Proposal generation failed: {exc}") from exc
    return envelop(result, available_actions=["download", "query", "generate_proposal"])

