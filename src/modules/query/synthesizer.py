"""Answer synthesizer for the **Query** loop."""

from __future__ import annotations

import os
import re
from pathlib import Path

import anthropic

from src.lib.anthropic_cost import anthropic_usd_from_usage
from src.lib.json_llm import parse_json_object
from src.lib.supabase import create_supabase_client, fetch_wiki_slugs_for_page_ids
from src.modules.query.models import ChunkResult, SynthesisResult

SYNTHESIS_MODEL = "claude-sonnet-4-20250514"


def _load_query_synthesize_prompt() -> str:
    path = Path(__file__).resolve().parents[2] / "config" / "prompts" / "query_synthesize.md"
    return path.read_text(encoding="utf-8")


def _normalize_citations(raw: list[object]) -> list[str]:
    out: list[str] = []
    for item in raw:
        if not isinstance(item, str):
            continue
        s = item.strip()
        m = re.match(r"^\[\[([^[\]]+)\]\]$", s)
        if m:
            s = m.group(1).strip()
        if s and s not in out:
            out.append(s)
    return out


def synthesize_answer(
    question: str,
    chunks: list[ChunkResult],
    tenant_id: str,
    *,
    api_key: str | None = None,
) -> SynthesisResult:
    """Call Claude with retrieved chunks; return structured synthesis + usage."""
    key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        msg = "ANTHROPIC_API_KEY is not set"
        raise RuntimeError(msg)

    client = create_supabase_client()
    page_ids = list({c.wiki_page_id for c in chunks})
    slug_by_page = fetch_wiki_slugs_for_page_ids(client, tenant_id=tenant_id, wiki_page_ids=page_ids)

    chunk_blocks: list[str] = []
    for i, ch in enumerate(chunks):
        slug = slug_by_page.get(ch.wiki_page_id, ch.wiki_page_id)
        chunk_blocks.append(
            f"### Chunk {i + 1} (wiki_slug=`{slug}`)\n{ch.chunk_text.strip()}",
        )
    context = "\n\n".join(chunk_blocks) if chunk_blocks else "(no chunks retrieved)"

    system = _load_query_synthesize_prompt()
    user = f"## User question\n{question}\n\n## Retrieved Wiki chunks\n{context}"

    ac = anthropic.Anthropic(api_key=key)
    message = ac.messages.create(
        model=SYNTHESIS_MODEL,
        max_tokens=4096,
        system=system,
        messages=[{"role": "user", "content": user}],
    )

    in_tok = int(message.usage.input_tokens)
    out_tok = int(message.usage.output_tokens)
    cost = float(
        anthropic_usd_from_usage(
            in_tok,
            out_tok,
            env_input_key="QUERY_SONNET_INPUT_PER_MTOK",
            env_output_key="QUERY_SONNET_OUTPUT_PER_MTOK",
            default_input_per_mtok="3",
            default_output_per_mtok="15",
        ),
    )

    text_parts: list[str] = []
    for block in message.content:
        if getattr(block, "type", None) == "text":
            text_parts.append(block.text)
    raw_text = "".join(text_parts).strip()
    parsed = parse_json_object(raw_text)
    answer = str(parsed.get("answer_markdown") or "").strip()
    citations_raw = parsed.get("citations")
    citations = _normalize_citations(list(citations_raw)) if isinstance(citations_raw, list) else []

    return SynthesisResult(
        answer_markdown=answer,
        citations=citations,
        input_tokens=in_tok,
        output_tokens=out_tok,
        cost_usd=cost,
    )
