"""Approximate Anthropic API cost from token usage (USD)."""

from __future__ import annotations

import os
from decimal import Decimal
from typing import Optional


def anthropic_usd_from_usage(
    input_tokens: int,
    output_tokens: int,
    *,
    input_per_mtok: Optional[Decimal] = None,
    output_per_mtok: Optional[Decimal] = None,
    env_input_key: str,
    env_output_key: str,
    default_input_per_mtok: str,
    default_output_per_mtok: str,
) -> Decimal:
    """Compute USD = (in/1e6)*rate_in + (out/1e6)*rate_out."""
    in_rate = input_per_mtok or Decimal(
        os.environ.get(env_input_key, default_input_per_mtok),
    )
    out_rate = output_per_mtok or Decimal(
        os.environ.get(env_output_key, default_output_per_mtok),
    )
    return (Decimal(input_tokens) / Decimal(1_000_000)) * in_rate + (
        Decimal(output_tokens) / Decimal(1_000_000)
    ) * out_rate
