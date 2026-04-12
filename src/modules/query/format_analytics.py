"""Analytics helpers for output-format UX (wiki_log)."""

from __future__ import annotations

from typing import Any, Optional

from src.lib.supabase import create_supabase_client, ensure_tenant_exists, insert_wiki_log_row


def log_format_chip_click(
    tenant_id: str,
    *,
    format_id: str,
    was_useful: Optional[bool] = None,
    answer_id: Optional[str] = None,
) -> None:
    client = create_supabase_client()
    ensure_tenant_exists(client, tenant_id)
    details: dict[str, Any] = {"format": format_id}
    if was_useful is not None:
        details["was_useful"] = was_useful
    if answer_id:
        details["answer_id"] = answer_id
    insert_wiki_log_row(
        client,
        tenant_id=tenant_id,
        operation="format_chip_click",
        details=details,
        module="format_analytics",
    )
