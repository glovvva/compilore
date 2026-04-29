"""Pydantic models for **Compile** loop outputs."""

from __future__ import annotations

import json
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic import field_validator
import yaml


class WikiPage(BaseModel):
    """One compiled Wiki page produced by Claude (persisted to Git + Supabase)."""

    model_config = ConfigDict(extra="forbid")

    slug: str = Field(min_length=1, description="URL-safe unique slug for file name and wikilinks")
    title: str = Field(min_length=1)
    page_type: Literal["concept", "entity", "source_summary", "output", "index"]
    content_markdown: str = Field(description="Markdown body only (no YAML fence)")
    frontmatter: dict[str, Any] = Field(default_factory=dict, description="YAML frontmatter fields as JSON object")

    @field_validator("frontmatter", mode="before")
    @classmethod
    def _normalize_frontmatter(cls, value: Any) -> dict[str, Any]:
        """Accept JSON object or YAML/JSON string and normalize to mapping."""
        if value is None:
            return {}
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            raw = value.strip()
            if not raw:
                return {}
            try:
                parsed_json = json.loads(raw)
                if isinstance(parsed_json, dict):
                    return parsed_json
            except json.JSONDecodeError:
                pass
            parsed_yaml = yaml.safe_load(raw)
            if isinstance(parsed_yaml, dict):
                return parsed_yaml
            msg = "frontmatter string must parse to an object"
            raise ValueError(msg)
        msg = "frontmatter must be an object or YAML/JSON string"
        raise ValueError(msg)
