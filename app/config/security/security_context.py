from typing import Optional
from uuid import UUID


class SecurityContext:
    def __init__(
        self,
        user_id: UUID,
        username: str,
        roles: list[str],
        email: Optional[str] = None,
        raw_claims: Optional[dict] = None
    ):
        self.user_id = user_id
        self.username = username
        self.roles = roles
        self.email = email
        self.raw_claims = raw_claims or {}
    
    @classmethod
    def from_claims(cls, claims: dict) -> "SecurityContext":
        """Create SecurityContext from JWT claims."""
        roles = claims.get("realm_access", {}).get("roles", [])
        username = claims.get("preferred_username") or claims.get("name", "unknown")
        
        return cls(
            user_id=claims["sub"],
            username=username,
            roles=roles,
            email=claims.get("email"),
            raw_claims=claims
        )
    
    def has_role(self, role: str) -> bool:
        return role in self.roles
    
    def has_any_role(self, *roles: str) -> bool:
        return any(role in self.roles for role in roles)
    
    def has_all_roles(self, *roles: str) -> bool:
        return all(role in self.roles for role in roles)