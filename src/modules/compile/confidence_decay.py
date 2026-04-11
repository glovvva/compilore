"""Confidence decay for compiled Wiki pages (**Compile** / maintenance).

Implements the monthly -5% decay and archive threshold (<0.30) described in the
brief. Typically triggered by n8n; keeps stale knowledge from dominating retrieval
without running autonomous **Lint** in a tight loop.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Sequence


def apply_monthly_decay(confidence: Decimal, months_since_verified: int) -> Decimal:
    """Placeholder: return decayed confidence (no business logic yet)."""
    _ = months_since_verified
    return confidence


def pages_below_archive_threshold(slugs: Sequence[str], threshold: Decimal) -> list[str]:
    """Placeholder: filter slugs that should move to archive (implementation deferred)."""
    _ = (slugs, threshold)
    return []
