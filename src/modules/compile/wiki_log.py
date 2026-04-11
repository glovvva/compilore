"""Append-only operations log in ``wiki/log.md`` (human-readable audit trail)."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path


def append_compile_cost_line(
    wiki_root: Path,
    *,
    document_title: str,
    cost_usd: Decimal,
    input_tokens: int,
    output_tokens: int,
    page_count: int,
    model: str,
) -> None:
    """Append one line documenting a Claude compile call and approximate cost."""
    log_path = wiki_root / "log.md"
    if not log_path.is_file():
        log_path.write_text(
            "# Wiki operation log\n\n"
            "Append-only chronology of ingest, compile, query, and lint operations.\n\n"
            "## Compile cost log (API)\n\n",
            encoding="utf-8",
        )

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = (
        f"- **{ts}** `compile` **{document_title}** — "
        f"cost ${cost_usd:.6f} USD, tokens {input_tokens}/{output_tokens}, "
        f"pages {page_count}, model `{model}`\n"
    )
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(line)


def append_query_claude_cost_line(
    wiki_root: Path,
    *,
    operation: str,
    detail: str,
    cost_usd: Decimal,
    input_tokens: int,
    output_tokens: int,
    model: str,
) -> None:
    """Append one line for a Claude call during **Query** (synthesis or gatekeeper)."""
    log_path = wiki_root / "log.md"
    if not log_path.is_file():
        log_path.write_text(
            "# Wiki operation log\n\n"
            "Append-only chronology of ingest, compile, query, and lint operations.\n\n"
            "## Compile cost log (API)\n\n",
            encoding="utf-8",
        )

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = (
        f"- **{ts}** `{operation}` **{detail}** — "
        f"cost ${cost_usd:.6f} USD, tokens {input_tokens}/{output_tokens}, model `{model}`\n"
    )
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(line)
