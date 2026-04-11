"""Contradiction checking for the **Lint** loop.

Uses Claude with ``lint_contradiction.md`` to surface conflicting statements across
Wiki pages. Expensive and **on-demand only** — invoked explicitly or via scheduled
jobs, not continuous background agents.
"""

from __future__ import annotations

from typing import Any


def detect_contradictions(wiki_page_contents: dict[str, str]) -> list[dict[str, Any]]:
    """Placeholder: return structured conflict reports (implementation deferred)."""
    _ = wiki_page_contents
    return []
