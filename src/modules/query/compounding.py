"""Compounding writes for the **Query** loop (gatekeeper-approved outputs)."""

from __future__ import annotations

import hashlib
import re
from datetime import date, datetime, timezone
from typing import Any

from git import Repo
from git.exc import GitCommandError

from src.graphs.ingest_compile_graph import resolve_wiki_root
from src.lib.supabase import create_supabase_client, insert_wiki_page_row
from src.modules.compile.models import WikiPage
from src.modules.compile.wiki_storage import render_page_markdown, wiki_page_relative_path
from src.modules.lint.models import ContradictionPlan
from src.modules.query.gatekeeper import GatekeeperDecision
from src.modules.query.models import SynthesisResult


def _strip_slug_from_index(index_text: str, slug: str) -> str:
    lines = index_text.splitlines()
    kept: list[str] = []
    needle = f"`{slug}`"
    for line in lines:
        if needle in line and "/" in line:
            continue
        kept.append(line)
    return "\n".join(kept) + ("\n" if kept else "")


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


def apply_lint_contradiction_merge(tenant_id: str, plan: ContradictionPlan) -> None:
    """Apply an HITL-approved contradiction merge: extend authoritative page, deprecate the other.

    One Git commit for both wiki files + index line removal. Updates ``wiki_pages`` rows only
    (chunk re-embedding is a separate ingest concern).
    """
    if not plan.is_contradiction:
        msg = "apply_lint_contradiction_merge requires is_contradiction=True"
        raise ValueError(msg)
    auth_slug = (plan.authoritative_page or "").strip()
    pa, pb = plan.page_a.strip(), plan.page_b.strip()
    if auth_slug not in {pa, pb}:
        msg = f"authoritative_page {auth_slug!r} must be one of {pa!r}, {pb!r}"
        raise ValueError(msg)
    other_slug = pb if auth_slug == pa else pa

    client = create_supabase_client()
    res_a = (
        client.table("wiki_pages")
        .select("*")
        .eq("tenant_id", tenant_id)
        .eq("slug", auth_slug)
        .limit(1)
        .execute()
    )
    res_b = (
        client.table("wiki_pages")
        .select("*")
        .eq("tenant_id", tenant_id)
        .eq("slug", other_slug)
        .limit(1)
        .execute()
    )
    row_auth = (getattr(res_a, "data", None) or [None])[0]
    row_other = (getattr(res_b, "data", None) or [None])[0]
    if not row_auth or not row_other:
        msg = "Could not load both wiki pages for merge"
        raise RuntimeError(msg)

    wiki_root = resolve_wiki_root()
    today = date.today().isoformat()
    now_iso = datetime.now(timezone.utc).isoformat()

    fm_auth: dict[str, Any] = dict(row_auth.get("frontmatter") or {})
    body_auth = str(row_auth.get("content_markdown") or "")
    merge_section = (
        f"\n\n## Merged resolution ({today})\n\n"
        f"_Lint merge: deprecated [[{other_slug}]]; authoritative page is [[{auth_slug}]]._\n\n"
        f"**Quote from [[{plan.page_a}]]:** {plan.conflict_quote_a}\n\n"
        f"**Quote from [[{plan.page_b}]]:** {plan.conflict_quote_b}\n\n"
        f"**Instructions applied:** {plan.merge_instructions}\n"
    )
    new_body_auth = body_auth.rstrip() + merge_section
    fm_auth["date_modified"] = today
    page_auth = WikiPage(
        slug=auth_slug,
        title=str(row_auth.get("title") or auth_slug),
        page_type=str(row_auth.get("page_type") or "concept"),
        content_markdown=new_body_auth,
        frontmatter=fm_auth,
    )

    fm_other: dict[str, Any] = dict(row_other.get("frontmatter") or {})
    fm_other["status"] = "deprecated"
    fm_other["date_modified"] = today
    stub = (
        f"_This page was merged into [[{auth_slug}]] after lint contradiction resolution "
        f"({today}). See the authoritative page for the merged content._\n"
    )
    page_other = WikiPage(
        slug=other_slug,
        title=str(row_other.get("title") or other_slug),
        page_type=str(row_other.get("page_type") or "concept"),
        content_markdown=stub,
        frontmatter=fm_other,
    )

    path_auth = wiki_root / wiki_page_relative_path(page_auth)
    path_other = wiki_root / wiki_page_relative_path(page_other)
    path_auth.parent.mkdir(parents=True, exist_ok=True)
    path_other.parent.mkdir(parents=True, exist_ok=True)
    path_auth.write_text(render_page_markdown(page_auth), encoding="utf-8")
    path_other.write_text(render_page_markdown(page_other), encoding="utf-8")

    index_path = wiki_root / "index.md"
    index_text = index_path.read_text(encoding="utf-8") if index_path.is_file() else ""
    index_text = _strip_slug_from_index(index_text, other_slug)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(index_text, encoding="utf-8")

    client.table("wiki_pages").update(
        {
            "content_markdown": new_body_auth,
            "frontmatter": fm_auth,
            "updated_at": now_iso,
        },
    ).eq("id", str(row_auth["id"])).execute()

    client.table("wiki_pages").update(
        {
            "content_markdown": stub,
            "frontmatter": fm_other,
            "status": "deprecated",
            "updated_at": now_iso,
        },
    ).eq("id", str(row_other["id"])).execute()

    repo = Repo(wiki_root)
    rel_auth = wiki_page_relative_path(page_auth)
    rel_other = wiki_page_relative_path(page_other)
    repo.index.add([rel_auth, rel_other, "index.md"])
    msg = f"lint: merge contradiction {other_slug} → {auth_slug}"
    try:
        repo.index.commit(msg)
    except GitCommandError as exc:
        err = str(exc).lower()
        if "nothing to commit" in err or "no changes" in err:
            return
        raise
