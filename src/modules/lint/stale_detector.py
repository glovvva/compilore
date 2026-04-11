"""Stale page detection for the **Lint** loop.

Flags pages by ``last_verified`` / modification dates per maintenance policy in
the brief. Feeds human review or recompilation — complements confidence decay.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path


def find_stale_pages(wiki_root: Path, as_of: datetime) -> list[str]:
    """Placeholder: return slugs or paths that exceed freshness thresholds."""
    _ = (wiki_root, as_of)
    return []
