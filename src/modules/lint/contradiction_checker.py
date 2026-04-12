"""
contradiction_checker.py — Detects contradictions between Wiki pages.

Part of the Lint loop (Loop 4). Claude-powered, on-demand only.
Uses 3-pass gated execution to prevent context bloat and hallucinated contradictions:
  Pass 1 (DETECT): List candidate conflict pairs — no resolving.
  Pass 2 (PLAN): For each pair, show contradiction + propose merge strategy.
  Pass 3 (IMPLEMENT): Only after human approval via HITL interrupt in lint_graph.py.

Cost: ~$0.40/run on a medium Wiki. NEVER run autonomously.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import anthropic

from src.lib.json_llm import strip_json_fence
from src.lib.supabase import create_supabase_client, ensure_tenant_exists
from src.modules.lint.models import ContradictionCandidate, ContradictionPlan
from src.modules.query.synthesizer import SYNTHESIS_MODEL

_PROMPTS_DIR = Path(__file__).resolve().parents[2] / "config" / "prompts"


def _load_prompt(name: str) -> str:
    path = _PROMPTS_DIR / name
    return path.read_text(encoding="utf-8")


def _page_summary(row: dict[str, Any]) -> str:
    fm = row.get("frontmatter") or {}
    if isinstance(fm, dict):
        s = fm.get("summary")
        if isinstance(s, str) and s.strip():
            return s.strip()[:500]
    body = str(row.get("content_markdown") or "").strip()
    return (body[:200] + "…") if len(body) > 200 else body


def _call_claude_json(system: str, user: str) -> str:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        msg = "ANTHROPIC_API_KEY is not set"
        raise RuntimeError(msg)
    ac = anthropic.Anthropic(api_key=key)
    message = ac.messages.create(
        model=SYNTHESIS_MODEL,
        max_tokens=4096,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    parts: list[str] = []
    for block in message.content:
        if getattr(block, "type", None) == "text":
            parts.append(block.text)
    return "".join(parts).strip()


def _parse_json_array(text: str) -> list[Any]:
    raw = strip_json_fence(text)
    data = json.loads(raw)
    if not isinstance(data, list):
        msg = "Expected JSON array at root"
        raise ValueError(msg)
    return data


def run_contradiction_detect_pass1(tenant_id: str) -> list[ContradictionCandidate]:
    """Pass 1: titles + summaries only → suspected pairs (JSON)."""
    client = create_supabase_client()
    ensure_tenant_exists(client, tenant_id)
    res = (
        client.table("wiki_pages")
        .select("slug,title,content_markdown,frontmatter,page_type")
        .eq("tenant_id", tenant_id)
        .execute()
    )
    rows = getattr(res, "data", None) or []
    catalog: list[dict[str, str]] = []
    for row in rows:
        slug = str(row.get("slug") or "").strip()
        if not slug:
            continue
        title = str(row.get("title") or slug).strip()
        catalog.append(
            {
                "slug": slug,
                "title": title,
                "summary": _page_summary(row),
            },
        )

    if not catalog:
        return []

    system = _load_prompt("lint_contradiction_detect.md")
    user = json.dumps({"pages": catalog}, ensure_ascii=False)
    raw = _call_claude_json(system, user)
    items = _parse_json_array(raw)
    out: list[ContradictionCandidate] = []
    for it in items:
        if not isinstance(it, dict):
            continue
        pa = str(it.get("page_a") or "").strip()
        pb = str(it.get("page_b") or "").strip()
        sc = str(it.get("suspected_conflict") or "").strip()
        if pa and pb and pa != pb:
            out.append(ContradictionCandidate(page_a=pa, page_b=pb, suspected_conflict=sc))
    return out


def run_contradiction_plan_pass2(
    tenant_id: str,
    candidates: list[ContradictionCandidate],
) -> list[ContradictionPlan]:
    """Pass 2: full content per suspected pair → structured merge plan JSON."""
    if not candidates:
        return []

    client = create_supabase_client()
    ensure_tenant_exists(client, tenant_id)
    system = _load_prompt("lint_contradiction_plan.md")
    plans: list[ContradictionPlan] = []

    for c in candidates:
        res_a = (
            client.table("wiki_pages")
            .select("slug,title,content_markdown")
            .eq("tenant_id", tenant_id)
            .eq("slug", c.page_a)
            .limit(1)
            .execute()
        )
        res_b = (
            client.table("wiki_pages")
            .select("slug,title,content_markdown")
            .eq("tenant_id", tenant_id)
            .eq("slug", c.page_b)
            .limit(1)
            .execute()
        )
        da = (getattr(res_a, "data", None) or [None])[0]
        db = (getattr(res_b, "data", None) or [None])[0]
        if not da or not db:
            continue

        payload = {
            "page_a": {"slug": c.page_a, "title": da.get("title"), "content": da.get("content_markdown")},
            "page_b": {"slug": c.page_b, "title": db.get("title"), "content": db.get("content_markdown")},
            "suspected_conflict": c.suspected_conflict,
        }
        user = json.dumps(payload, ensure_ascii=False)
        raw = _call_claude_json(system, user)
        obj = json.loads(strip_json_fence(raw))
        if not isinstance(obj, dict):
            continue
        is_c = bool(obj.get("is_contradiction", False))
        plans.append(
            ContradictionPlan(
                page_a=c.page_a,
                page_b=c.page_b,
                is_contradiction=is_c,
                conflict_quote_a=str(obj.get("conflict_quote_a") or ""),
                conflict_quote_b=str(obj.get("conflict_quote_b") or ""),
                authoritative_page=str(obj.get("authoritative_page") or ""),
                merge_instructions=str(obj.get("merge_instructions") or ""),
                raw=obj,
            ),
        )
    return plans


def pair_key(page_a: str, page_b: str) -> str:
    x, y = sorted([page_a.strip(), page_b.strip()])
    return f"{x}__{y}"
