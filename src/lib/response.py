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

    success: bool = True
    data: Optional[T] = None
    error: Optional[str] = None
    meta: ResponseMeta = Field(default_factory=ResponseMeta)
    available_actions: list[str] = Field(default_factory=list)
    ai_context: Optional[AIContext] = None


def envelop(
    data: T,
    *,
    processing_time_ms: Optional[float] = None,
    ai_context: Optional[AIContext] = None,
    available_actions: Optional[list[str]] = None,
    success: bool = True,
    error: Optional[str] = None,
) -> APIResponse[T]:
    """Build an :class:`APIResponse` with optional timing, AI metadata, and agent hints."""
    actions = list(available_actions) if available_actions is not None else []
    return APIResponse(
        success=success,
        data=data,
        error=error,
        meta=ResponseMeta(processing_time_ms=processing_time_ms),
        available_actions=actions,
        ai_context=ai_context,
    )
