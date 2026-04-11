"""Pydantic models for the **Query** loop (search, synthesis, gatekeeper, API)."""

from __future__ import annotations

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


class QueryResult(BaseModel):
    """HTTP response for ``POST /query``."""

    model_config = ConfigDict(extra="forbid")

    answer_markdown: str
    citations: list[str] = Field(default_factory=list)
    saved_to_wiki: bool = False
    gatekeeper_reasoning: str = ""
    cost_usd: float = Field(description="Total estimated Claude USD for this query (synthesis + gatekeeper)")
