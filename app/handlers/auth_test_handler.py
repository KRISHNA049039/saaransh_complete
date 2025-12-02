from fastapi import APIRouter, Depends
from typing import Optional
from app.config.security.resource_server import (
    get_security_context, 
    require_roles
)
from app.config.security.security_context import SecurityContext

router = APIRouter(prefix="/test/auth", tags=["test"])


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