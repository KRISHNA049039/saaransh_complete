

from typing import Any
from authlib.integrations.httpx_client import AsyncOAuth2Client
from app.settings import settings
from datetime import datetime

TOKEN_URL = f"{settings.KEYCLOAK_URL}/realms/{settings.KEYCLOAK_CLIENT_REALM}/protocol/openid-connect/token"
CLIENT_ID = settings.KEYCLOAK_M2M_CLIENT_ID
CLIENT_SECRET = settings.KEYCLOAK_M2M_CLIENT_SECRET


class OAuth2Client:
    REFRESH_MARGIN = 30

    def __init__(self, client_id: str, client_secret: str, token_endpoint: str):
        self.client = AsyncOAuth2Client(
            client_id=client_id,
            client_secret=client_secret,
            token_endpoint=token_endpoint,
        )
        self._token: dict[str, Any] | None = None

    def _is_token_expired(self) -> bool:
        if not self._token:
            return True

        expires_at = self._token.get("expires_at")
        if not expires_at:
            return True
        return datetime.now().timestamp() >= (expires_at - self.REFRESH_MARGIN)

    async def _guarantee_token(self):
        if self._token is None or self._is_token_expired():
            token = await self.client.fetch_token(grant_type="client_credentials")
            self._token = token

    async def request(self, method: str, url: str, **kwargs):
        await self._guarantee_token()
        return await self.client.request(method, url, **kwargs)

    async def get(self, url: str, **kwargs):
        return await self.request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs):
        return await self.request("POST", url, **kwargs)

    def get_token_details(self):
        return self._token



def create_oauth2_client() -> OAuth2Client:
    return OAuth2Client(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        token_endpoint=TOKEN_URL,
        )


m2m_oauth2_client = create_oauth2_client()


ADMIN_TOKEN_URL = (
    f"{settings.KEYCLOAK_URL}/realms/{settings.KEYCLOAK_RESOURCE_REALM}/protocol/openid-connect/token"
    )

kc_admin_client = OAuth2Client(
    client_id=settings.KEYCLOAK_ADMIN_CLIENT_ID,
    client_secret=settings.KEYCLOAK_ADMIN_CLIENT_SECRET,
    token_endpoint=ADMIN_TOKEN_URL,
    )

