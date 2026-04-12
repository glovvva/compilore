"""Typed results for the Lint loop."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class OrphanResult:
    page_slug: str
    page_title: str
    broken_links: list[str]
    checked_at: datetime


@dataclass
class StaleResult:
    slug: str
    title: str
    days_since_update: int
    confidence: float
    page_type: str


@dataclass
class DuplicateCandidate:
    page_a_slug: str
    page_a_title: str
    page_b_slug: str
    page_b_title: str
    similarity_score: float
    suggested_action: str  # "merge" | "review"


@dataclass
class ContradictionCandidate:
    page_a: str
    page_b: str
    suspected_conflict: str


@dataclass
class ContradictionPlan:
    page_a: str
    page_b: str
    is_contradiction: bool
    conflict_quote_a: str = ""
    conflict_quote_b: str = ""
    authoritative_page: str = ""
    merge_instructions: str = ""
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class LintReport:
    tenant_id: str
    checked_at: str
    orphans: list[dict[str, Any]]
    stale_pages: list[dict[str, Any]]
    duplicate_candidates: list[dict[str, Any]]
    contradiction_candidates: list[dict[str, Any]]
    contradiction_plans: list[dict[str, Any]]
    merge_results: list[dict[str, Any]]
    errors: list[str] = field(default_factory=list)
    thread_id: str | None = None
    pending_resolution: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_id": self.tenant_id,
            "checked_at": self.checked_at,
            "orphans": self.orphans,
            "stale_pages": self.stale_pages,
            "duplicate_candidates": self.duplicate_candidates,
            "contradiction_candidates": self.contradiction_candidates,
            "contradiction_plans": self.contradiction_plans,
            "merge_results": self.merge_results,
            "errors": self.errors,
            "thread_id": self.thread_id,
            "pending_resolution": self.pending_resolution,
        }


@dataclass
class DecayReport:
    tenant_id: str
    ran_at: str
    pages_decayed: int
    pages_archived: int
    archived_slugs: list[str]
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_id": self.tenant_id,
            "ran_at": self.ran_at,
            "pages_decayed": self.pages_decayed,
            "pages_archived": self.pages_archived,
            "archived_slugs": self.archived_slugs,
            "errors": self.errors,
        }
