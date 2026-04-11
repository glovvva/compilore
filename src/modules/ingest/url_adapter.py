"""URL ingest adapter for the **Ingest** loop.

Fetches HTML and extracts main article text with **trafilatura** (noise removal,
optional tables). Produces the same ``IngestResult`` shape as file adapters so
**Compile** stays format-agnostic.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import trafilatura
from trafilatura.metadata import extract_metadata

from .models import IngestResult


def extract_url(url: str) -> IngestResult:
    """Fetch ``url`` and return cleaned text plus metadata in ``frontmatter``."""
    raw = url.strip()
    if not raw:
        msg = "URL is empty"
        raise ValueError(msg)

    downloaded = trafilatura.fetch_url(raw)
    if not downloaded:
        msg = f"Failed to download URL: {raw}"
        raise RuntimeError(msg)

    body = trafilatura.extract(
        downloaded,
        url=raw,
        include_comments=False,
        include_tables=True,
    )
    if body is None:
        body = ""

    meta = extract_metadata(filecontent=downloaded, default_url=raw)
    extracted_title: str | None = None
    if meta is not None and meta.title:
        extracted_title = str(meta.title).strip() or None

    if not extracted_title:
        host = urlparse(raw).netloc or "url"
        extracted_title = host

    frontmatter: dict[str, Any] = {
        "source_url": raw,
        "title": extracted_title,
    }

    label = urlparse(raw).path.rstrip("/").split("/")[-1] or urlparse(raw).netloc
    safe_stem = "".join(c if c.isalnum() or c in "-._" else "-" for c in label)[:120]
    source_path = Path(safe_stem or "url-source")

    return IngestResult(
        body=body.strip(),
        frontmatter=frontmatter,
        source_path=source_path,
        doc_type="url",
    )
