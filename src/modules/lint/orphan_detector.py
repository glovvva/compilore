"""Orphan / broken link detection for the **Lint** loop.

Deterministic RegEx-based checks for broken ``[[wikilinks]]`` and similar — cheap
and safe to run on a schedule. **Lint is on-demand / scheduled, never a tight
autonomous agent loop** (brief §1.3, §5.6).
"""

from __future__ import annotations

from pathlib import Path


def find_orphan_references(wiki_root: Path) -> list[str]:
    """Placeholder: return list of broken link descriptions or paths."""
    _ = wiki_root
    return []
