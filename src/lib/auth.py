from fastapi import HTTPException, Header
from supabase import create_client
import os


async def get_current_tenant_id(authorization: str = Header(...)) -> str:
    token = authorization.removeprefix("Bearer ")
    supabase = create_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    )
    user_response = supabase.auth.get_user(token)
    if not user_response.user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    result = supabase.table("user_profiles") \
        .select("tenant_id") \
        .eq("id", user_response.user.id) \
        .single() \
        .execute()

    if not result.data:
        raise HTTPException(status_code=403, detail="No tenant assigned to this user")

    return result.data["tenant_id"]
