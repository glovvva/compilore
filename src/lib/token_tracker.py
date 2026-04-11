"""Token and cost tracking for LLM calls.

Feeds LangSmith and persistent ``wiki_log`` rows; supports page-ratio monitoring
(output vs concept pages) per brief §5.3. Cross-cutting concern shared by all four
loops where APIs are invoked.
"""

from __future__ import annotations

from decimal import Decimal


def record_usage(operation: str, input_tokens: int, output_tokens: int, cost_usd: Decimal) -> None:
    """Placeholder: persist usage metrics (implementation deferred)."""
    _ = (operation, input_tokens, output_tokens, cost_usd)
    return None
