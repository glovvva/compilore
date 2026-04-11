"""Pydantic models for **Compile** loop outputs."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class WikiPage(BaseModel):
    """One compiled Wiki page produced by Claude (persisted to Git + Supabase)."""

    model_config = ConfigDict(extra="forbid")

    slug: str = Field(min_length=1, description="URL-safe unique slug for file name and wikilinks")
    title: str = Field(min_length=1)
    page_type: Literal["concept", "entity", "source_summary", "output", "index"]
    content_markdown: str = Field(description="Markdown body only (no YAML fence)")
    frontmatter: dict[str, Any] = Field(default_factory=dict, description="YAML frontmatter fields as JSON object")
