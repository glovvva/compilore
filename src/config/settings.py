"""Application settings loaded from environment."""

from __future__ import annotations

import os

from pydantic import BaseModel, ConfigDict


def _env_bool(name: str, default: bool = False) -> bool:
    raw = (os.environ.get(name) or "").strip().lower()
    if not raw:
        return default
    return raw in {"1", "true", "yes", "on"}


class Settings(BaseModel):
    """Runtime feature flags and configuration."""

    model_config = ConfigDict(extra="forbid")

    TECHNICAL_ADVISOR_MODE: bool = False


settings = Settings(
    TECHNICAL_ADVISOR_MODE=_env_bool("TECHNICAL_ADVISOR_MODE", default=False),
)
