from __future__ import annotations

import logging
import os
from typing import Optional, TypedDict

import jwt as pyjwt
from fastapi import Header, HTTPException, Request

_logger = logging.getLogger(__name__)


class TenantContext(TypedDict):
    """Authenticated caller scope (tenant + profile preferences)."""

    tenant_id: str
    user_id: str
    locale: str
    department_id: Optional[str]


def _resolve_user_id(token: str) -> str:
    """Try live Supabase get_user; fall back to local JWT verification on any network failure."""
    try:
        from supabase import create_client

        supabase = create_client(
            os.environ["SUPABASE_URL"],
            os.environ["SUPABASE_SERVICE_ROLE_KEY"],
        )
        user_response = supabase.auth.get_user(token)
        if not user_response.user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        return str(user_response.user.id)
    except HTTPException:
        raise
    except Exception as exc:
        _logger.warning(
            "Supabase get_user failed (%s); falling back to local JWT verification", exc
        )

    jwt_secret = os.environ.get("SUPABASE_JWT_SECRET", "")
    if not jwt_secret:
        raise HTTPException(
            status_code=503,
            detail="Auth service unreachable and SUPABASE_JWT_SECRET not configured",
        )
    try:
        payload = pyjwt.decode(
            token,
            jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )
    except pyjwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail=f"Invalid token: {exc}") from exc

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="JWT missing sub claim")
    return str(user_id)


async def get_current_tenant_id(
    request: Request,
    authorization: str = Header(...),
) -> TenantContext:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401, detail="Missing or malformed Authorization header"
        )
    token = authorization.split(" ", 1)[1]

    user_id = _resolve_user_id(token)

    from supabase import create_client

    supabase = create_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_ROLE_KEY"],
    )
    result = (
        supabase.table("user_profiles")
        .select("tenant_id, locale, department_id")
        .eq("id", user_id)
        .single()
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=403, detail="No tenant assigned to this user")

    row = result.data
    header_locale = getattr(request.state, "locale", None) or "pl"
    profile_locale = row.get("locale") or header_locale
    if profile_locale not in ("pl", "en"):
        profile_locale = "pl"

    dept = row.get("department_id")
    department_id = str(dept) if dept else None

    return TenantContext(
        tenant_id=str(row["tenant_id"]),
        user_id=user_id,
        locale=profile_locale,
        department_id=department_id,
    )
