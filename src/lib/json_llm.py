"""Parse JSON from LLM text (strip optional markdown fences)."""

from __future__ import annotations

import json
import re


def strip_json_fence(text: str) -> str:
    text = text.strip()
    m = re.match(r"^```(?:json)?\s*\n?(.*?)\n?```\s*$", text, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return text


def parse_json_object(text: str) -> dict[str, object]:
    raw = strip_json_fence(text)
    data = json.loads(raw)
    if not isinstance(data, dict):
        msg = "Expected JSON object at root"
        raise ValueError(msg)
    return data
