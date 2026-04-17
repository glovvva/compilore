"""Technical Advisor ICP query wrapper.

Called instead of run_query() when TECHNICAL_ADVISOR_MODE=True. Core
query_graph.py is untouched.
"""

from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from starlette.concurrency import run_in_threadpool

from src.config.settings import settings
from src.graphs.query_graph import run_query
from src.lib.supabase import create_supabase_client
from src.modules.query.models import QueryResponseCard
from src.modules.query.technical_parameter_filter import (
    ParsedQuery,
    SearchCandidate,
    filter_by_technical_parameters,
)


class ParameterFilterResult(BaseModel):
    """Compact filter summary attached to technical advisor query responses."""

    model_config = ConfigDict(extra="forbid")

    exact_matches: int = Field(default=0)
    partial_matches: int = Field(default=0)
    eliminated: int = Field(default=0)


_VOLTAGE_RE = re.compile(r"\b(\d+(?:[.,]\d+)?)\s*V\b", re.IGNORECASE)
_CURRENT_RE = re.compile(r"\b(\d+(?:[.,]\d+)?)\s*A\b", re.IGNORECASE)
_TEMP_RANGE_RE = re.compile(
    r"(-?\d+(?:[.,]\d+)?)\s*(?:°?\s*C)?\s*(?:to|do|[-–])\s*\+?(-?\d+(?:[.,]\d+)?)\s*°?\s*C",
    re.IGNORECASE,
)
_THREE_PHASE_RE = re.compile(r"\b(3[\s-]?phase|three[\s-]?phase)\b", re.IGNORECASE)
_SINGLE_PHASE_RE = re.compile(r"\b(1[\s-]?phase|single[\s-]?phase)\b", re.IGNORECASE)
_DIN_RE = re.compile(r"\bdin(?:\s*rail)?\b", re.IGNORECASE)


def _as_float(value: str) -> float:
    return float(value.replace(",", "."))


def _extract_parameters(question: str) -> ParsedQuery | None:
    """Parse simple deterministic technical constraints from free text."""
    hard_parameters: dict[str, Any] = {}

    voltage_match = _VOLTAGE_RE.search(question)
    if voltage_match:
        hard_parameters["voltage"] = _as_float(voltage_match.group(1))

    current_match = _CURRENT_RE.search(question)
    if current_match:
        hard_parameters["current"] = _as_float(current_match.group(1))

    temp_match = _TEMP_RANGE_RE.search(question)
    if temp_match:
        hard_parameters["temperature_range"] = {
            "min": _as_float(temp_match.group(1)),
            "max": _as_float(temp_match.group(2)),
        }

    if _THREE_PHASE_RE.search(question):
        hard_parameters["phases"] = "3-phase"
    elif _SINGLE_PHASE_RE.search(question):
        hard_parameters["phases"] = "1-phase"

    if _DIN_RE.search(question):
        hard_parameters["mounting"] = "DIN rail"

    if not hard_parameters:
        return None

    return ParsedQuery(hard_parameters=hard_parameters, soft_parameters={})


def _fetch_product_candidates(tenant_id: str, slugs: list[str]) -> list[SearchCandidate]:
    """Fetch cited product pages with frontmatter technical parameters."""
    unique_slugs = [slug for slug in dict.fromkeys(slugs) if slug]
    if not unique_slugs:
        return []

    client = create_supabase_client()
    res = (
        client.table("wiki_pages")
        .select("slug,title,page_type,frontmatter")
        .eq("tenant_id", tenant_id)
        .in_("slug", unique_slugs)
        .execute()
    )
    rows = getattr(res, "data", None) or []
    out: list[SearchCandidate] = []
    for row in rows:
        frontmatter = row.get("frontmatter") or {}
        technical_parameters = frontmatter.get("technical_parameters") or {}
        if not isinstance(technical_parameters, dict):
            technical_parameters = {}
        out.append(
            SearchCandidate(
                slug=str(row.get("slug") or ""),
                title=str(row.get("title") or ""),
                page_type=str(row.get("page_type") or ""),
                technical_parameters=technical_parameters,
            )
        )
    return out


async def run_technical_advisor_query(question: str, tenant_id: str) -> QueryResponseCard:
    """Run core query flow, then optionally apply deterministic parameter filtering."""
    if not settings.TECHNICAL_ADVISOR_MODE:
        raise RuntimeError("TECHNICAL_ADVISOR_MODE is disabled")

    result, err = await run_in_threadpool(run_query, question, tenant_id)
    if err or result is None:
        raise RuntimeError(err or "Query produced no result")

    product_slugs = [
        chip.slug
        for chip in result.source_chips
        if chip.page_type == "product_entity" and chip.slug
    ]
    if not product_slugs:
        return result

    parsed_params = _extract_parameters(question)
    if parsed_params is None:
        return result

    candidates = await run_in_threadpool(_fetch_product_candidates, tenant_id, product_slugs)
    if not candidates:
        return result

    filtered = await run_in_threadpool(filter_by_technical_parameters, candidates, parsed_params)
    summary = ParameterFilterResult(
        exact_matches=len(filtered.exact_matches),
        partial_matches=len(filtered.partial_matches),
        eliminated=len(filtered.eliminated),
    )
    return result.model_copy(
        update={"parameter_filter_result": summary.model_dump(mode="json")}
    )
