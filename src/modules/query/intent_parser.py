"""
intent_parser.py — Detects output format intent from natural language query.

Runs before synthesis. Pure string matching — no LLM, no cost.
Strips format directive from query before sending to synthesizer
so the LLM doesn't get confused by format instructions.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class IntentParseResult:
    requested_format: Optional[str]  # None = default response_card
    clean_query: str  # Query with format directive stripped


# (pattern, format_id) — longer / more specific patterns first
_INTENT_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bmind\s+map\b", re.I), "mindmap"),
    (re.compile(r"\bmapa\s+my[sś]li\b", re.I), "mindmap"),
    (re.compile(r"\bmapa\s+wiedzy\b", re.I), "mindmap"),
    (re.compile(r"\bpoka[zż]\s+relacje\b", re.I), "mindmap"),
    (re.compile(r"/mindmap\b", re.I), "mindmap"),
    (re.compile(r"\bmindmap\b", re.I), "mindmap"),
    (re.compile(r"\bpoka[zż]\s+powi[aą]zania\b", re.I), "graph"),
    (re.compile(r"\bjak\s+po[lł][aą]czone\b", re.I), "graph"),
    (re.compile(r"/graph\b", re.I), "graph"),
    (re.compile(r"\bdiagram\b", re.I), "graph"),
    (re.compile(r"\bgraf\b", re.I), "graph"),
    (re.compile(r"\bgraph\b", re.I), "graph"),
    (re.compile(r"\bcomparison\s+table\b", re.I), "comparison_table"),
    (re.compile(r"\bpor[óo]wnaj\b", re.I), "comparison_table"),
    (re.compile(r"\bversus\b", re.I), "comparison_table"),
    (re.compile(r"\bvs\.?\b", re.I), "comparison_table"),
    (re.compile(r"/table\b", re.I), "comparison_table"),
    (re.compile(r"\btabela\b", re.I), "comparison_table"),
    (re.compile(r"\btable\b", re.I), "comparison_table"),
    (re.compile(r"\bcompare\b", re.I), "comparison_table"),
    (re.compile(r"\bsummary\s+card\b", re.I), "card"),
    (re.compile(r"\bpodsumuj\b", re.I), "card"),
    (re.compile(r"\bskr[óo]t\b", re.I), "card"),
    (re.compile(r"/card\b", re.I), "card"),
    (re.compile(r"\bstep\s+by\s+step\b", re.I), "protocol"),
    (re.compile(r"\bkrok\s+po\s+kroku\b", re.I), "protocol"),
    (re.compile(r"\bprotok[oó][lł]\b", re.I), "protocol"),
    (re.compile(r"/protocol\b", re.I), "protocol"),
]


def _collapse_ws(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


class IntentParser:
    """Strip format directives and detect requested structured view."""

    def parse(self, query_text: str) -> IntentParseResult:
        raw = (query_text or "").strip()
        if not raw:
            return IntentParseResult(requested_format=None, clean_query="")

        chosen_format: Optional[str] = None
        working = raw

        for rx, fmt in _INTENT_PATTERNS:
            if rx.search(working):
                chosen_format = fmt
                working = rx.sub(" ", working)
                break

        clean = _collapse_ws(working)
        if not clean:
            clean = raw

        return IntentParseResult(requested_format=chosen_format, clean_query=clean or raw)
