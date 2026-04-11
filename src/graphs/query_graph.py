"""LangGraph: **Query** pipeline with **Gatekeeper** (Sprint 2)."""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Any, Optional, TypedDict

from git import Repo
from git.exc import GitCommandError
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from src.graphs.ingest_compile_graph import _default_tenant_id, resolve_wiki_root
from src.modules.compile.wiki_log import append_query_claude_cost_line
from src.modules.query.compounding import save_answer_to_wiki
from src.modules.query.hybrid_search import hybrid_search
from src.modules.query.models import ChunkResult, QueryResult, SynthesisResult
from src.lib.openai_client import create_embedding
from src.modules.query.gatekeeper import GATEKEEPER_MODEL, GatekeeperDecision, run_gatekeeper_evaluation
from src.modules.query.synthesizer import SYNTHESIS_MODEL, synthesize_answer


class QueryGraphState(TypedDict, total=False):
    question: str
    tenant_id: str
    query_embedding: list[float]
    chunks: list[dict[str, Any]]
    synthesis: dict[str, Any]
    gatekeeper_decision: dict[str, Any]
    gatekeeper_input_tokens: int
    gatekeeper_output_tokens: int
    gatekeeper_cost_usd: float
    saved_to_wiki: bool
    output_slug: str
    result: dict[str, Any]
    error: Optional[str]


def node_embed_question(state: QueryGraphState) -> dict[str, Any]:
    if state.get("error"):
        return {}
    try:
        emb = create_embedding(state["question"])
    except Exception as exc:
        return {"error": f"Query embedding failed: {exc}"}
    return {"query_embedding": emb}


def node_hybrid_search(state: QueryGraphState) -> dict[str, Any]:
    if state.get("error"):
        return {}
    try:
        found = hybrid_search(
            state["question"],
            state["tenant_id"],
            match_count=10,
            query_embedding=state.get("query_embedding"),
        )
    except Exception as exc:
        return {"error": f"Hybrid search failed: {exc}"}
    return {"chunks": [c.model_dump(mode="json") for c in found]}


def node_synthesize(state: QueryGraphState) -> dict[str, Any]:
    if state.get("error"):
        return {}
    try:
        chunks = [ChunkResult.model_validate(c) for c in state.get("chunks") or []]
        syn = synthesize_answer(state["question"], chunks, state["tenant_id"])
    except Exception as exc:
        return {"error": f"Synthesis failed: {exc}"}
    return {"synthesis": syn.model_dump(mode="json")}


def node_gatekeeper(state: QueryGraphState) -> dict[str, Any]:
    if state.get("error"):
        return {}
    try:
        syn = SynthesisResult.model_validate(state["synthesis"])
        chunks = [ChunkResult.model_validate(c) for c in state.get("chunks") or []]
        decision, in_tok, out_tok, cost = run_gatekeeper_evaluation(
            state["question"],
            syn,
            chunks,
        )
    except Exception as exc:
        return {"error": f"Gatekeeper failed: {exc}"}
    return {
        "gatekeeper_decision": decision.model_dump(mode="json"),
        "gatekeeper_input_tokens": in_tok,
        "gatekeeper_output_tokens": out_tok,
        "gatekeeper_cost_usd": cost,
    }


def node_save_if_approved(state: QueryGraphState) -> dict[str, Any]:
    if state.get("error"):
        return {}
    decision = GatekeeperDecision.model_validate(state["gatekeeper_decision"])
    if not decision.should_save:
        return {"saved_to_wiki": False}
    try:
        syn = SynthesisResult.model_validate(state["synthesis"])
        slug = save_answer_to_wiki(
            state["question"],
            syn,
            decision,
            state["tenant_id"],
        )
    except Exception as exc:
        return {"error": f"Save to wiki failed: {exc}", "saved_to_wiki": False}
    return {"saved_to_wiki": True, "output_slug": slug}


def node_log_query_claude(state: QueryGraphState) -> dict[str, Any]:
    """Best-effort: append ``wiki/log.md`` lines and commit; never fails the query."""
    if state.get("error"):
        return {}
    syn_raw = state.get("synthesis")
    if not syn_raw:
        return {}
    wiki_root = resolve_wiki_root()
    try:
        syn = SynthesisResult.model_validate(syn_raw)
        q_preview = state["question"][:80] + ("…" if len(state["question"]) > 80 else "")
        append_query_claude_cost_line(
            wiki_root,
            operation="query_synthesize",
            detail=q_preview,
            cost_usd=Decimal(str(syn.cost_usd)),
            input_tokens=syn.input_tokens,
            output_tokens=syn.output_tokens,
            model=SYNTHESIS_MODEL,
        )
        if "gatekeeper_input_tokens" in state:
            append_query_claude_cost_line(
                wiki_root,
                operation="query_gatekeeper",
                detail=q_preview,
                cost_usd=Decimal(str(state.get("gatekeeper_cost_usd", 0))),
                input_tokens=int(state.get("gatekeeper_input_tokens", 0)),
                output_tokens=int(state.get("gatekeeper_output_tokens", 0)),
                model=GATEKEEPER_MODEL,
            )
        repo = Repo(wiki_root)
        repo.index.add(["log.md"])
        try:
            repo.index.commit(f"log: query claude — {q_preview}")
        except GitCommandError as exc:
            err = str(exc).lower()
            if "nothing to commit" not in err and "no changes" not in err:
                pass
    except Exception:
        pass
    return {}


def node_return_answer(state: QueryGraphState) -> dict[str, Any]:
    if state.get("error"):
        return {}
    syn = SynthesisResult.model_validate(state["synthesis"])
    decision = GatekeeperDecision.model_validate(state["gatekeeper_decision"])
    total = float(syn.cost_usd) + float(state.get("gatekeeper_cost_usd", 0))
    qr = QueryResult(
        answer_markdown=syn.answer_markdown,
        citations=syn.citations,
        saved_to_wiki=bool(state.get("saved_to_wiki")),
        gatekeeper_reasoning=decision.reasoning,
        cost_usd=total,
    )
    return {"result": qr.model_dump(mode="json")}


def build_query_graph() -> Any:
    builder = StateGraph(QueryGraphState)
    builder.add_node("embed_question", node_embed_question)
    builder.add_node("hybrid_search", node_hybrid_search)
    builder.add_node("synthesize", node_synthesize)
    builder.add_node("gatekeeper", node_gatekeeper)
    builder.add_node("save_if_approved", node_save_if_approved)
    builder.add_node("log_query_claude", node_log_query_claude)
    builder.add_node("return_answer", node_return_answer)

    builder.add_edge(START, "embed_question")
    builder.add_edge("embed_question", "hybrid_search")
    builder.add_edge("hybrid_search", "synthesize")
    builder.add_edge("synthesize", "gatekeeper")
    builder.add_edge("gatekeeper", "save_if_approved")
    builder.add_edge("save_if_approved", "log_query_claude")
    builder.add_edge("log_query_claude", "return_answer")
    builder.add_edge("return_answer", END)

    return builder.compile(checkpointer=MemorySaver())


def run_query(question: str, tenant_id: str) -> tuple[Optional[QueryResult], Optional[str]]:
    """Run the query graph; return ``(result, error_message)``."""
    graph = build_query_graph()
    tid = (tenant_id or "").strip() or _default_tenant_id()
    thread_id = f"query-{uuid.uuid4()}"
    out: QueryGraphState = graph.invoke(
        {
            "question": question.strip(),
            "tenant_id": tid,
            "error": None,
        },
        config={"configurable": {"thread_id": thread_id}},
    )
    err = out.get("error")
    if err:
        return None, str(err)
    raw = out.get("result")
    if not raw:
        return None, "Query finished without a result payload"
    return QueryResult.model_validate(raw), None
