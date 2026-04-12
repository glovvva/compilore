"""Pydantic models for the **Query** loop (search, synthesis, gatekeeper, API)."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class ChunkResult(BaseModel):
    """One row from hybrid search over ``document_chunks``."""

    model_config = ConfigDict(extra="forbid")

    chunk_id: str
    wiki_page_id: str
    chunk_text: str
    rrf_score: float = Field(description="Reciprocal rank fusion score")


class SynthesisResult(BaseModel):
    """Claude synthesis output for a user question."""

    model_config = ConfigDict(extra="forbid")

    answer_markdown: str
    citations: list[str] = Field(default_factory=list, description="Cited wiki slugs or wikilinks")
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0


class SourceChip(BaseModel):
    """One retrieved wiki page shown on the response card."""

    model_config = ConfigDict(extra="forbid")

    title: str
    slug: str
    page_type: str


class QueryResponseCard(BaseModel):
    """HTTP response for ``POST /query`` (Sprint 4 F-pattern card + format hints)."""

    model_config = ConfigDict(extra="forbid")

    format: Literal["response_card"] = "response_card"
    headline: str
    body: str
    source_chips: list[SourceChip] = Field(default_factory=list)
    confidence: float = 0.0
    confidence_delta: Optional[str] = Field(
        default=None,
        description="Change vs last query top-page confidence, e.g. +0.15",
    )
    save_to_wiki: bool = False
    gatekeeper_passed: bool = False
    suggested_formats: list[str] = Field(default_factory=list)
    format_reasoning: dict[str, str] = Field(default_factory=dict)
    gatekeeper_reasoning: str = ""
    cost_usd: float = Field(
        default=0.0,
        description="Total estimated Claude USD (synthesis + gatekeeper + headline)",
    )
    answer_id: str
    requested_format: Optional[str] = None


class QueryResult(BaseModel):
    """Legacy flat query response (pre–Sprint 4). Prefer :class:`QueryResponseCard`."""

    model_config = ConfigDict(extra="forbid")

    answer_markdown: str
    citations: list[str] = Field(default_factory=list)
    saved_to_wiki: bool = False
    gatekeeper_reasoning: str = ""
    cost_usd: float = Field(description="Total estimated Claude USD for this query (synthesis + gatekeeper)")
