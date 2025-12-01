from fastapi import APIRouter, Depends
from typing import Optional
from app.config.security.resource_server import (
    get_current_user, 
    require_auth, 
    require_roles
)
from app.config.security.security_context import SecurityContext

router = APIRouter(prefix="/test", tags=["test"])


@router.get("/whoami")
async def who_am_i(claims: Optional[dict] = Depends(get_current_user)):
    if not claims:
        return {"authenticated": False}
    
    context = SecurityContext.from_claims(claims)
    return {
        "authenticated": True,
        "user_id": context.user_id,
        "username": context.username,
        "email": context.email,
        "roles": context.roles,
    }


@router.get("/protected")
async def protected_route(claims: dict = Depends(require_auth)):
    context = SecurityContext.from_claims(claims)
    return {
        "message": "You are authenticated!",
        "user": context.username,
        "roles": context.roles
    }


@router.get("/admin-only")
async def admin_only(claims: dict = Depends(require_roles("SAARANSH_ADMIN"))):
    context = SecurityContext.from_claims(claims)
    return {
        "message": "Welcome, admin!",
        "user": context.username
    }