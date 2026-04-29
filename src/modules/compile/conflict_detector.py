"""Compile-time conflict-detection scaffold for Karpathy's **Compile** loop.

This module is intended to sit after entity-resolution. Its future role is to
look for pages that are semantically close to existing knowledge but express
different factual claims, then push those cases into a human review queue
instead of silently letting contradictions accumulate inside the Company Brain.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from pydantic import BaseModel, ConfigDict, Field
from supabase import Client

from src.modules.compile.models import WikiPage

DEFAULT_CONFLICT_SIMILARITY_THRESHOLD = 0.70


class ConflictFlag(BaseModel):
    """Potential contradiction that should be reviewed by a human operator."""

    model_config = ConfigDict(extra="forbid")

    page_id: str = Field(min_length=1)
    conflicting_page_id: str = Field(min_length=1)
    conflicting_claims: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)


def detect_compile_time_conflicts(
    client: Client,
    *,
    tenant_id: str,
    pages: Sequence[WikiPage],
    slug_to_wiki_page_id: Mapping[str, str],
    similarity_threshold: float = DEFAULT_CONFLICT_SIMILARITY_THRESHOLD,
) -> list[ConflictFlag]:
    """Return HITL conflict candidates for newly compiled concept/entity pages.

    Placeholder only: the future implementation will query hybrid search with a
    page summary, inspect semantically close pages, and emit ``ConflictFlag``
    rows when similar pages appear to disagree factually.
    """
    _ = client
    _ = tenant_id
    _ = similarity_threshold

    candidate_pages = [
        page
        for page in pages
        if page.page_type in {"concept", "entity"} and slug_to_wiki_page_id.get(page.slug)
    ]
    _ = candidate_pages
    return []


def queue_conflicts_for_hitl_review(
    *,
    tenant_id: str,
    document_id: str,
    conflict_flags: Sequence[ConflictFlag],
    webhook_url: str | None = None,
) -> None:
    """Placeholder notification hook for Slack via n8n webhook.

    The future implementation will serialize ``conflict_flags`` to the review
    payload expected by n8n/Slack. For now this is an intentional no-op so the
    graph shape exists without introducing outbound side effects.
    """
    _ = tenant_id
    _ = document_id
    _ = conflict_flags
    _ = webhook_url
