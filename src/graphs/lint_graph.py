"""
lint_graph.py — LangGraph graph for the on-demand Lint loop (Loop 4).

Orchestrates: orphan detection → stale detection → deduplication →
contradiction detection (with HITL interrupt) → confidence decay (separate trigger).

HITL: interrupt_before="resolve_contradiction" node.
Human receives structured report. Decides per-contradiction: approve/reject merge.
Graph resumes after human input via graph.update_state() then graph.invoke(None).

Never runs autonomously. Always triggered by explicit user action or
approved n8n schedule (decay only).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from src.graphs.ingest_compile_graph import _default_tenant_id
from src.lib.supabase import create_supabase_client, insert_wiki_log_row
from src.modules.lint.contradiction_checker import pair_key, run_contradiction_detect_pass1, run_contradiction_plan_pass2
from src.modules.lint.deduplication import find_duplicate_candidates
from src.modules.lint.models import ContradictionCandidate, ContradictionPlan, DecayReport, LintReport
from src.modules.lint.orphan_detector import detect_orphans
from src.modules.lint.stale_detector import detect_stale_pages
from src.modules.query.compounding import apply_lint_contradiction_merge


class LintState(TypedDict, total=False):
    tenant_id: str
    orphans: list[dict[str, Any]]
    stale_pages: list[dict[str, Any]]
    duplicate_candidates: list[dict[str, Any]]
    contradiction_candidates: list[dict[str, Any]]
    contradiction_plans: list[dict[str, Any]]
    human_decisions: dict[str, str]
    merge_results: list[dict[str, Any]]
    report: dict[str, Any]
    errors: list[str]


_LINT_CHECKPOINTER = MemorySaver()


def _err(state: LintState, msg: str) -> list[str]:
    return [*state.get("errors", []), msg]


def _orphan_rows(tenant_id: str) -> list[dict[str, Any]]:
    found = detect_orphans(tenant_id)
    return [
        {
            "page_slug": o.page_slug,
            "page_title": o.page_title,
            "broken_links": o.broken_links,
            "checked_at": o.checked_at.isoformat(),
        }
        for o in found
    ]


def _stale_rows(tenant_id: str) -> list[dict[str, Any]]:
    found = detect_stale_pages(tenant_id)
    return [
        {
            "slug": s.slug,
            "title": s.title,
            "days_since_update": s.days_since_update,
            "confidence": s.confidence,
            "page_type": s.page_type,
        }
        for s in found
    ]


def _dup_rows(tenant_id: str) -> list[dict[str, Any]]:
    found = find_duplicate_candidates(tenant_id)
    return [
        {
            "page_a_slug": d.page_a_slug,
            "page_a_title": d.page_a_title,
            "page_b_slug": d.page_b_slug,
            "page_b_title": d.page_b_title,
            "similarity_score": d.similarity_score,
            "suggested_action": d.suggested_action,
        }
        for d in found
    ]


def node_detect_orphans(state: LintState) -> dict[str, Any]:
    try:
        rows = _orphan_rows(state["tenant_id"])
        return {"orphans": rows}
    except Exception as exc:
        return {"orphans": [], "errors": _err(state, f"orphan detection: {exc}")}


def node_detect_stale(state: LintState) -> dict[str, Any]:
    try:
        rows = _stale_rows(state["tenant_id"])
        return {"stale_pages": rows}
    except Exception as exc:
        return {"stale_pages": [], "errors": _err(state, f"stale detection: {exc}")}


def node_detect_duplicates(state: LintState) -> dict[str, Any]:
    try:
        rows = _dup_rows(state["tenant_id"])
        return {"duplicate_candidates": rows}
    except Exception as exc:
        return {
            "duplicate_candidates": [],
            "errors": _err(state, f"deduplication: {exc}"),
        }


def node_detect_contradictions_pass1(state: LintState) -> dict[str, Any]:
    try:
        cands = run_contradiction_detect_pass1(state["tenant_id"])
        return {
            "contradiction_candidates": [
                {"page_a": c.page_a, "page_b": c.page_b, "suspected_conflict": c.suspected_conflict}
                for c in cands
            ],
        }
    except Exception as exc:
        return {
            "contradiction_candidates": [],
            "errors": _err(state, f"contradiction pass 1: {exc}"),
        }


def node_plan_contradictions_pass2(state: LintState) -> dict[str, Any]:
    try:
        raw_c = state.get("contradiction_candidates") or []

        cands = [
            ContradictionCandidate(
                page_a=str(x.get("page_a") or ""),
                page_b=str(x.get("page_b") or ""),
                suspected_conflict=str(x.get("suspected_conflict") or ""),
            )
            for x in raw_c
            if x.get("page_a") and x.get("page_b")
        ]
        plans = run_contradiction_plan_pass2(state["tenant_id"], cands)
        return {
            "contradiction_plans": [
                {
                    "page_a": p.page_a,
                    "page_b": p.page_b,
                    "is_contradiction": p.is_contradiction,
                    "conflict_quote_a": p.conflict_quote_a,
                    "conflict_quote_b": p.conflict_quote_b,
                    "authoritative_page": p.authoritative_page,
                    "merge_instructions": p.merge_instructions,
                }
                for p in plans
            ],
        }
    except Exception as exc:
        return {
            "contradiction_plans": [],
            "errors": _err(state, f"contradiction pass 2: {exc}"),
        }


def node_resolve_contradiction(state: LintState) -> dict[str, Any]:
    """HITL gate: runs only after interrupt is cleared and human_decisions are merged into state."""
    return {}


def node_apply_resolution(state: LintState) -> dict[str, Any]:
    decisions = state.get("human_decisions") or {}
    raw_plans = state.get("contradiction_plans") or []
    results: list[dict[str, Any]] = []
    errs = list(state.get("errors") or [])
    tid = state["tenant_id"]
    for raw in raw_plans:
        if not raw.get("is_contradiction"):
            continue
        pa = str(raw.get("page_a") or "")
        pb = str(raw.get("page_b") or "")
        key = pair_key(pa, pb)
        if decisions.get(key) != "approve":
            results.append({"pair": key, "status": "skipped", "reason": decisions.get(key, "no_decision")})
            continue
        plan = ContradictionPlan(
            page_a=pa,
            page_b=pb,
            is_contradiction=True,
            conflict_quote_a=str(raw.get("conflict_quote_a") or ""),
            conflict_quote_b=str(raw.get("conflict_quote_b") or ""),
            authoritative_page=str(raw.get("authoritative_page") or ""),
            merge_instructions=str(raw.get("merge_instructions") or ""),
            raw=raw,
        )
        try:
            apply_lint_contradiction_merge(tid, plan)
            results.append({"pair": key, "status": "merged"})
        except Exception as exc:
            results.append({"pair": key, "status": "error", "error": str(exc)})
            errs.append(f"merge {key}: {exc}")
    return {"merge_results": results, "errors": errs}


def node_compile_report(state: LintState) -> dict[str, Any]:
    checked_at = datetime.now(timezone.utc).isoformat()
    report = LintReport(
        tenant_id=state["tenant_id"],
        checked_at=checked_at,
        orphans=state.get("orphans") or [],
        stale_pages=state.get("stale_pages") or [],
        duplicate_candidates=state.get("duplicate_candidates") or [],
        contradiction_candidates=state.get("contradiction_candidates") or [],
        contradiction_plans=state.get("contradiction_plans") or [],
        merge_results=state.get("merge_results") or [],
        errors=state.get("errors") or [],
        thread_id=None,
        pending_resolution=False,
    )
    payload = report.to_dict()
    try:
        client = create_supabase_client()
        insert_wiki_log_row(
            client,
            tenant_id=state["tenant_id"],
            operation="lint_run",
            details=payload,
            module="lint_graph",
        )
    except Exception:
        pass
    return {"report": payload}


def _after_pass2(state: LintState) -> str:
    plans = state.get("contradiction_plans") or []
    for p in plans:
        if p.get("is_contradiction"):
            return "hitl"
    return "report"


def build_lint_graph() -> Any:
    builder = StateGraph(LintState)
    builder.add_node("detect_orphans", node_detect_orphans)
    builder.add_node("detect_stale", node_detect_stale)
    builder.add_node("detect_duplicates", node_detect_duplicates)
    builder.add_node("contradictions_pass1", node_detect_contradictions_pass1)
    builder.add_node("contradictions_pass2", node_plan_contradictions_pass2)
    builder.add_node("resolve_contradiction", node_resolve_contradiction)
    builder.add_node("apply_resolution", node_apply_resolution)
    builder.add_node("compile_report", node_compile_report)

    builder.add_edge(START, "detect_orphans")
    builder.add_edge("detect_orphans", "detect_stale")
    builder.add_edge("detect_stale", "detect_duplicates")
    builder.add_edge("detect_duplicates", "contradictions_pass1")
    builder.add_edge("contradictions_pass1", "contradictions_pass2")
    builder.add_conditional_edges(
        "contradictions_pass2",
        _after_pass2,
        {"hitl": "resolve_contradiction", "report": "compile_report"},
    )
    builder.add_edge("resolve_contradiction", "apply_resolution")
    builder.add_edge("apply_resolution", "compile_report")
    builder.add_edge("compile_report", END)

    return builder.compile(
        checkpointer=_LINT_CHECKPOINTER,
        interrupt_before=["resolve_contradiction"],
    )


def _lint_report_from_state(state: LintState, *, thread_id: str | None, pending: bool) -> LintReport:
    checked_at = datetime.now(timezone.utc).isoformat()
    return LintReport(
        tenant_id=state.get("tenant_id") or "",
        checked_at=checked_at,
        orphans=state.get("orphans") or [],
        stale_pages=state.get("stale_pages") or [],
        duplicate_candidates=state.get("duplicate_candidates") or [],
        contradiction_candidates=state.get("contradiction_candidates") or [],
        contradiction_plans=state.get("contradiction_plans") or [],
        merge_results=state.get("merge_results") or [],
        errors=state.get("errors") or [],
        thread_id=thread_id,
        pending_resolution=pending,
    )


def _persist_pending_report(tenant_id: str, report: LintReport) -> None:
    try:
        client = create_supabase_client()
        insert_wiki_log_row(
            client,
            tenant_id=tenant_id,
            operation="lint_run",
            details=report.to_dict(),
            module="lint_graph",
        )
    except Exception:
        pass


def run_lint(tenant_id: str) -> LintReport:
    """Run lint through contradiction planning; may pause before HITL merge node."""
    graph = build_lint_graph()
    tid = (tenant_id or "").strip() or _default_tenant_id()
    thread_id = f"lint-{uuid.uuid4()}"
    config: dict[str, Any] = {"configurable": {"thread_id": thread_id}}
    init: LintState = {
        "tenant_id": tid,
        "orphans": [],
        "stale_pages": [],
        "duplicate_candidates": [],
        "contradiction_candidates": [],
        "contradiction_plans": [],
        "human_decisions": {},
        "merge_results": [],
        "errors": [],
    }
    out = graph.invoke(init, config)
    snap = graph.get_state(config)
    nxt = snap.next or ()
    pending = "resolve_contradiction" in nxt
    merged = {**init, **out}
    report = _lint_report_from_state(merged, thread_id=thread_id, pending=pending)
    if pending:
        _persist_pending_report(tid, report)
    if not pending and isinstance(out.get("report"), dict):
        return LintReport(
            tenant_id=str(out["report"].get("tenant_id") or tid),
            checked_at=str(out["report"].get("checked_at") or report.checked_at),
            orphans=list(out["report"].get("orphans") or []),
            stale_pages=list(out["report"].get("stale_pages") or []),
            duplicate_candidates=list(out["report"].get("duplicate_candidates") or []),
            contradiction_candidates=list(out["report"].get("contradiction_candidates") or []),
            contradiction_plans=list(out["report"].get("contradiction_plans") or []),
            merge_results=list(out["report"].get("merge_results") or []),
            errors=list(out["report"].get("errors") or []),
            thread_id=None,
            pending_resolution=False,
        )
    return report


def resume_lint(thread_id: str, decisions: dict[str, str]) -> LintReport:
    """Resume after HITL: supply slug_a__slug_b → approve|reject."""
    graph = build_lint_graph()
    config: dict[str, Any] = {"configurable": {"thread_id": thread_id}}
    st = graph.get_state(config)
    if not st.next or "resolve_contradiction" not in st.next:
        msg = "No paused lint run for this thread_id"
        raise RuntimeError(msg)
    graph.update_state(config, {"human_decisions": decisions})
    out = graph.invoke(None, config)
    raw = out.get("report")
    if isinstance(raw, dict):
        return LintReport(
            tenant_id=str(raw.get("tenant_id") or ""),
            checked_at=str(raw.get("checked_at") or ""),
            orphans=list(raw.get("orphans") or []),
            stale_pages=list(raw.get("stale_pages") or []),
            duplicate_candidates=list(raw.get("duplicate_candidates") or []),
            contradiction_candidates=list(raw.get("contradiction_candidates") or []),
            contradiction_plans=list(raw.get("contradiction_plans") or []),
            merge_results=list(raw.get("merge_results") or []),
            errors=list(raw.get("errors") or []),
            thread_id=None,
            pending_resolution=False,
        )
    merged: dict[str, Any] = {**dict(st.values), **out}
    return _lint_report_from_state(merged, thread_id=None, pending=False)


def run_decay(tenant_id: str) -> DecayReport:
    """Monthly confidence decay + archival (invoked via API / cron, not from this graph)."""
    from src.modules.lint.confidence_decay import run_confidence_decay

    return run_confidence_decay(tenant_id)
