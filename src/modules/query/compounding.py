"""Compounding writes for the **Query** loop (gatekeeper-approved outputs)."""

from __future__ import annotations

import hashlib
import re
from datetime import date
from typing import Any

from git import Repo
from git.exc import GitCommandError

from src.graphs.ingest_compile_graph import resolve_wiki_root
from src.lib.supabase import create_supabase_client, insert_wiki_page_row
from src.modules.compile.models import WikiPage
from src.modules.compile.wiki_storage import render_page_markdown, wiki_page_relative_path
from src.modules.query.gatekeeper import GatekeeperDecision
from src.modules.query.models import SynthesisResult


def _output_slug(question: str) -> str:
    digest = hashlib.sha256(question.strip().encode("utf-8")).hexdigest()[:16]
    return f"output-{digest}"


def _commit_message_fragment(question: str) -> str:
    one_line = re.sub(r"\s+", " ", question.strip())[:60]
    return one_line or "query"


def save_answer_to_wiki(
    question: str,
    answer: SynthesisResult,
    decision: GatekeeperDecision,
    tenant_id: str,
) -> str:
    """Persist approved answer under ``wiki/outputs/``, insert ``wiki_pages``, Git commit.

    Preconditions: ``decision.should_save`` is True (caller enforced).
    Returns the output slug.
    """
    if not decision.should_save:
        msg = "save_answer_to_wiki requires should_save=True"
        raise ValueError(msg)

    slug = _output_slug(question)
    title = _commit_message_fragment(question)
    today = date.today().isoformat()
    frontmatter: dict[str, Any] = {
        "title": title,
        "type": "output",
        "status": "draft",
        "confidence": float(decision.confidence),
        "date_created": today,
        "date_modified": today,
        "summary": f"Saved answer for question: {title}",
        "source_question": question,
        "citations": answer.citations,
        "gatekeeper_reasoning": decision.reasoning,
    }

    page = WikiPage(
        slug=slug,
        title=title,
        page_type="output",
        content_markdown=answer.answer_markdown,
        frontmatter=frontmatter,
    )

    wiki_root = resolve_wiki_root()
    rel = wiki_page_relative_path(page)
    out_path = wiki_root / rel
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(render_page_markdown(page), encoding="utf-8")

    client = create_supabase_client()
    insert_wiki_page_row(
        client,
        tenant_id=tenant_id,
        slug=slug,
        title=title,
        page_type="output",
        content_markdown=answer.answer_markdown,
        frontmatter=frontmatter,
        source_documents=[],
    )

    repo = Repo(wiki_root)
    repo.index.add([rel])
    msg = f"output: {_commit_message_fragment(question)}"
    try:
        repo.index.commit(msg)
    except GitCommandError as exc:
        err = str(exc).lower()
        if "nothing to commit" in err or "no changes" in err:
            return slug
        raise

    return slug
