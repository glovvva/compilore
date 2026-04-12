"""
format_evaluator.py — Rule-based output format suggester.

Analyzes the shape of a synthesized answer and the wiki_pages retrieved
to suggest 1-2 relevant output formats as clickable chips in the UI.

Zero LLM cost. Zero latency. Pure heuristics.
Tracks suggestions in wiki_log for Phase 2 LLM-based evaluator training.

Heuristic rules:
- ≥3 entities with parallel attributes in answer → suggest "comparison_table"
- ≥4 wiki_pages of different page_types in search results → suggest "mindmap"
- ≥3 sequential steps detected (numbered list, "first/then/finally") → suggest "protocol"
- Single long answer (>400 words) with no lists → suggest "card"
- Multiple [[wikilinks]] to entity pages → suggest "graph"
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from src.lib.supabase import create_supabase_client, insert_wiki_log_row

WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")
_STEP_WORDS = re.compile(
    r"\b(?:first|second|third|then|next|finally|lastly|step\s+\d+)\b",
    re.I,
)
_NUMBERED_LINE = re.compile(r"^\s*\d+[\).\s]\s+\S", re.M)
_LABEL_VALUE_LINES = re.compile(r"^\s*[^\n:]{1,50}:\s*[^\n]{2,}", re.M)
_MD_LIST = re.compile(r"(?m)^\s*(?:[-*+]|\d+[\).\s])\s+\S")


@dataclass
class FormatEvalInput:
    answer_text: str
    wiki_pages_retrieved: list[dict]  # each has page_type, slug, title
    query_text: str


@dataclass
class FormatEvalResult:
    suggested_formats: list[str]
    confidence: dict[str, float]
    reasoning: dict[str, str]


def _word_count(text: str) -> int:
    return len(re.findall(r"\S+", text or ""))


def _rule_comparison_table(text: str) -> tuple[str, float, str] | None:
    lines = _LABEL_VALUE_LINES.findall(text or "")
    if len(lines) >= 3:
        return (
            "comparison_table",
            0.82,
            "Several labeled attribute lines — good fit for a comparison table.",
        )
    low = (text or "").lower()
    if (" vs " in low or " versus " in low) and _word_count(text) > 80:
        return ("comparison_table", 0.72, "Versus-style phrasing detected in the answer.")
    return None


def _rule_mindmap(pages: list[dict]) -> tuple[str, float, str] | None:
    types = {str(p.get("page_type") or "").lower() for p in pages if p.get("page_type")}
    types.discard("")
    if len(types) >= 4:
        return (
            "mindmap",
            0.88,
            f"{len(types)} distinct page types in retrieval — map view can show structure.",
        )
    return None


def _rule_protocol(text: str) -> tuple[str, float, str] | None:
    t = text or ""
    n_num = len(_NUMBERED_LINE.findall(t))
    n_kw = len(_STEP_WORDS.findall(t))
    if n_num >= 3:
        return ("protocol", 0.85, "Numbered steps detected — protocol layout fits.")
    if n_kw >= 3:
        return ("protocol", 0.78, "Sequential language (first/then/finally…) — protocol view.")
    return None


def _rule_card(text: str) -> tuple[str, float, str] | None:
    if _word_count(text) <= 400:
        return None
    if _MD_LIST.search(text or ""):
        return None
    return ("card", 0.7, "Long prose without lists — summary card reduces cognitive load.")


def _rule_graph(text: str, pages: list[dict]) -> tuple[str, float, str] | None:
    slugs = {str(p.get("slug") or "") for p in pages}
    entity_slugs = {
        str(p.get("slug") or "")
        for p in pages
        if str(p.get("page_type") or "").lower() == "entity"
    }
    linked = [m.group(1).strip() for m in WIKILINK_RE.finditer(text or "")]
    linked_set = set(linked)
    hits = len(linked_set & entity_slugs) if entity_slugs else 0
    if len(linked) >= 3 and (hits >= 2 or len(linked_set & slugs) >= 3):
        return (
            "graph",
            0.8,
            "Multiple wikilinks tied to retrieved pages — graph view shows relationships.",
        )
    if len(linked) >= 4:
        return ("graph", 0.68, "Several wikilinks in the answer — try a link graph.")
    return None


class FormatEvaluator:
    """Score formats with deterministic rules; log suggestions for training."""

    def evaluate(self, inp: FormatEvalInput) -> FormatEvalResult:
        text = inp.answer_text or ""
        pages = inp.wiki_pages_retrieved or []
        candidates: list[tuple[str, float, str]] = []

        h = _rule_comparison_table(text)
        if h:
            candidates.append(h)
        h = _rule_mindmap(pages)
        if h:
            candidates.append(h)
        h = _rule_protocol(text)
        if h:
            candidates.append(h)
        h = _rule_card(text)
        if h:
            candidates.append(h)
        h = _rule_graph(text, pages)
        if h:
            candidates.append(h)

        candidates = [(f, c, r) for f, c, r in candidates if c >= 0.6]
        candidates.sort(key=lambda x: x[1], reverse=True)
        top = candidates[:2]

        conf = {f: c for f, c, _ in top}
        reason = {f: r for f, _, r in top}
        formats = [f for f, _, _ in top]

        return FormatEvalResult(
            suggested_formats=formats,
            confidence=conf,
            reasoning=reason,
        )

    def evaluate_and_log(self, tenant_id: str, inp: FormatEvalInput) -> FormatEvalResult:
        result = self.evaluate(inp)
        try:
            client = create_supabase_client()
            insert_wiki_log_row(
                client,
                tenant_id=tenant_id,
                operation="format_eval_suggest",
                details={
                    "suggested_formats": result.suggested_formats,
                    "confidence": result.confidence,
                    "reasoning": result.reasoning,
                    "query_snippet": (inp.query_text or "")[:200],
                },
                module="format_evaluator",
            )
        except Exception:
            pass
        return result
