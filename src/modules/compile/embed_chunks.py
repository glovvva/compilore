"""Embed wiki page bodies and persist ``document_chunks`` rows."""

from __future__ import annotations

from supabase import Client

from src.lib.chunking import chunk_text_by_tokens
from src.lib.openai_client import create_embedding
from src.lib.supabase import insert_document_chunk
from src.modules.compile.models import WikiPage


def embed_and_store_wiki_pages_chunks(
    client: Client,
    *,
    tenant_id: str,
    document_id: str,
    pages: list[WikiPage],
    slug_to_wiki_page_id: dict[str, str],
    max_tokens: int = 500,
    overlap_tokens: int = 50,
) -> int:
    """Chunk each page body, embed, insert chunks. Returns number of chunks written."""
    total = 0
    for page in pages:
        wiki_page_id = slug_to_wiki_page_id.get(page.slug)
        if not wiki_page_id:
            msg = f"No wiki_page id for slug {page.slug!r}"
            raise KeyError(msg)
        full_text = f"# {page.title}\n\n{page.content_markdown}"
        chunks = chunk_text_by_tokens(
            full_text,
            max_tokens=max_tokens,
            overlap_tokens=overlap_tokens,
        )
        if not chunks:
            continue
        for idx, chunk_text in enumerate(chunks):
            embedding = create_embedding(chunk_text)
            insert_document_chunk(
                client,
                tenant_id=tenant_id,
                wiki_page_id=wiki_page_id,
                document_id=document_id,
                chunk_text=chunk_text,
                chunk_index=idx,
                embedding=embedding,
                metadata={"slug": page.slug, "page_type": page.page_type},
            )
            total += 1
    return total
