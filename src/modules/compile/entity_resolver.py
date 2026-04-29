"""Entity-resolution scaffold for Karpathy's **Compile** loop.

This module sits after ``wiki_generator`` materializes pages and before later
Compile-loop safeguards enrich or challenge them. The long-term role is to
detect near-duplicate entity pages and surface merge suggestions to a human,
keeping the Company Brain coherent without allowing auto-merges.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from pydantic import BaseModel, ConfigDict, Field
from supabase import Client

from src.modules.compile.models import WikiPage

DEFAULT_ENTITY_SIMILARITY_THRESHOLD = 0.80


class MergeSuggestion(BaseModel):
    """Human-review suggestion for two entity pages that likely represent one thing."""

    model_config = ConfigDict(extra="forbid")

    existing_page_id: str = Field(min_length=1)
    new_page_id: str = Field(min_length=1)
    similarity_score: float = Field(ge=0.0, le=1.0)
    reason: str = Field(min_length=1)


def _entity_summary(page: WikiPage) -> str:
    """Extract the shortest durable summary scaffold for future embedding work."""
    summary = page.frontmatter.get("summary")
    if isinstance(summary, str) and summary.strip():
        return summary.strip()
    return page.content_markdown.strip()[:500]


def resolve_entity_merge_suggestions(
    client: Client,
    *,
    tenant_id: str,
    pages: Sequence[WikiPage],
    slug_to_wiki_page_id: Mapping[str, str],
    similarity_threshold: float = DEFAULT_ENTITY_SIMILARITY_THRESHOLD,
) -> list[MergeSuggestion]:
    """Return HITL merge suggestions for near-duplicate entity pages.

    Placeholder only: the future implementation will embed each new entity title
    plus summary, compare it against existing ``wiki_pages`` rows where
    ``page_type='entity'``, and emit suggestions when cosine similarity exceeds
    ``similarity_threshold``.
    """
    _ = client
    _ = tenant_id
    _ = similarity_threshold

    entity_candidates = [
        page for page in pages if page.page_type == "entity" and slug_to_wiki_page_id.get(page.slug)
    ]
    for page in entity_candidates:
        _ = _entity_summary(page)

    return []
