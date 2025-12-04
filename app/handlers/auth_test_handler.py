from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from app.settings import settings
from app.config.security.oauth2_client import m2m_oauth2_client
from app.config.security.resource_server import (
    get_security_context, 
    require_roles
)
from app.config.security.security_context import SecurityContext

router = APIRouter(prefix="/auth", tags=["test"])


@router.get("/whoami")
async def who_am_i(context: Optional[SecurityContext] = Depends(get_security_context)):
    if not context:
        return {"authenticated": False}
    
    return {
        "authenticated": True,
        "user_id": context.user_id,
        "username": context.username,
        "email": context.email,
        "roles": context.roles,
    }


@router.get("/admin-only")
async def admin_only(claims: dict = Depends(require_roles("SAARANSH_ADMIN"))):
    context = SecurityContext.from_claims(claims)
    return {
        "message": "Welcome, admin!",
        "user": context.username
    }


@router.get("/m2m-check")
async def m2m_check():
    try:
        BASE_URL = settings.NIRDESH_DB_SERVICE_URL
        response = await m2m_oauth2_client.get(f"{BASE_URL}/api/users/m2m")
        token_info = m2m_oauth2_client.get_token_details()

        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            data = response.json()
        else:
            data = response.text
        return {
            "message": "M2M client credentials flow is working!",
            "token_expires_in": token_info.get("expires_in") if token_info else None,
            "token_expires_at": token_info.get("expires_at") if token_info else None,
            "token_type": token_info.get("token_type") if token_info else None,
            "response": data,
            "response_status": response.status_code,
            "response_headers": response.headers
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))