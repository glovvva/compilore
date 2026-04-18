"""Wiki generator for Karpathy's **Compile** loop.

Turns ingested text into interconnected Markdown pages using Claude and
``compile_wiki.md``. Each successful compile run is followed by Git + index updates
from the LangGraph pipeline.
"""

# Technical Advisor ICP note:
# - Adds page types: `product_entity`, `manufacturer_entity`.
# - These are handled by `compile_technical_catalog.md` prompt instructions.
# - The `wiki_generator.py` core loop is unchanged: it receives pages from the
#   prompt pipeline, validates them, and stores them.
# - `technical_parameters` JSONB field in frontmatter is passed through as-is.

from __future__ import annotations

import json
import os
import re
from decimal import Decimal
from typing import Any

import anthropic

from src.lib.supabase import schedule_insert_wiki_log_row
from src.modules.compile.models import WikiPage
from src.modules.compile.prompts import load_compile_prompt
from src.modules.ingest.models import IngestResult

DEFAULT_MODEL = "claude-sonnet-4-20250514"


def _strip_json_fence(text: str) -> str:
    text = text.strip()
    m = re.match(r"^```(?:json)?\s*\n?(.*?)\n?```\s*$", text, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return text


def _anthropic_cost_usd(input_tokens: int, output_tokens: int) -> Decimal:
    """Approximate USD from usage; override with env COMPILE_ANTHROPIC_* per MTok."""
    in_rate = Decimal(os.environ.get("COMPILE_ANTHROPIC_INPUT_PER_MTOK", "3"))
    out_rate = Decimal(os.environ.get("COMPILE_ANTHROPIC_OUTPUT_PER_MTOK", "15"))
    return (Decimal(input_tokens) / Decimal(1_000_000)) * in_rate + (
        Decimal(output_tokens) / Decimal(1_000_000)
    ) * out_rate


def compile_wiki_pages(
    ingest: IngestResult,
    *,
    api_key: str | None = None,
    model: str = DEFAULT_MODEL,
) -> tuple[list[WikiPage], int, int, Decimal]:
    """Call Claude with ingest content; parse and validate JSON array of ``WikiPage``.

    Returns ``(pages, input_tokens, output_tokens, cost_usd_approx)``.
    """
    key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        msg = "ANTHROPIC_API_KEY is not set"
        raise RuntimeError(msg)

    system = load_compile_prompt()
    user_payload: dict[str, Any] = {
        "source_path": str(ingest.source_path),
        "doc_type": ingest.doc_type,
        "frontmatter": ingest.frontmatter,
        "body": ingest.body,
    }
    user_text = (
        "Compile the following ingested document into the JSON array of wiki pages "
        "as specified in your system instructions. Respond with JSON only.\n\n"
        + json.dumps({"ingested_document": user_payload}, ensure_ascii=False)
    )

    client = anthropic.Anthropic(api_key=key)
    message = client.messages.create(
        model=model,
        max_tokens=16_384,
        system=system,
        messages=[{"role": "user", "content": user_text}],
    )

    input_tokens = int(message.usage.input_tokens)
    output_tokens = int(message.usage.output_tokens)
    cost = _anthropic_cost_usd(input_tokens, output_tokens)

    blocks = getattr(message, "content", []) or []
    text_parts: list[str] = []
    for block in blocks:
        if getattr(block, "type", None) == "text":
            text_parts.append(block.text)
    raw = "".join(text_parts).strip()
    if not raw:
        msg = "Claude returned no text content"
        raise RuntimeError(msg)

    parsed = json.loads(_strip_json_fence(raw))
    if not isinstance(parsed, list):
        msg = "Claude JSON root must be an array of wiki pages"
        raise ValueError(msg)

    pages = [WikiPage.model_validate(item) for item in parsed]
    return pages, input_tokens, output_tokens, cost


def schedule_wiki_generator_compile_log(
    *,
    tenant_id: str,
    document_id: str,
    pages: list[WikiPage],
    input_tokens: int,
    output_tokens: int,
    cost_usd: float,
    pdf_extract_log: dict[str, Any] | None = None,
) -> None:
    """After compile pages are persisted, log ``wiki_log`` for the wiki_generator module."""
    details: dict[str, Any] = {
        "document_id": str(document_id),
        "pages_created": len(pages),
        "page_types": [p.page_type for p in pages],
    }
    if pdf_extract_log:
        details.update(pdf_extract_log)
    schedule_insert_wiki_log_row(
        tenant_id=tenant_id,
        operation="compile",
        module="wiki_generator",
        details=details,
        tokens_used=int(input_tokens) + int(output_tokens),
        cost_usd=float(cost_usd),
    )
