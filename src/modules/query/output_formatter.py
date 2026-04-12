"""
output_formatter.py — Transforms synthesized answers into structured output formats.

Handles: response_card, mindmap, graph, comparison_table, card, protocol.
For mindmap and graph: calls Claude to reformat answer as Mermaid/Markmap syntax.
For comparison_table: Claude reformats as HTML table.
For card: Claude distills to headline + 3 bullets + source chips.
For response_card: default format, structures existing answer into F-pattern card.

Cost per format transformation: ~$0.005 (small Claude call, short output).
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

import anthropic

from src.lib.anthropic_cost import anthropic_usd_from_usage
from src.lib.json_llm import parse_json_object, strip_json_fence
from src.lib.supabase import create_supabase_client
from src.modules.query.format_evaluator import FormatEvalResult
from src.modules.query.gatekeeper import GATEKEEPER_MODEL
from src.modules.query.models import ChunkResult

_PROMPTS = Path(__file__).resolve().parents[2] / "config" / "prompts"

_FORMAT_MODEL = os.environ.get("QUERY_FORMAT_MODEL", GATEKEEPER_MODEL)


def _load_prompt(name: str) -> str:
    return (_PROMPTS / name).read_text(encoding="utf-8")


def _call_claude(system: str, user: str) -> tuple[str, float]:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        msg = "ANTHROPIC_API_KEY is not set"
        raise RuntimeError(msg)
    ac = anthropic.Anthropic(api_key=key)
    message = ac.messages.create(
        model=_FORMAT_MODEL,
        max_tokens=2048,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    parts: list[str] = []
    for block in message.content:
        if getattr(block, "type", None) == "text":
            parts.append(block.text)
    text = "".join(parts).strip()
    cost = float(
        anthropic_usd_from_usage(
            int(message.usage.input_tokens),
            int(message.usage.output_tokens),
            env_input_key="GATE_HAIKU_INPUT_PER_MTOK",
            env_output_key="GATE_HAIKU_OUTPUT_PER_MTOK",
            default_input_per_mtok="1",
            default_output_per_mtok="5",
        ),
    )
    return text, cost


def fetch_last_top_page_confidence(tenant_id: str) -> float | None:
    """Return ``top_page_confidence`` from the latest ``query_response_card`` log row."""
    client = create_supabase_client()
    res = (
        client.table("wiki_log")
        .select("details")
        .eq("tenant_id", tenant_id)
        .eq("operation", "query_response_card")
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    rows = getattr(res, "data", None) or []
    if not rows:
        return None
    det = rows[0].get("details") or {}
    if isinstance(det, dict) and "top_page_confidence" in det:
        try:
            return float(det["top_page_confidence"])
        except (TypeError, ValueError):
            return None
    return None


def compute_top_retrieval_confidence(
    chunks: list[ChunkResult],
    page_rows: list[dict[str, Any]],
) -> float:
    by_id = {str(r.get("id") or ""): float(r.get("confidence") or 0.0) for r in page_rows}
    ordered = sorted(chunks, key=lambda c: -c.rrf_score)
    for c in ordered:
        v = by_id.get(c.wiki_page_id)
        if v is not None:
            return v
    return 0.0


def format_confidence_delta(previous: float | None, current: float) -> str | None:
    if previous is None:
        return None
    delta = round(current - previous, 2)
    if abs(delta) < 0.01:
        return None
    sign = "+" if delta > 0 else ""
    return f"{sign}{delta:.2f}"


def generate_headline(question: str, answer_markdown: str) -> tuple[str, float]:
    system = _load_prompt("format_response_card_headline.md")
    excerpt = (answer_markdown or "")[:6000]
    user = f"## Question\n{question}\n\n## Answer\n{excerpt}"
    text, cost = _call_claude(system, user)
    one = re.sub(r"\s+", " ", text).strip()
    if len(one) > 220:
        one = one[:217].rsplit(" ", 1)[0] + "…"
    return one or "Summary unavailable.", cost


def build_response_card(
    *,
    tenant_id: str,
    answer_id: str,
    question: str,
    answer_markdown: str,
    source_chips: list[dict[str, Any]],
    gatekeeper_confidence: float,
    gatekeeper_should_save: bool,
    saved_to_wiki: bool,
    gatekeeper_reasoning: str,
    cost_usd: float,
    format_eval: FormatEvalResult,
    requested_format: str | None,
    chunks: list[ChunkResult],
    page_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    prev = fetch_last_top_page_confidence(tenant_id)
    current_top = compute_top_retrieval_confidence(chunks, page_rows)
    delta = format_confidence_delta(prev, current_top)

    try:
        headline, h_cost = generate_headline(question, answer_markdown)
    except Exception:
        headline = ((answer_markdown or "").strip()[:120] + "…") if len((answer_markdown or "").strip()) > 120 else (answer_markdown or "No answer.").strip()
        h_cost = 0.0
    total_cost = float(cost_usd) + float(h_cost)

    reasoning_sub = {k: format_eval.reasoning[k] for k in format_eval.suggested_formats if k in format_eval.reasoning}

    return {
        "format": "response_card",
        "headline": headline,
        "body": answer_markdown,
        "source_chips": source_chips,
        "confidence": float(gatekeeper_confidence),
        "confidence_delta": delta,
        "save_to_wiki": saved_to_wiki,
        "gatekeeper_passed": gatekeeper_should_save,
        "suggested_formats": list(format_eval.suggested_formats),
        "format_reasoning": reasoning_sub,
        "gatekeeper_reasoning": gatekeeper_reasoning,
        "cost_usd": round(total_cost, 6),
        "answer_id": answer_id,
        "requested_format": requested_format,
        "top_page_confidence": current_top,
    }


def log_response_card_anchor(tenant_id: str, card: dict[str, Any]) -> None:
    """Persist minimal row for confidence-delta chaining on the next query."""
    from src.lib.supabase import insert_wiki_log_row

    try:
        insert_wiki_log_row(
            client=create_supabase_client(),
            tenant_id=tenant_id,
            operation="query_response_card",
            details={
                "answer_id": card.get("answer_id"),
                "top_page_confidence": card.get("top_page_confidence"),
                "query_snippet": str(card.get("_query_snippet") or "")[:160],
            },
            module="output_formatter",
        )
    except Exception:
        pass


def transform_answer_to_format(
    *,
    answer_text: str,
    source_chips: list[dict[str, Any]],
    query_text: str,
    format_id: str,
) -> dict[str, Any]:
    """Run a focused Claude transform for alternate views (``POST /query/format``)."""
    fmt = (format_id or "").strip().lower()
    chips_txt = json.dumps(source_chips, ensure_ascii=False)[:4000]
    base_user = (
        f"## Question / context\n{query_text}\n\n"
        f"## Source chips (JSON)\n{chips_txt}\n\n"
        f"## Answer\n{answer_text}\n"
    )

    if fmt == "mindmap":
        system = _load_prompt("format_mindmap.md")
        md, cost = _call_claude(system, base_user)
        return {"format": "mindmap", "markmap_markdown": strip_json_fence(md), "cost_usd": cost}

    if fmt == "graph":
        system = _load_prompt("format_graph.md")
        raw, cost = _call_claude(system, base_user)
        mer = strip_json_fence(raw)
        mer = mer.removeprefix("```mermaid").removesuffix("```").strip()
        return {"format": "graph", "mermaid_syntax": mer, "cost_usd": cost}

    if fmt == "comparison_table":
        system = _load_prompt("format_comparison_table.md")
        html, cost = _call_claude(system, base_user)
        html_clean = strip_json_fence(html)
        cap_m = re.search(r"<caption[^>]*>(.*?)</caption>", html_clean, re.I | re.DOTALL)
        caption = re.sub(r"\s+", " ", cap_m.group(1)).strip() if cap_m else ""
        return {
            "format": "comparison_table",
            "html_table": html_clean,
            "caption": caption,
            "cost_usd": cost,
        }

    if fmt == "card":
        system = _load_prompt("format_card.md")
        raw, cost = _call_claude(system, base_user)
        obj = parse_json_object(raw)
        bullets = obj.get("bullets")
        if not isinstance(bullets, list):
            bullets = []
        bullets = [str(b) for b in bullets[:3]]
        while len(bullets) < 3:
            bullets.append("—")
        return {
            "format": "card",
            "headline": str(obj.get("headline") or "")[:500],
            "bullets": bullets[:3],
            "source_chips": source_chips,
            "cost_usd": cost,
        }

    if fmt == "protocol":
        system = _load_prompt("format_protocol.md")
        raw, cost = _call_claude(system, base_user)
        obj = parse_json_object(raw)
        steps = obj.get("steps")
        if not isinstance(steps, list):
            steps = []
        steps = [str(s) for s in steps][:12]
        return {
            "format": "protocol",
            "title": str(obj.get("title") or "Protocol"),
            "steps": steps,
            "cost_usd": cost,
        }

    if fmt == "response_card":
        return {
            "format": "response_card",
            "headline": answer_text[:120] + ("…" if len(answer_text) > 120 else ""),
            "body": answer_text,
            "source_chips": source_chips,
            "cost_usd": 0.0,
        }

    msg = f"Unsupported format: {format_id!r}"
    raise ValueError(msg)
