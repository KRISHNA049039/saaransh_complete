# Authentication and Security

## Overview

Saaransh Backend implements enterprise-grade authentication and authorization using **Keycloak** as the identity provider. The system uses OAuth2/OIDC standards with JWT tokens for secure API access and role-based access control (RBAC) for fine-grained permissions.

## Authentication Architecture

### Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client App    │    │  Saaransh API   │    │    Keycloak     │
│                 │    │                 │    │                 │
│ 1. Login Request│───▶│                 │    │                 │
│                 │    │ 2. Redirect to  │───▶│ 3. User Login   │
│                 │    │    Keycloak     │    │                 │
│                 │    │                 │◀───│ 4. Auth Code    │
│ 5. Access Token │◀───│                 │    │                 │
│                 │    │                 │    │                 │
│ 6. API Request  │───▶│ 7. Validate JWT │    │                 │
│    + JWT Token  │    │    Token        │    │                 │
│                 │    │                 │    │                 │
│ 8. API Response │◀───│                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Key Features

1. **OAuth2/OIDC Compliance**: Standard authentication protocols
2. **JWT Token Validation**: Stateless token verification
3. **Role-Based Access Control**: Fine-grained permissions
4. **Machine-to-Machine Authentication**: Service-to-service communication
5. **Token Caching**: Performance optimization with LRU cache
6. **Automatic Token Refresh**: Seamless token lifecycle management

## Authentication Flow

### 1. User Authentication

Users authenticate through Keycloak and receive JWT tokens:

```http
POST /realms/{realm}/protocol/openid-connect/token
Host: keycloak.example.com
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&
client_id=saaransh_client&
client_secret=client_secret&
code=authorization_code&
redirect_uri=https://app.example.com/callback
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "scope": "openid profile email"
}
```

### 2. API Request Authentication

All API requests must include the JWT token in the Authorization header:

```http
GET /api/v1/summaries
Host: api.saaransh.com
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 3. Token Validation Process

The API validates tokens through the following steps:

1. **Extract Token**: Parse Bearer token from Authorization header
2. **Fetch JWKS**: Retrieve public keys from Keycloak (cached)
3. **Verify Signature**: Validate token signature using public key
4. **Validate Claims**: Check expiration, issuer, and required claims
5. **Create Security Context**: Extract user information and roles

## Security Implementation

### JWT Token Validation

```python
def verify_token(token: str) -> dict[str, Any]:
    jwks = load_jwks()  # Cached JWKS from Keycloak
    
    try:
        decoded_token_object = jwt.decode(token, jwks)
        claims = dict(decoded_token_object.claims)
        
        # Validate required claims
        claims_registry = jwt.JWTClaimsRegistry(
            exp={"essential": True},      # Token expiration
            nbf={"essential": False},     # Not before
            iat={"essential": False},     # Issued at
            iss={"value": ISSUER},        # Issuer validation
            sub={"essential": True}       # Subject (user ID)
        )
        claims_registry.validate(claims)
        
        return claims
        
    except JoseError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation failed: {str(error)}",
            headers={"WWW-Authenticate": "Bearer"}
        )
```

### JWKS Caching

Public keys are cached for performance:

```python
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
```

### Security Context

User information is encapsulated in a SecurityContext:

```python
class SecurityContext:
    def __init__(self, user_id: UUID, username: str, roles: list[str], email: Optional[str] = None, raw_claims: Optional[dict] = None):
        self.user_id = user_id
        self.username = username
        self.roles = roles
        self.email = email
        self.raw_claims = raw_claims or {}

    @classmethod
    def from_claims(cls, claims: dict) -> "SecurityContext":
        roles = claims.get("realm_access", {}).get("roles", [])
        username = claims.get("preferred_username") or claims.get("name", "unknown")
        
        return cls(
            user_id=claims["sub"],
            username=username,
            roles=roles,
            email=claims.get("email"),
            raw_claims=claims,
        )

    def has_role(self, role: str) -> bool:
        return role in self.roles

    def is_admin(self) -> bool:
        return self.has_role(settings.KC_SAARANSH_ADMIN_ROLE)
```

## Authorization Patterns

### 1. Basic Authentication

Require valid authentication for all protected endpoints:

```python
@router.get("/summaries")
async def get_summaries(
    context: SecurityContext = Depends(get_security_context)
):
    # context contains user information
    return await get_user_summaries(context.user_id)
```

### 2. Role-Based Access Control

Restrict access based on user roles:

```python
@router.post("/admin/users")
async def create_user(
    request: UserCreateRequest,
    claims: dict = Depends(require_roles("SAARANSH_ADMIN"))
):
    # Only users with SAARANSH_ADMIN role can access
    return await create_new_user(request)
```

### 3. Multiple Role Requirements

Support flexible role requirements:

```python
# Require ANY of the specified roles
@router.get("/reports")
async def get_reports(
    claims: dict = Depends(require_roles("ADMIN", "MANAGER", mode="any"))
):
    pass

# Require ALL of the specified roles
@router.delete("/system/data")
async def delete_system_data(
    claims: dict = Depends(require_roles("ADMIN", "DATA_MANAGER", mode="all"))
):
    pass
```

### 4. Router-Level Security

Apply authentication to entire routers:

```python
# All routes in this router require authentication
protected_router = APIRouter(
    prefix="/api/v1", 
    dependencies=[Depends(require_auth)]
)

# Add individual routers
protected_router.include_router(summaries_router)
protected_router.include_router(comments_router)
protected_router.include_router(users_router)
```

## Machine-to-Machine Authentication

### OAuth2 Client Credentials Flow

For service-to-service communication:

```python
class OAuth2Client:
    def __init__(self, client_id: str, client_secret: str, token_endpoint: str):
        self.client = AsyncOAuth2Client(
            client_id=client_id,
            client_secret=client_secret,
            token_endpoint=token_endpoint,
        )
        self._token: dict[str, Any] | None = None

    async def _guarantee_token(self):
        if self._token is None or self._is_token_expired():
            token = await self.client.fetch_token(grant_type="client_credentials")
            self._token = token

    async def request(self, method: str, url: str, **kwargs):
        await self._guarantee_token()
        return await self.client.request(method, url, **kwargs)
```

### Usage Example

```python
# M2M client for external service calls
m2m_client = OAuth2Client(
    client_id=settings.KEYCLOAK_M2M_CLIENT_ID,
    client_secret=settings.KEYCLOAK_M2M_CLIENT_SECRET,
    token_endpoint=TOKEN_URL,
)

# Make authenticated request to external service
response = await m2m_client.get("https://external-api.com/data")
```

## API Authentication Examples

### 1. Login and Token Acquisition

**Request:**
```bash
curl -X POST "https://keycloak.example.com/realms/saaransh/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password&username=user@example.com&password=password&client_id=saaransh_client&client_secret=client_secret"
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "scope": "openid profile email"
}
```

### 2. Authenticated API Request

**Request:**
```bash
curl -X GET "https://api.saaransh.com/api/v1/summaries" \
  -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response:**
```json
{
  "summaries": [
    {
      "summary_id": "123e4567-e89b-12d3-a456-426614174000",
      "content": "AI-generated summary content...",
      "status": "SUBMITTED",
      "created_date": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### 3. Check Authentication Status

**Endpoint:** `GET /api/v1/test/auth/whoami`

**Request:**
```bash
curl -X GET "https://api.saaransh.com/api/v1/test/auth/whoami" \
  -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response:**
```json
{
  "authenticated": true,
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "username": "john.doe",
  "email": "john.doe@example.com",
  "roles": ["USER", "SAARANSH_ADMIN"]
}
```

### 4. Admin-Only Endpoint

**Endpoint:** `GET /api/v1/test/auth/admin-only`

**Request:**
```bash
curl -X GET "https://api.saaransh.com/api/v1/test/auth/admin-only" \
  -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Success Response (Admin User):**
```json
{
  "message": "Welcome, admin!",
  "user": "john.doe"
}
```

**Error Response (Non-Admin User):**
```json
{
  "detail": "Missing permissions. Required any of: SAARANSH_ADMIN"
}
```

## Error Handling

### Authentication Errors

| Status Code | Error | Description |
|-------------|-------|-------------|
| 401 | `Missing authentication token` | No Authorization header provided |
| 401 | `Token validation failed` | Invalid or expired JWT token |
| 401 | `Token verification error` | Token format or signature invalid |
| 403 | `Missing permissions` | User lacks required roles |
| 503 | `Cannot connect to Keycloak` | Keycloak service unavailable |

### Error Response Format

```json
{
  "detail": "Token validation failed: Token has expired",
  "headers": {
    "WWW-Authenticate": "Bearer"
  }
}
```

## Configuration

### Environment Variables

```bash
# Keycloak Configuration
KEYCLOAK_URL=https://keycloak.example.com
KEYCLOAK_RESOURCE_REALM=saaransh
KEYCLOAK_CLIENT_REALM=nirdesh

# M2M Client Credentials
KEYCLOAK_M2M_CLIENT_ID=saaransh_m2m_client
KEYCLOAK_M2M_CLIENT_SECRET=your_client_secret

# Admin Client Credentials
KEYCLOAK_ADMIN_CLIENT_ID=saaransh_admin_client
KEYCLOAK_ADMIN_CLIENT_SECRET=your_admin_secret

# Role Configuration
KC_SAARANSH_ADMIN_ROLE=SAARANSH_ADMIN
```

### Keycloak Setup

1. **Create Realm**: Set up `saaransh` realm in Keycloak
2. **Create Clients**: Configure OAuth2 clients for web app and M2M
3. **Define Roles**: Create `SAARANSH_ADMIN` and other required roles
4. **User Management**: Set up users and assign appropriate roles

## Security Best Practices

### 1. Token Security
- Use HTTPS for all token exchanges
- Implement proper token expiration times
- Store tokens securely on client side
- Implement token refresh mechanisms

### 2. Role Management
- Follow principle of least privilege
- Use granular roles for specific permissions
- Regularly audit user roles and permissions
- Implement role hierarchy when appropriate

### 3. API Security
- Validate all input parameters
- Implement rate limiting
- Log security events
- Use CORS policies appropriately

### 4. Error Handling
- Don't expose sensitive information in error messages
- Log security failures for monitoring
- Implement proper HTTP status codes
- Provide clear error messages for legitimate failures

## Testing Authentication

### Test Endpoints

The API provides test endpoints for authentication verification:

- `GET /api/v1/test/auth/whoami` - Check current user info
- `GET /api/v1/test/auth/admin-only` - Test admin role requirement
- `GET /api/v1/test/auth/m2m-check` - Test M2M authentication

### Integration Testing

```python
def test_authenticated_endpoint():
    # Get token from Keycloak
    token = get_test_token()
    
    # Make authenticated request
    response = client.get(
        "/api/v1/summaries",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200

def test_unauthorized_access():
    # Request without token
    response = client.get("/api/v1/summaries")
    
    assert response.status_code == 401
    assert "Missing authentication token" in response.json()["detail"]
```