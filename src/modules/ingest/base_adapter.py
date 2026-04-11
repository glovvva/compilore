"""Abstract ingest adapter for Karpathy's **Ingest** loop.

The Ingest loop reads raw uploads and produces normalized text (and metadata) for
the **Compile** loop. Adapters isolate format-specific parsing so the core engine
stays blind to file types — the sacred modularity rule from the project brief.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from .models import IngestResult


class BaseIngestAdapter(ABC):
    """Protocol-style base for pluggable document readers."""

    @abstractmethod
    def can_handle(self, path: Path) -> bool:
        """Return True if this adapter should process the given path."""

    @abstractmethod
    def extract(self, path: Path) -> IngestResult:
        """Parse file into a typed ``IngestResult``."""


def placeholder_supported_extensions() -> frozenset[str]:
    """Reserved for future registry of ingest adapters by extension."""
    return frozenset()
