
import httpx
from joserfc import jwt
from joserfc.jwk import KeySet
from joserfc.errors import JoseError
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from functools import lru_cache
from typing import Any, Literal, Optional
from app.config.security.security_context import SecurityContext
from app.settings import settings
from fastapi import Request

KEYCLOAK_URL = settings.KEYCLOAK_URL
KEYCLOAK_REALM = settings.KEYCLOAK_RESOURCE_REALM
JWKS_URL = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/certs"
ISSUER = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}"

security = HTTPBearer(auto_error=False)


@lru_cache()
def load_jwks() -> KeySet:
    try:
        response = httpx.get(JWKS_URL, timeout=10.0)
        response.raise_for_status()
        return KeySet.import_key_set(response.json())
    except httpx.ConnectError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Cannot connect to Keycloak: {str(error)}"
        )
    except httpx.HTTPError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to fetch JWKS: {str(error)}"
        )


def verify_token(token: str) -> dict[str, Any]:
    jwks = load_jwks()

    try:
        decoded_token_object = jwt.decode(token, jwks)
        claims = dict(decoded_token_object.claims)
        
        claims_registry = jwt.JWTClaimsRegistry(
            exp={"essential": True},
            nbf={"essential": False},
            iat={"essential": False},
            iss={"value": ISSUER},
            sub={"essential": True}
        )
        claims_registry.validate(claims)
        
        return claims
        
    except JoseError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation failed: {str(error)}",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification error: {str(error)}",
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[dict]:
    if hasattr(request.state, "claims"):
        return request.state.claims

    if not credentials:
        return None

    claims = verify_token(credentials.credentials)
    request.state.claims = claims
    return claims



async def require_auth(
        request: Request,
        credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict[str, Any]:
    """
    Authentication dependency. Raises 401 if not authenticated.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    claims = verify_token(credentials.credentials)
    request.state.claims = claims
    return claims


async def get_security_context(
    claims: dict = Depends(get_current_user)
) -> Optional[SecurityContext]:
    if not claims:
        return None
    return SecurityContext.from_claims(claims)


def require_roles(*roles: str, mode: Literal["any", "all"] = "any"):

    async def checker(claims: dict[str, Any] = Depends(require_auth)) -> dict[str, Any]:
        user_roles = set(claims.get("realm_access", {}).get("roles", []))
        required = set(roles)
        if mode == "all":
            authorized = user_roles.issuperset(required)
        else:
            authorized = not user_roles.isdisjoint(required)

        if not authorized:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permissions. Required {mode} of: {', '.join(roles)}"
            )
        return claims
        
    return checker