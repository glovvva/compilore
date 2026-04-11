"""Anthropic (Claude) API wrapper for Compilore.

Used in **Compile**, **Query** synthesis, **Gatekeeper**, and **Lint** contradiction
flows. Model choice (e.g. Claude 3.7 Sonnet) follows the locked decisions in the
brief; token usage should feed ``token_tracker`` and ``wiki_log``.
"""

from __future__ import annotations

from typing import Any


def create_anthropic_client(api_key: str) -> Any:
    """Placeholder: return Anthropic SDK client (implementation deferred)."""
    _ = api_key
    return None
