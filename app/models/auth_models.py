"""
Authentication Models

Pydantic models for authentication and OAuth flows.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class AsanaOAuthRequest(BaseModel):
    """Request model for initiating Asana OAuth flow"""
    redirect_url: Optional[str] = Field(None, description="Custom redirect URL after OAuth completion")
    state: Optional[str] = Field(None, description="Custom state parameter for OAuth flow")


class AsanaOAuthCallback(BaseModel):
    """Model for Asana OAuth callback parameters"""
    code: str = Field(..., description="Authorization code from Asana")
    state: Optional[str] = Field(None, description="State parameter from OAuth flow")


class TokenResponse(BaseModel):
    """Response model for token operations"""
    access_token: str = Field(..., description="Access token")
    token_type: str = Field(default="Bearer", description="Token type")
    expires_in: Optional[int] = Field(None, description="Token expiration in seconds")
    refresh_token: Optional[str] = Field(None, description="Refresh token")
    scope: Optional[str] = Field(None, description="Token scope")


class AsanaTokenInfo(BaseModel):
    """Asana token information"""
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    scope: Optional[str] = None
    user_gid: Optional[str] = None
    user_email: Optional[str] = None


class UserSession(BaseModel):
    """User session information"""
    user_id: str
    user_email: Optional[str] = None
    asana_token: Optional[AsanaTokenInfo] = None
    created_at: datetime
    last_accessed: datetime
    expires_at: datetime


class AuthenticationMethod(BaseModel):
    """Authentication method configuration"""
    method_type: str = Field(..., description="Type of authentication (pat, oauth)")
    is_active: bool = Field(default=True, description="Whether this method is active")
    token_info: Optional[Dict[str, Any]] = Field(None, description="Token information")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AsanaAuthConfig(BaseModel):
    """Asana authentication configuration"""
    pat_token: Optional[str] = Field(None, description="Personal Access Token")
    oauth_enabled: bool = Field(default=False, description="Whether OAuth is enabled")
    oauth_token: Optional[AsanaTokenInfo] = Field(None, description="OAuth token information")
    preferred_method: str = Field(default="pat", description="Preferred authentication method")


class AuthStatus(BaseModel):
    """Authentication status response"""
    is_authenticated: bool
    auth_method: str  # "pat", "oauth", "none"
    user_info: Optional[Dict[str, Any]] = None
    token_expires_at: Optional[datetime] = None
    needs_refresh: bool = False


class OAuthState(BaseModel):
    """OAuth state information for security"""
    state_id: str
    redirect_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    user_session_id: Optional[str] = None