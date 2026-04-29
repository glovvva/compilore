"""
Proposal generator — Output module for Compilore.
Uses Wiki context to generate structured client proposals.
Part of the Query loop output formats (Phase 2 priority for sales segment).
"""

from __future__ import annotations

import hashlib
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import anthropic
from git import Repo
from git.exc import GitCommandError
from pydantic import BaseModel, Field

from src.graphs.ingest_compile_graph import resolve_wiki_root
from src.lib.anthropic_cost import anthropic_usd_from_usage
from src.lib.supabase import schedule_insert_wiki_log_row
from src.modules.query.hybrid_search import hybrid_search
from src.modules.query.page_metadata import fetch_wiki_pages_by_ids

PROPOSAL_MODEL = "claude-sonnet-4-20250514"
_WIKILINK_RE = re.compile(r"\[\[([^[\]]+)\]\]")


class ProposalRequest(BaseModel):
    client_name: str = Field(min_length=1)
    client_company: str = Field(min_length=1)
    client_needs: str = Field(min_length=1)
    department_id: Optional[str] = None
    language: str = "pl"


class ProposalResponse(BaseModel):
    content: str
    wiki_pages_used: list[str] = Field(default_factory=list)
    previous_proposals_found: int = 0
    git_commit_hash: Optional[str] = None


def _load_generate_proposal_prompt() -> str:
    path = Path(__file__).resolve().parents[2] / "config" / "prompts" / "generate_proposal.md"
    return path.read_text(encoding="utf-8")


def _proposal_filename(request: ProposalRequest) -> str:
    seed = f"{request.client_company.strip()}::{request.client_name.strip()}::{request.client_needs.strip()}"
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12]
    stem = re.sub(r"[^a-z0-9]+", "-", request.client_company.lower()).strip("-") or "client"
    return f"proposal-{stem}-{digest}.md"


def _extract_wiki_links(markdown: str) -> list[str]:
    out: list[str] = []
    for match in _WIKILINK_RE.findall(markdown):
        title = match.strip()
        if title and title not in out:
            out.append(title)
    return out


def _build_wiki_context(tenant_id: str, chunks_text: list[str], wiki_page_ids: list[str]) -> str:
    rows = fetch_wiki_pages_by_ids(tenant_id, wiki_page_ids)
    by_id = {str(row.get("id") or ""): row for row in rows}
    blocks: list[str] = []
    for idx, chunk in enumerate(chunks_text):
        row = by_id.get(wiki_page_ids[idx]) if idx < len(wiki_page_ids) else None
        title = str((row or {}).get("title") or (row or {}).get("slug") or "unknown")
        excerpt = chunk.strip()
        blocks.append(f"### Source {idx + 1} [[{title}]]\n{excerpt}")
    return "\n\n".join(blocks) if blocks else "(no wiki context found)"


async def generate_proposal(
    request: ProposalRequest,
    tenant_id: str,
) -> ProposalResponse:
    """Generate a proposal from Wiki context and persist it under ``wiki/outputs/proposals/``."""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        msg = "ANTHROPIC_API_KEY is not set"
        raise RuntimeError(msg)

    wiki_results = await hybrid_search(
        query=f"{request.client_needs} {request.client_company}",
        tenant_id=tenant_id,
        match_count=15,
        scope="tenant",
        department_id=request.department_id,
    )

    previous = await hybrid_search(
        query="proposal client offer",
        tenant_id=tenant_id,
        match_count=3,
        scope="tenant",
        department_id=request.department_id,
    )

    wiki_page_ids = [c.wiki_page_id for c in wiki_results]
    chunk_texts = [c.chunk_text for c in wiki_results]
    wiki_context = _build_wiki_context(tenant_id, chunk_texts, wiki_page_ids)
    previous_proposals = "\n\n".join(c.chunk_text.strip() for c in previous) if previous else "(none)"

    client_info = (
        f"Client name: {request.client_name.strip()}\n"
        f"Company: {request.client_company.strip()}\n"
        f"Needs: {request.client_needs.strip()}\n"
        f"Language: {request.language.strip() or 'pl'}"
    )

    system_template = _load_generate_proposal_prompt()
    system = (
        system_template.replace("{wiki_context}", wiki_context)
        .replace("{previous_proposals}", previous_proposals)
        .replace("{client_info}", client_info)
    )

    ac = anthropic.Anthropic(api_key=key)
    message = ac.messages.create(
        model=PROPOSAL_MODEL,
        max_tokens=4096,
        system=system,
        messages=[{"role": "user", "content": "Proszę przygotować propozycję dla klienta."}],
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
    proposal_markdown = "".join(text_parts).strip()
    if not proposal_markdown:
        msg = "Claude returned no proposal text"
        raise RuntimeError(msg)

    wiki_pages_used = _extract_wiki_links(proposal_markdown)

    wiki_root = resolve_wiki_root()
    rel_path = Path("outputs") / "proposals" / _proposal_filename(request)
    out_path = wiki_root / rel_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(proposal_markdown + "\n", encoding="utf-8")

    commit_hash: Optional[str] = None
    try:
        repo = Repo(wiki_root)
        repo.index.add([str(rel_path)])
        msg = f"output: proposal — {request.client_company.strip()}"
        try:
            repo.index.commit(msg)
            commit_hash = repo.head.commit.hexsha
        except GitCommandError as exc:
            err = str(exc).lower()
            if "nothing to commit" in err or "no changes" in err:
                commit_hash = None
            else:
                raise
    except Exception as exc:
        raise RuntimeError(f"Git commit failed: {exc}") from exc

    schedule_insert_wiki_log_row(
        tenant_id=tenant_id,
        operation="generate_proposal",
        module="proposal_generator",
        details={
            "client_company": request.client_company[:100],
            "client_name": request.client_name[:100],
            "wiki_results": len(wiki_results),
            "previous_proposals_found": len(previous),
            "proposal_path": str(rel_path),
        },
        tokens_used=in_tok + out_tok,
        cost_usd=cost,
    )

    return ProposalResponse(
        content=proposal_markdown,
        wiki_pages_used=wiki_pages_used,
        previous_proposals_found=len(previous),
        git_commit_hash=commit_hash,
    )

