"""Gatekeeper for the **Query** loop (critical safeguard — brief §5.1).

TODO (PreResponseChecklist pattern, GapRoll-style): after the model returns an evaluation,
add a self-check step that verifies the written reasoning is internally consistent with
the three criteria **Novelty × Necessity × Grounding** before persisting or returning the
decision (e.g. short second pass or structured checklist). Not implemented yet — current
flow returns the first structured JSON decision only.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import anthropic
from pydantic import BaseModel, ConfigDict, Field

from src.lib.anthropic_cost import anthropic_usd_from_usage
from src.lib.json_llm import parse_json_object
from src.lib.supabase import create_supabase_client, insert_wiki_log_row
from src.modules.query.hybrid_search import gatekeeper_answer_precheck
from src.modules.query.models import ChunkResult, SynthesisResult

GATEKEEPER_MODEL = "claude-haiku-4-5-20251001"


class GatekeeperDecision(BaseModel):
    """Structured gate outcome before persisting to ``wiki/outputs/``."""

    model_config = ConfigDict(extra="forbid")

    should_save: bool
    reasoning: str = ""
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)


def _load_gatekeeper_prompt() -> str:
    path = Path(__file__).resolve().parents[2] / "config" / "prompts" / "gatekeeper_evaluate.md"
    return path.read_text(encoding="utf-8")


def run_gatekeeper_evaluation(
    question: str,
    answer: SynthesisResult,
    chunks: list[ChunkResult],
    *,
    tenant_id: str | None = None,
    api_key: str | None = None,
) -> tuple[GatekeeperDecision, int, int, float]:
    """Call Haiku; return decision and (input_tokens, output_tokens, cost_usd)."""
    key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        msg = "ANTHROPIC_API_KEY is not set"
        raise RuntimeError(msg)

    chunk_summary = [
        {"wiki_page_id": c.wiki_page_id, "snippet": c.chunk_text[:400]}
        for c in chunks[:20]
    ]
    payload = {
        "question": question,
        "answer_markdown": answer.answer_markdown,
        "citations": answer.citations,
        "retrieved_chunks": chunk_summary,
    }

    precheck_note = ""
    tid = (tenant_id or "").strip()
    if tid:
        try:
            hit = gatekeeper_answer_precheck(tid, answer.answer_markdown)
            if hit:
                slug, ptype, sim = hit
                precheck_note = (
                    f"\n\nNOTE: This knowledge already exists at [[{slug}]] (similarity: {sim:.2f}). "
                    "Evaluate whether saving this adds genuine value beyond the existing page.\n"
                )
                try:
                    client = create_supabase_client()
                    insert_wiki_log_row(
                        client,
                        tenant_id=tid,
                        operation="gatekeeper_precheck",
                        details={
                            "existing_page": slug,
                            "similarity": sim,
                            "page_type": ptype,
                            "decision": "injected_context",
                        },
                        module="gatekeeper",
                    )
                except Exception:
                    pass
        except Exception:
            pass

    system = _load_gatekeeper_prompt()
    user = (
        "Evaluate whether to save this answer to the Wiki as an output page.\n\n"
        + json.dumps({"evaluation_payload": payload}, ensure_ascii=False)
        + precheck_note
    )

    ac = anthropic.Anthropic(api_key=key)
    message = ac.messages.create(
        model=GATEKEEPER_MODEL,
        max_tokens=1024,
        system=system,
        messages=[{"role": "user", "content": user}],
    )

    in_tok = int(message.usage.input_tokens)
    out_tok = int(message.usage.output_tokens)
    cost = float(
        anthropic_usd_from_usage(
            in_tok,
            out_tok,
            env_input_key="GATE_HAIKU_INPUT_PER_MTOK",
            env_output_key="GATE_HAIKU_OUTPUT_PER_MTOK",
            default_input_per_mtok="1",
            default_output_per_mtok="5",
        ),
    )

    text_parts: list[str] = []
    for block in message.content:
        if getattr(block, "type", None) == "text":
            text_parts.append(block.text)
    raw_text = "".join(text_parts).strip()
    parsed = parse_json_object(raw_text)
    if "confidence" in parsed and isinstance(parsed["confidence"], (int, float, str)):
        try:
            parsed["confidence"] = float(parsed["confidence"])
        except (TypeError, ValueError):
            parsed["confidence"] = 0.0
    decision = GatekeeperDecision.model_validate(parsed)
    return decision, in_tok, out_tok, cost


def evaluate_answer(
    question: str,
    answer: SynthesisResult,
    chunks: list[ChunkResult],
    *,
    tenant_id: str | None = None,
    api_key: str | None = None,
) -> GatekeeperDecision:
    """Public API: gate decision only (see :func:`run_gatekeeper_evaluation` for usage)."""
    decision, _, _, _ = run_gatekeeper_evaluation(
        question,
        answer,
        chunks,
        tenant_id=tenant_id,
        api_key=api_key,
    )
    return decision
