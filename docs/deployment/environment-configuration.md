# Environment Configuration

## Overview

Saaransh Backend uses environment-based configuration for flexible deployment across different environments. All configuration is managed through environment variables with sensible defaults for development and comprehensive options for production deployment.

## Environment Variables

### Core Application Settings

```bash
# Server Configuration
SERVER_HOST=127.0.0.1                    # Server bind address
SERVER_PORT=8000                         # Server port
LOG_LEVEL=DEBUG                          # Logging level (DEBUG, INFO, WARN, ERROR)

# CORS Configuration
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173  # Allowed origins (comma-separated)
```

### Database Configuration

```bash
# PostgreSQL Database
DB_URL=postgresql+asyncpg://username:password@hostname/database  # Database connection URL
DB_SCHEMA=saaransh                       # Database schema name
DB_DEBUG=true                            # Enable SQL query logging
DB_POOL_SIZE=20                          # Connection pool size
DB_MAX_OVERFLOW=10                       # Maximum overflow connections
```

### AI/LLM Configuration

```bash
# LLM Provider Settings
LLM_SDK=litellm                          # LLM SDK (always litellm)
DEFAULT_LLM_MODEL=gemini/gemini-2.5-flash  # Default model for AI operations

# Provider API Keys (choose based on your preferred provider)
GEMINI_API_KEY=your_gemini_api_key       # Google Gemini API key
OPENAI_API_KEY=your_openai_api_key       # OpenAI API key
ANTHROPIC_API_KEY=your_anthropic_api_key # Anthropic Claude API key
```

### Authentication (Keycloak)

```bash
# Keycloak Configuration
KEYCLOAK_URL=http://localhost:8081       # Keycloak server URL
KEYCLOAK_RESOURCE_REALM=saaransh         # Resource realm name
KEYCLOAK_CLIENT_REALM=nirdesh            # Client realm name

# Machine-to-Machine Client
KEYCLOAK_M2M_CLIENT_ID=saaransh_m2m_client      # M2M client ID
KEYCLOAK_M2M_CLIENT_SECRET=your_client_secret   # M2M client secret

# Admin Client
KEYCLOAK_ADMIN_CLIENT_ID=saaransh_admin_client          # Admin client ID
KEYCLOAK_ADMIN_CLIENT_SECRET=your_admin_client_secret   # Admin client secret

# Role Configuration
KC_SAARANSH_ADMIN_ROLE=SAARANSH_ADMIN    # Admin role name
```

### External Integrations

```bash
# Asana Integration
ENABLE_ASANA=true                        # Enable/disable Asana integration
ASANA_ACCESS_TOKEN=2/1212000333310446/1212371107783289:00bf8b93d27be1eb951707d09509979f

# Nirdesh Integration
ENABLE_NIRDESH=true                      # Enable/disable Nirdesh integration
NIRDESH_DB_SERVICE_URL=https://nirdesh-api.example.com  # Nirdesh service URL
```

## Environment Files

### Development (.env.example)

```bash
# Copy this file to .env and update with your values

# LLM Provider (choose one and set the corresponding API key)
GEMINI_API_KEY=your_gemini_api_key_here
# OPENAI_API_KEY=your_openai_api_key_here
LLM_SDK=litellm
LOG_LEVEL=DEBUG

# Database
DB_URL=postgresql+asyncpg://username:password@localhost/saaransh
DB_SCHEMA=saaransh
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
DB_DEBUG=true

# Keycloak
KEYCLOAK_URL=http://localhost:8081
KEYCLOAK_RESOURCE_REALM=saaransh
KEYCLOAK_CLIENT_REALM=nirdesh
KEYCLOAK_M2M_CLIENT_ID=your_m2m_client_id
KEYCLOAK_M2M_CLIENT_SECRET=your_m2m_client_secret

# External Integrations (optional)
ENABLE_ASANA=true
ASANA_ACCESS_TOKEN=your_asana_token_here
```

### Production Environment

```bash
# Production configuration template

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
LOG_LEVEL=INFO

# CORS (update with your frontend domains)
CORS_ORIGINS=https://app.yourdomain.com,https://admin.yourdomain.com

# Database (use production database)
DB_URL=postgresql+asyncpg://prod_user:secure_password@db.yourdomain.com/saaransh_prod
DB_SCHEMA=saaransh
DB_POOL_SIZE=50
DB_MAX_OVERFLOW=20
DB_DEBUG=false

# LLM (use production API keys)
GEMINI_API_KEY=${GEMINI_API_KEY}  # From secrets management
LLM_SDK=litellm
DEFAULT_LLM_MODEL=gemini/gemini-2.5-flash

# Keycloak (production instance)
KEYCLOAK_URL=https://auth.yourdomain.com
KEYCLOAK_RESOURCE_REALM=saaransh
KEYCLOAK_CLIENT_REALM=production
KEYCLOAK_M2M_CLIENT_ID=${KC_M2M_CLIENT_ID}
KEYCLOAK_M2M_CLIENT_SECRET=${KC_M2M_CLIENT_SECRET}
KEYCLOAK_ADMIN_CLIENT_ID=${KC_ADMIN_CLIENT_ID}
KEYCLOAK_ADMIN_CLIENT_SECRET=${KC_ADMIN_CLIENT_SECRET}

# Integrations
ENABLE_ASANA=true
ASANA_ACCESS_TOKEN=${ASANA_TOKEN}
```

## Configuration Management

### Settings Class Implementation

```python
class Settings:
    def __init__(self):
        self._load_env()

    def _load_env(self):
        # CORS Configuration with list parsing
        self.CORS_ORIGINS: List[str] = get_list_env(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        )
        
        # Logging
        self.LOG_LEVEL: str = os.getenv("LOG_LEVEL", "DEBUG")

        # LLM Configuration
        self.LLM_SDK: str = os.getenv("LLM_SDK", "litellm")
        self.DEFAULT_LLM_MODEL: str = os.getenv(
            "DEFAULT_LLM_MODEL", "gemini/gemini-2.5-flash"
        )

        # Server Configuration
        self.SERVER_HOST: str = os.getenv("SERVER_HOST", "127.0.0.1")
        self.SERVER_PORT: int = int(os.getenv("SERVER_PORT", "8000"))

        # Database Configuration with type conversion
        self.DB_URL: str = os.getenv("DB_URL", "")
        self.DB_SCHEMA: str = os.getenv("DB_SCHEMA", "")
        self.DB_DEBUG: bool = os.getenv("DB_DEBUG", "false").lower() == "true"
        self.DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "20"))
        self.DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))

        # External Services
        self.NIRDESH_DB_SERVICE_URL: str = str(os.getenv("NIRDESH_DB_SERVICE_URL", ""))

        # Keycloak Configuration
        self.KEYCLOAK_URL: str = os.getenv("KEYCLOAK_URL", "")
        self.KEYCLOAK_RESOURCE_REALM: str = os.getenv("KEYCLOAK_RESOURCE_REALM", "")
        self.KEYCLOAK_CLIENT_REALM: str = os.getenv("KEYCLOAK_CLIENT_REALM", "")
        self.KEYCLOAK_M2M_CLIENT_ID: str = os.getenv("KEYCLOAK_M2M_CLIENT_ID", "")
        self.KEYCLOAK_M2M_CLIENT_SECRET: str = os.getenv("KEYCLOAK_M2M_CLIENT_SECRET", "")
        self.KEYCLOAK_ADMIN_CLIENT_ID: str = os.getenv("KEYCLOAK_ADMIN_CLIENT_ID", "saaransh_admin_client")
        self.KEYCLOAK_ADMIN_CLIENT_SECRET: str = os.getenv("KEYCLOAK_ADMIN_CLIENT_SECRET", "default_secret")

        # Role Configuration
        self.KC_SAARANSH_ADMIN_ROLE: str = os.getenv("KC_SAARANSH_ADMIN_ROLE", "SAARANSH_ADMIN")

# Global settings instance
settings = Settings()
```

### Helper Functions

```python
def get_list_env(key: str, default: str, sep=",") -> List[str]:
    """Parse comma-separated environment variables into lists."""
    value = os.getenv(key, default)
    return [v.strip() for v in value.split(sep) if v.strip()]
```

## Environment-Specific Configurations

### Development Environment

**Characteristics:**
- Debug logging enabled
- Local database connections
- Relaxed CORS policies
- Development-friendly defaults

**Key Settings:**
```bash
LOG_LEVEL=DEBUG
DB_DEBUG=true
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
SERVER_HOST=127.0.0.1
```

### Staging Environment

**Characteristics:**
- Production-like configuration
- Staging database and services
- Limited external integrations
- Enhanced logging for testing

**Key Settings:**
```bash
LOG_LEVEL=INFO
DB_DEBUG=false
CORS_ORIGINS=https://staging.yourdomain.com
SERVER_HOST=0.0.0.0
DB_POOL_SIZE=30
```

### Production Environment

**Characteristics:**
- Optimized for performance and security
- Production databases and services
- All integrations enabled
- Comprehensive monitoring

**Key Settings:**
```bash
LOG_LEVEL=WARN
DB_DEBUG=false
CORS_ORIGINS=https://app.yourdomain.com
SERVER_HOST=0.0.0.0
DB_POOL_SIZE=50
DB_MAX_OVERFLOW=20
```

## Secrets Management

### Environment Variables vs Secrets

**Environment Variables (Non-sensitive):**
- Server configuration (host, port)
- Feature flags (ENABLE_ASANA)
- Public URLs and endpoints
- Logging levels and debug flags

**Secrets (Sensitive):**
- Database passwords and connection strings
- API keys (LLM providers, external services)
- Client secrets (Keycloak, OAuth)
- Access tokens

### Production Secrets Management

```bash
# Use secrets management systems in production
DB_URL=${DB_CONNECTION_STRING}           # From AWS Secrets Manager
GEMINI_API_KEY=${GEMINI_API_SECRET}      # From HashiCorp Vault
KEYCLOAK_M2M_CLIENT_SECRET=${KC_SECRET}  # From Kubernetes secrets
```

### Docker Secrets

```yaml
# docker-compose.yml
version: '3.8'
services:
  saaransh-backend:
    image: saaransh-backend:latest
    environment:
      - LOG_LEVEL=INFO
      - SERVER_HOST=0.0.0.0
      - DB_URL_FILE=/run/secrets/db_url
      - GEMINI_API_KEY_FILE=/run/secrets/gemini_key
    secrets:
      - db_url
      - gemini_key

secrets:
  db_url:
    external: true
  gemini_key:
    external: true
```

## Configuration Validation

### Startup Validation

```python
def validate_configuration():
    """Validate critical configuration at startup."""
    errors = []
    
    # Database configuration
    if not settings.DB_URL:
        errors.append("DB_URL is required")
    
    # LLM configuration
    if not any([
        os.getenv("GEMINI_API_KEY"),
        os.getenv("OPENAI_API_KEY"),
        os.getenv("ANTHROPIC_API_KEY")
    ]):
        errors.append("At least one LLM API key is required")
    
    # Keycloak configuration
    if not settings.KEYCLOAK_URL:
        errors.append("KEYCLOAK_URL is required")
    
    if errors:
        logger.error("Configuration validation failed:")
        for error in errors:
            logger.error(f"  - {error}")
        raise ValueError("Invalid configuration")
    
    logger.info("Configuration validation passed")

# Call during application startup
validate_configuration()
```

### Runtime Configuration Checks

```python
def check_integration_config():
    """Check integration configuration at runtime."""
    status = {}
    
    # Check Asana
    if os.getenv("ENABLE_ASANA", "false").lower() == "true":
        if os.getenv("ASANA_ACCESS_TOKEN"):
            status["asana"] = "configured"
        else:
            status["asana"] = "enabled_but_no_token"
    else:
        status["asana"] = "disabled"
    
    # Check Nirdesh
    if os.getenv("ENABLE_NIRDESH", "false").lower() == "true":
        if os.getenv("NIRDESH_DB_SERVICE_URL"):
            status["nirdesh"] = "configured"
        else:
            status["nirdesh"] = "enabled_but_no_url"
    else:
        status["nirdesh"] = "disabled"
    
    return status
```

## Deployment Configurations

### Docker Environment

```dockerfile
# Dockerfile
FROM python:3.12-slim

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY app/ /app/app/
COPY serve.py /app/

# Set working directory
WORKDIR /app

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "serve.py"]
```

### Kubernetes ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: saaransh-config
data:
  LOG_LEVEL: "INFO"
  SERVER_HOST: "0.0.0.0"
  SERVER_PORT: "8000"
  LLM_SDK: "litellm"
  DEFAULT_LLM_MODEL: "gemini/gemini-2.5-flash"
  DB_SCHEMA: "saaransh"
  DB_POOL_SIZE: "50"
  DB_MAX_OVERFLOW: "20"
  DB_DEBUG: "false"
  KEYCLOAK_RESOURCE_REALM: "saaransh"
  KEYCLOAK_CLIENT_REALM: "production"
  KC_SAARANSH_ADMIN_ROLE: "SAARANSH_ADMIN"
  ENABLE_ASANA: "true"
  ENABLE_NIRDESH: "true"
```

### Kubernetes Secrets

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: saaransh-secrets
type: Opaque
stringData:
  DB_URL: "postgresql+asyncpg://user:password@db:5432/saaransh"
  GEMINI_API_KEY: "your-gemini-api-key"
  KEYCLOAK_M2M_CLIENT_SECRET: "your-m2m-secret"
  KEYCLOAK_ADMIN_CLIENT_SECRET: "your-admin-secret"
  ASANA_ACCESS_TOKEN: "your-asana-token"
```

## Configuration Best Practices

### 1. Environment Separation
- Use different configuration files for each environment
- Never commit secrets to version control
- Use environment-specific defaults
- Validate configuration at startup

### 2. Secrets Management
- Use dedicated secrets management systems in production
- Rotate secrets regularly
- Limit access to secrets
- Monitor secret usage

### 3. Configuration Documentation
- Document all environment variables
- Provide example configurations
- Explain the impact of each setting
- Keep documentation up to date

### 4. Validation and Testing
- Validate configuration at startup
- Test with different configuration combinations
- Provide clear error messages for invalid configurations
- Monitor configuration changes

### 5. Deployment Automation
- Use infrastructure as code for configuration
- Automate configuration deployment
- Version control configuration templates
- Test configuration changes in staging first