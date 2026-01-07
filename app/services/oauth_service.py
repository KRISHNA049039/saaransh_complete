"""
OAuth Service

Handles OAuth flows for external services like Asana.
"""

import secrets
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
import httpx
import logging
from urllib.parse import urlencode, parse_qs

from app.settings import settings
from app.models.auth_models import (
    AsanaTokenInfo, 
    OAuthState, 
    TokenResponse,
    AuthStatus
)

logger = logging.getLogger(__name__)


class AsanaOAuthService:
    """Service for handling Asana OAuth 2.0 flow"""
    
    def __init__(self):
        self.client_id = settings.ASANA_CLIENT_ID
        self.client_secret = settings.ASANA_CLIENT_SECRET
        self.redirect_uri = settings.ASANA_REDIRECT_URI
        self.scopes = settings.ASANA_OAUTH_SCOPES
        
        # Asana OAuth endpoints
        self.auth_url = "https://app.asana.com/-/oauth_authorize"
        self.token_url = "https://app.asana.com/-/oauth_token"
        self.revoke_url = "https://app.asana.com/-/oauth_revoke"
        
        # In-memory storage for OAuth states (use Redis in production)
        self._oauth_states: Dict[str, OAuthState] = {}
        
        # HTTP client for API calls
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    def generate_oauth_url(self, custom_redirect: Optional[str] = None) -> Tuple[str, str]:
        """
        Generate OAuth authorization URL and state
        
        Returns:
            Tuple of (oauth_url, state_id)
        """
        # Generate secure state parameter
        state_id = secrets.token_urlsafe(32)
        
        # Store state information
        oauth_state = OAuthState(
            state_id=state_id,
            redirect_url=custom_redirect,
            expires_at=datetime.utcnow() + timedelta(minutes=10)  # 10 minute expiry
        )
        self._oauth_states[state_id] = oauth_state
        
        # Build OAuth URL
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "state": state_id,
            "scope": self.scopes
        }
        
        oauth_url = f"{self.auth_url}?{urlencode(params)}"
        
        logger.info(f"Generated OAuth URL for state: {state_id}")
        return oauth_url, state_id
    
    async def exchange_code_for_token(self, code: str, state: str) -> Optional[AsanaTokenInfo]:
        """
        Exchange authorization code for access token
        
        Args:
            code: Authorization code from Asana
            state: State parameter for validation
            
        Returns:
            AsanaTokenInfo if successful, None otherwise
        """
        try:
            # Validate state
            if not self._validate_state(state):
                logger.error(f"Invalid OAuth state: {state}")
                return None
            
            # Prepare token exchange request
            token_data = {
                "grant_type": "authorization_code",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "redirect_uri": self.redirect_uri,
                "code": code
            }
            
            # Exchange code for token
            response = await self.http_client.post(
                self.token_url,
                data=token_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code != 200:
                logger.error(f"Token exchange failed: {response.status_code} - {response.text}")
                return None
            
            token_response = response.json()
            
            # Get user info with the new token
            user_info = await self._get_user_info(token_response["access_token"])
            
            # Create token info
            token_info = AsanaTokenInfo(
                access_token=token_response["access_token"],
                refresh_token=token_response.get("refresh_token"),
                expires_at=datetime.utcnow() + timedelta(seconds=token_response.get("expires_in", 3600)),
                scope=token_response.get("scope"),
                user_gid=user_info.get("gid") if user_info else None,
                user_email=user_info.get("email") if user_info else None
            )
            
            # Clean up state
            self._cleanup_state(state)
            
            logger.info(f"Successfully exchanged code for token for user: {token_info.user_email}")
            return token_info
            
        except Exception as e:
            logger.error(f"Error exchanging code for token: {e}")
            return None
    
    async def refresh_token(self, refresh_token: str) -> Optional[AsanaTokenInfo]:
        """
        Refresh an expired access token
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            New AsanaTokenInfo if successful, None otherwise
        """
        try:
            refresh_data = {
                "grant_type": "refresh_token",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": refresh_token
            }
            
            response = await self.http_client.post(
                self.token_url,
                data=refresh_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code != 200:
                logger.error(f"Token refresh failed: {response.status_code} - {response.text}")
                return None
            
            token_response = response.json()
            
            # Get user info with refreshed token
            user_info = await self._get_user_info(token_response["access_token"])
            
            # Create new token info
            token_info = AsanaTokenInfo(
                access_token=token_response["access_token"],
                refresh_token=token_response.get("refresh_token", refresh_token),
                expires_at=datetime.utcnow() + timedelta(seconds=token_response.get("expires_in", 3600)),
                scope=token_response.get("scope"),
                user_gid=user_info.get("gid") if user_info else None,
                user_email=user_info.get("email") if user_info else None
            )
            
            logger.info(f"Successfully refreshed token for user: {token_info.user_email}")
            return token_info
            
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            return None
    
    async def revoke_token(self, access_token: str) -> bool:
        """
        Revoke an access token
        
        Args:
            access_token: Access token to revoke
            
        Returns:
            True if successful, False otherwise
        """
        try:
            revoke_data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "token": access_token
            }
            
            response = await self.http_client.post(
                self.revoke_url,
                data=revoke_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            success = response.status_code == 200
            if success:
                logger.info("Successfully revoked token")
            else:
                logger.error(f"Token revocation failed: {response.status_code} - {response.text}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error revoking token: {e}")
            return False
    
    async def validate_token(self, access_token: str) -> Optional[Dict[str, Any]]:
        """
        Validate an access token by making a test API call
        
        Args:
            access_token: Access token to validate
            
        Returns:
            User info if token is valid, None otherwise
        """
        return await self._get_user_info(access_token)
    
    def get_oauth_redirect_url(self, state: str) -> Optional[str]:
        """
        Get the custom redirect URL for a given state
        
        Args:
            state: OAuth state parameter
            
        Returns:
            Custom redirect URL if exists, None otherwise
        """
        oauth_state = self._oauth_states.get(state)
        return oauth_state.redirect_url if oauth_state else None
    
    async def _get_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """
        Get user information using access token
        
        Args:
            access_token: Asana access token
            
        Returns:
            User info dict if successful, None otherwise
        """
        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            response = await self.http_client.get(
                "https://app.asana.com/api/1.0/users/me",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("data")
            else:
                logger.error(f"Failed to get user info: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            return None
    
    def _validate_state(self, state: str) -> bool:
        """
        Validate OAuth state parameter
        
        Args:
            state: State parameter to validate
            
        Returns:
            True if valid, False otherwise
        """
        oauth_state = self._oauth_states.get(state)
        if not oauth_state:
            return False
        
        # Check if state has expired
        if datetime.utcnow() > oauth_state.expires_at:
            self._cleanup_state(state)
            return False
        
        return True
    
    def _cleanup_state(self, state: str):
        """Clean up OAuth state"""
        self._oauth_states.pop(state, None)
    
    def cleanup_expired_states(self):
        """Clean up expired OAuth states"""
        now = datetime.utcnow()
        expired_states = [
            state_id for state_id, oauth_state in self._oauth_states.items()
            if now > oauth_state.expires_at
        ]
        
        for state_id in expired_states:
            self._oauth_states.pop(state_id, None)
        
        if expired_states:
            logger.info(f"Cleaned up {len(expired_states)} expired OAuth states")
    
    async def close(self):
        """Close HTTP client"""
        await self.http_client.aclose()


class AuthenticationService:
    """Service for managing authentication methods"""
    
    def __init__(self):
        self.oauth_service = AsanaOAuthService()
    
    async def get_auth_status(self, pat_token: Optional[str] = None, oauth_token: Optional[AsanaTokenInfo] = None) -> AuthStatus:
        """
        Get current authentication status
        
        Args:
            pat_token: Personal Access Token
            oauth_token: OAuth token information
            
        Returns:
            AuthStatus with current authentication state
        """
        # Check OAuth token first (preferred method)
        if oauth_token and oauth_token.access_token:
            # Check if token needs refresh
            needs_refresh = False
            if oauth_token.expires_at and datetime.utcnow() >= oauth_token.expires_at:
                needs_refresh = True
            
            # Validate token
            user_info = await self.oauth_service.validate_token(oauth_token.access_token)
            if user_info:
                return AuthStatus(
                    is_authenticated=True,
                    auth_method="oauth",
                    user_info=user_info,
                    token_expires_at=oauth_token.expires_at,
                    needs_refresh=needs_refresh
                )
        
        # Check PAT token
        if pat_token:
            user_info = await self._validate_pat_token(pat_token)
            if user_info:
                return AuthStatus(
                    is_authenticated=True,
                    auth_method="pat",
                    user_info=user_info,
                    token_expires_at=None,  # PAT tokens don't expire
                    needs_refresh=False
                )
        
        # No valid authentication
        return AuthStatus(
            is_authenticated=False,
            auth_method="none",
            user_info=None,
            token_expires_at=None,
            needs_refresh=False
        )
    
    async def _validate_pat_token(self, pat_token: str) -> Optional[Dict[str, Any]]:
        """
        Validate Personal Access Token
        
        Args:
            pat_token: Personal Access Token
            
        Returns:
            User info if valid, None otherwise
        """
        try:
            headers = {
                "Authorization": f"Bearer {pat_token}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    "https://app.asana.com/api/1.0/users/me",
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("data")
                else:
                    logger.error(f"PAT validation failed: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error validating PAT token: {e}")
            return None
    
    async def close(self):
        """Close services"""
        await self.oauth_service.close()


# Global service instances
oauth_service = AsanaOAuthService()
auth_service = AuthenticationService()