"""Locale JSON catalogs for API/UI strings (infrastructure only; Polish catalog shipped)."""

from __future__ import annotations

import json
from pathlib import Path

_cache: dict[str, dict[str, object]] = {}


def t(key: str, locale: str = "pl") -> str:
    """Translate key for given locale. Falls back to key if not found."""
    if locale not in _cache:
        path = Path(__file__).parent / f"{locale}.json"
        if path.exists():
            _cache[locale] = json.loads(path.read_text(encoding="utf-8"))
        else:
            _cache[locale] = {}

    parts = key.split(".")
    val: object = _cache[locale]
    for part in parts:
        if isinstance(val, dict):
            val = val.get(part, {})
        else:
            return key
    return val if isinstance(val, str) else key
