"""Deterministic post-search filtering for Technical Advisor ICP.

Post-search parameter matching for technical_advisor ICP. Called after
``hybrid_search`` and before synthesizer. Core Engine ``hybrid_search`` is
unchanged.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class SearchCandidate(BaseModel):
    """One retrieved wiki page candidate to evaluate."""

    model_config = ConfigDict(extra="forbid")

    slug: str
    title: str
    page_type: str
    technical_parameters: dict[str, Any] = Field(default_factory=dict)


class ParsedQuery(BaseModel):
    """Structured technical constraints parsed from user query."""

    model_config = ConfigDict(extra="forbid")

    hard_parameters: dict[str, Any] = Field(default_factory=dict)
    soft_parameters: dict[str, Any] = Field(default_factory=dict)


class EliminatedMatch(BaseModel):
    """Candidate removed from exact/partial buckets with explicit reason."""

    model_config = ConfigDict(extra="forbid")

    slug: str
    title: str
    reason: str


class ParameterMatch(BaseModel):
    """Candidate that survived hard-parameter filtering."""

    model_config = ConfigDict(extra="forbid")

    slug: str
    title: str
    matched_hard: list[str] = Field(default_factory=list)
    matched_soft: list[str] = Field(default_factory=list)
    unmet_soft: list[str] = Field(default_factory=list)


class ParameterFilterOutput(BaseModel):
    """Output buckets for downstream technical synthesis."""

    model_config = ConfigDict(extra="forbid")

    exact_matches: list[ParameterMatch] = Field(default_factory=list)
    partial_matches: list[ParameterMatch] = Field(default_factory=list)
    eliminated: list[EliminatedMatch] = Field(default_factory=list)


def _normalize_key(value: str) -> str:
    return value.strip().lower().replace(" ", "_")


def _to_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        s = value.strip().replace(",", ".")
        try:
            return float(s)
        except ValueError:
            return None
    return None


def _string_equal(a: Any, b: Any) -> bool:
    return str(a).strip().lower() == str(b).strip().lower()


def _match_scalar(expected: Any, actual: Any) -> bool:
    exp_num = _to_float(expected)
    act_num = _to_float(actual)
    if exp_num is not None and act_num is not None:
        return exp_num == act_num
    return _string_equal(expected, actual)


def _match_range(expected: dict[str, Any], actual: Any) -> bool:
    """Match query min/max constraint against scalar or range-like actual values."""
    min_v = _to_float(expected.get("min"))
    max_v = _to_float(expected.get("max"))
    if min_v is None and max_v is None:
        return False

    if isinstance(actual, dict):
        act_min = _to_float(actual.get("min"))
        act_max = _to_float(actual.get("max"))
        if act_min is not None and min_v is not None and act_min > min_v:
            return False
        if act_max is not None and max_v is not None and act_max < max_v:
            return False
        return True

    act_scalar = _to_float(actual)
    if act_scalar is None:
        return False
    if min_v is not None and act_scalar < min_v:
        return False
    if max_v is not None and act_scalar > max_v:
        return False
    return True


def _match_value(expected: Any, actual: Any) -> bool:
    if isinstance(expected, dict) and ("min" in expected or "max" in expected):
        return _match_range(expected, actual)
    if isinstance(expected, list):
        return any(_match_scalar(item, actual) for item in expected)
    return _match_scalar(expected, actual)


def _evaluate_parameter(
    page_parameters: dict[str, Any], parameter: str, expected: Any
) -> tuple[Literal["match", "missing", "mismatch"], str]:
    key = _normalize_key(parameter)
    normalized_params = {_normalize_key(k): v for k, v in page_parameters.items()}
    if key not in normalized_params:
        return "missing", f"missing parameter `{parameter}`"
    actual = normalized_params[key]
    if _match_value(expected, actual):
        return "match", ""
    return "mismatch", f"hard parameter `{parameter}` mismatch"


def filter_by_technical_parameters(
    results: list[SearchCandidate], parsed_query: ParsedQuery
) -> ParameterFilterOutput:
    """Filter hybrid-search candidates using deterministic parameter checks."""
    out = ParameterFilterOutput()

    for candidate in results:
        if candidate.page_type != "product_entity":
            out.eliminated.append(
                EliminatedMatch(
                    slug=candidate.slug,
                    title=candidate.title,
                    reason="not a product_entity page",
                )
            )
            continue

        matched_hard: list[str] = []
        hard_failed_reason: str | None = None
        for param, expected in parsed_query.hard_parameters.items():
            status, reason = _evaluate_parameter(candidate.technical_parameters, param, expected)
            if status != "match":
                hard_failed_reason = reason
                break
            matched_hard.append(param)

        if hard_failed_reason is not None:
            out.eliminated.append(
                EliminatedMatch(
                    slug=candidate.slug,
                    title=candidate.title,
                    reason=hard_failed_reason,
                )
            )
            continue

        matched_soft: list[str] = []
        unmet_soft: list[str] = []
        for param, expected in parsed_query.soft_parameters.items():
            status, _ = _evaluate_parameter(candidate.technical_parameters, param, expected)
            if status == "match":
                matched_soft.append(param)
            else:
                unmet_soft.append(param)

        row = ParameterMatch(
            slug=candidate.slug,
            title=candidate.title,
            matched_hard=matched_hard,
            matched_soft=matched_soft,
            unmet_soft=unmet_soft,
        )
        if not unmet_soft:
            out.exact_matches.append(row)
        else:
            out.partial_matches.append(row)

    return out
