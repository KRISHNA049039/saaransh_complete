# Dependency Injection and Configuration Patterns

## Overview

Saaransh Backend leverages FastAPI's built-in dependency injection system combined with custom configuration patterns to achieve loose coupling, testability, and maintainability. The system uses a combination of constructor injection, factory patterns, and FastAPI's `Depends()` mechanism to manage dependencies throughout the application.

## Architecture

### Dependency Injection Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    Handler Layer                            │
│  FastAPI dependencies injected via Depends()               │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                  Builder Layer                              │
│  Constructor injection with optional dependencies          │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                 Accessor Layer                              │
│  Factory pattern for service creation                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              Configuration Layer                            │
│  Environment-based settings with defaults                  │
└─────────────────────────────────────────────────────────────┘
```

## Configuration Management

### Settings Pattern

The application uses a centralized settings class that loads configuration from environment variables:

```python
class Settings:
    def __init__(self):
        self._load_env()

    def _load_env(self):
        # CORS Configuration
        self.CORS_ORIGINS: List[str] = get_list_env(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        )
        
        # Logging Configuration
        self.LOG_LEVEL: str = os.getenv("LOG_LEVEL", "DEBUG")
        
        # LLM Configuration
        self.LLM_SDK: str = os.getenv("LLM_SDK", "litellm")
        self.DEFAULT_LLM_MODEL: str = os.getenv(
            "DEFAULT_LLM_MODEL", "gemini/gemini-2.5-flash"
        )
        
        # Server Configuration
        self.SERVER_HOST: str = os.getenv("SERVER_HOST", "127.0.0.1")
        self.SERVER_PORT: int = int(os.getenv("SERVER_PORT", "8000"))
        
        # Database Configuration
        self.DB_URL: str = os.getenv("DB_URL", "")
        self.DB_SCHEMA: str = os.getenv("DB_SCHEMA", "")
        self.DB_DEBUG: bool = os.getenv("DB_DEBUG", "false").lower() == "true"
        self.DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "20"))
        self.DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
        
        # Keycloak Configuration
        self.KEYCLOAK_URL: str = os.getenv("KEYCLOAK_URL", "")
        self.KEYCLOAK_RESOURCE_REALM: str = os.getenv("KEYCLOAK_RESOURCE_REALM", "")
        # ... more Keycloak settings

# Global settings instance
settings = Settings()
```

### Configuration Features

1. **Environment Variable Loading**: Automatic loading from `.env` files
2. **Type Conversion**: Automatic conversion to appropriate Python types
3. **Default Values**: Sensible defaults for development environments
4. **List Parsing**: Helper function for comma-separated values
5. **Validation**: Type hints and runtime validation

### Helper Functions

```python
def get_list_env(key: str, default: str, sep=",") -> List[str]:
    """Parse comma-separated environment variables into lists."""
    value = os.getenv(key, default)
    return [v.strip() for v in value.split(sep) if v.strip()]
```

## Database Dependency Injection

### Database Session Management

The database layer uses FastAPI's dependency injection for session management:

```python
# Database Engine Configuration
engine = create_async_engine(
    settings.DB_URL,
    echo=settings.DB_DEBUG,
    pool_pre_ping=True,
    future=True,
    pool_size=settings.DB_POOL_SIZE, 
    max_overflow=settings.DB_MAX_OVERFLOW,
)

# Session Factory
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Dependency Function
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise
```

### Usage in Handlers

```python
@router.post("/summaries", response_model=SummaryResponse)
async def create_summary(
    request: SummaryCreateRequest,
    session: AsyncSession = Depends(get_session),  # Injected dependency
    context: SecurityContext = Depends(get_security_context),
):
    builder = SummaryBuilder(session=session)
    return await builder.build_summary(request, context.user_id)
```

### Benefits

1. **Automatic Transaction Management**: Commit on success, rollback on error
2. **Connection Pooling**: Efficient database connection reuse
3. **Testability**: Easy to mock database sessions for testing
4. **Resource Cleanup**: Automatic session cleanup

## Authentication and Security Injection

### Security Context Pattern

The security system uses a multi-layered dependency injection approach:

```python
# Base Security Dependency
security = HTTPBearer(auto_error=False)

# Token Verification
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

# Required Authentication
async def require_auth(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict[str, Any]:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    claims = verify_token(credentials.credentials)
    request.state.claims = claims
    return claims

# Security Context Creation
async def get_security_context(
    claims: dict = Depends(get_current_user)
) -> Optional[SecurityContext]:
    if not claims:
        return None
    return SecurityContext.from_claims(claims)
```

### Security Context Class

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
        """Create SecurityContext from JWT claims."""
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

### Role-Based Access Control

```python
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

# Usage
@router.post("/admin/users")
async def create_admin_user(
    request: UserCreateRequest,
    claims: dict = Depends(require_roles("SAARANSH_ADMIN"))
):
    # Only users with SAARANSH_ADMIN role can access
    pass
```

## Factory Pattern Integration

### LLM Service Factory

The system uses factory patterns for service creation:

```python
def get_llm_accessor(llm_sdk: Optional[str] = None) -> LLMAccessor:
    llm_sdk = settings.LLM_SDK.strip().lower() or "litellm"
    
    if llm_sdk == "litellm":
        return LiteLLMAccessor()
    else:
        raise ValueError(f"Unknown LLM sdk: {llm_sdk}")
```

### Usage in Builders

```python
class SummaryBuilder:
    def __init__(self, session: AsyncSession, summary_accessor: SummaryAccessor | None = None, llm_accessor: LLMAccessor | None = None):
        self.session = session
        self.summary_accessor = summary_accessor or SummaryAccessor()
        self.llm_accessor = llm_accessor or get_llm_accessor()  # Factory method
```

### Benefits

1. **Runtime Configuration**: Service selection based on configuration
2. **Easy Testing**: Mock different service implementations
3. **Extensibility**: Add new providers without changing existing code
4. **Centralized Creation**: Single point for service instantiation

## Singleton Pattern for Resources

### Embedding Model Singleton

For resource-intensive components, the system uses singleton pattern:

```python
class EmbeddingModelSingleton:
    _model = None

    @classmethod
    def get_model(cls, model_name: str = "sentence-transformers/all-mpnet-base-v2"):
        if cls._model is None:
            logger.info(f"Loading embedding model: {model_name}")
            cls._model = SentenceTransformer(model_name)
            logger.info("Embedding model loaded and ready")
        return cls._model

class EmbeddingModel:
    def __init__(self, model_name="sentence-transformers/all-mpnet-base-v2"):
        self.model = EmbeddingModelSingleton.get_model(model_name)

    def embed(self, texts):
        return self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
        ).tolist()
```

### Application Lifecycle Management

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize expensive resources
    EmbeddingModelSingleton.get_model()
    print("Embedding model loaded at startup")

    yield
    
    # Shutdown: Cleanup resources
    print("Shutting down Saaransh backend")

app = FastAPI(
    title="saaransh_backend",
    description="Backend service for Saaransh application",
    version="1.0.0",
    lifespan=lifespan,  # Lifecycle management
)
```

## Constructor Injection in Builders

### Flexible Constructor Design

Builders use constructor injection with optional dependencies:

```python
class SummaryBuilder:
    def __init__(
        self,
        session: AsyncSession,
        summary_accessor: SummaryAccessor | None = None,
        llm_accessor: LLMAccessor | None = None,
    ):
        self.session = session
        self.summary_accessor = summary_accessor or SummaryAccessor()
        self.llm_accessor = llm_accessor or get_llm_accessor()
        self.embedding_builder = ContentEmbeddingsBuilder()

class CommentBuilder:
    def __init__(self, session: AsyncSession, accessor: CommentAccessor | None = None):
        self.session = session
        self.comments_accessor = accessor or CommentAccessor()

class UserBuilder:
    def __init__(self, session: AsyncSession, accessor: UserAccessor | None = None):
        self.session = session
        self.user_accessor = accessor or UserAccessor()
        self.kc = get_keycloak_accessor()  # Factory method
```

### Benefits

1. **Testability**: Easy to inject mock dependencies
2. **Flexibility**: Override specific dependencies when needed
3. **Default Behavior**: Sensible defaults for normal operation
4. **Loose Coupling**: Depend on interfaces, not implementations

## Router-Level Dependency Injection

### Protected Routes

The application uses router-level dependencies for authentication:

```python
# Protected router with authentication requirement
protected_router = APIRouter(
    prefix="/api/v1", 
    dependencies=[Depends(require_auth)]  # Applied to all routes
)

# Add routers to protected router
protected_router.include_router(comments_router)
protected_router.include_router(summaries_router)
protected_router.include_router(users_router)

# Test router with same authentication
test_router = APIRouter(
    prefix="/api/v1/test", 
    dependencies=[Depends(require_auth)]
)

# Add routers to main app
app.include_router(protected_router)
app.include_router(test_router)
```

### Benefits

1. **Centralized Security**: Authentication applied consistently
2. **Easy Configuration**: Change authentication for entire router
3. **Clear Separation**: Public vs protected routes clearly defined
4. **Maintainability**: Single point of control for route security

## Middleware Integration

### CORS Configuration

```python
origins = settings.CORS_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Configuration-driven
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Logging Setup

```python
def setup_logging(level: str = "INFO"):
    logging.basicConfig(
        level=level.upper(),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

# Application startup
setup_logging(settings.LOG_LEVEL)  # Configuration-driven
```

## Testing Patterns

### Dependency Override for Testing

FastAPI's dependency injection makes testing straightforward:

```python
# Test setup
def get_test_session():
    # Return test database session
    pass

def get_test_llm_accessor():
    # Return mock LLM service
    pass

# Override dependencies for testing
app.dependency_overrides[get_session] = get_test_session
app.dependency_overrides[get_llm_accessor] = get_test_llm_accessor

# Test with overridden dependencies
def test_create_summary():
    response = client.post("/api/v1/summaries", json=test_data)
    assert response.status_code == 200
```

### Builder Testing

```python
# Test builder with mock dependencies
async def test_summary_builder():
    mock_session = Mock()
    mock_accessor = Mock()
    mock_llm = Mock()
    
    builder = SummaryBuilder(
        session=mock_session,
        summary_accessor=mock_accessor,
        llm_accessor=mock_llm
    )
    
    # Test with controlled dependencies
    result = await builder.build_summary(test_request, user_id)
    
    # Verify interactions
    mock_accessor.insert.assert_called_once()
    mock_llm.get_response.assert_called_once()
```

## Best Practices

### 1. Configuration Management
- Use environment variables for all configuration
- Provide sensible defaults for development
- Validate configuration at startup
- Group related settings logically

### 2. Dependency Injection
- Use constructor injection for long-lived dependencies
- Use FastAPI's `Depends()` for request-scoped dependencies
- Provide optional dependencies with defaults
- Keep dependency graphs shallow

### 3. Factory Patterns
- Use factories for complex object creation
- Make factories configurable through settings
- Cache expensive resources appropriately
- Handle factory errors gracefully

### 4. Security Dependencies
- Use router-level dependencies for consistent security
- Create reusable security dependencies
- Implement proper error handling for auth failures
- Cache security context to avoid repeated processing

### 5. Testing
- Override dependencies for testing
- Use dependency injection to isolate units under test
- Mock external services and databases
- Test dependency configuration separately

### 6. Resource Management
- Use singletons for expensive resources
- Initialize resources at application startup
- Clean up resources at shutdown
- Monitor resource usage and performance