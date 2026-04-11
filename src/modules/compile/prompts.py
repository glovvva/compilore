"""Compile-time prompt loading helpers for the **Compile** loop.

Loads system instructions from ``src/config/prompts/*.md`` so compilation behavior
is version-controlled separately from Python code. Aligns with project rules:
no large inline prompts in modules.
"""

from __future__ import annotations

from pathlib import Path


def load_compile_prompt(prompts_dir: Path | None = None) -> str:
    """Return the ``compile_wiki.md`` system prompt text."""
    base = prompts_dir or default_prompts_directory()
    return (base / "compile_wiki.md").read_text(encoding="utf-8")


def default_prompts_directory() -> Path:
    """Resolve ``src/config/prompts`` relative to this package (scaffold)."""
    return Path(__file__).resolve().parents[2] / "config" / "prompts"
