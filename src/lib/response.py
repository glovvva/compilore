"""Uniform JSON envelope for HTTP API responses (GapRoll-style metadata + optional AI context)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ResponseMeta(BaseModel):
    """Per-response correlation and timing (UTC)."""

    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    processing_time_ms: Optional[float] = None


class AIContext(BaseModel):
    """Optional provenance for AI-assisted operations."""

    ai_generated: bool = False
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None
    cost_usd: Optional[float] = None


class APIResponse(BaseModel, Generic[T]):
    """Standard API payload wrapper."""

    data: T
    meta: ResponseMeta = Field(default_factory=ResponseMeta)
    ai_context: Optional[AIContext] = None


def envelop(
    data: T,
    *,
    processing_time_ms: Optional[float] = None,
    ai_context: Optional[AIContext] = None,
) -> APIResponse[T]:
    """Build an :class:`APIResponse` with optional timing and AI metadata."""
    return APIResponse(
        data=data,
        meta=ResponseMeta(processing_time_ms=processing_time_ms),
        ai_context=ai_context,
    )
