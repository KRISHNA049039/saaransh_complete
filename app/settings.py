import os
from typing import List
from dotenv import load_dotenv

load_dotenv()


def get_list_env(key: str, default: str, sep=",") -> List[str]:
    value = os.getenv(key, default)
    return [v.strip() for v in value.split(sep) if v.strip()]


class Settings:

    def __init__(self):
        self._load_env()

    def _load_env(self):
        self.CORS_ORIGINS: List[str] = get_list_env(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        )
        self.LOG_LEVEL: str = os.getenv("LOG_LEVEL", "DEBUG")

        self.LLM_SDK: str = os.getenv("LLM_SDK", "litellm")
        self.DEFAULT_LLM_MODEL: str = os.getenv(
            "DEFAULT_LLM_MODEL", "gemini/gemini-2.5-flash"
        )

        # Local LLM Configuration
        self.LOCAL_LLM_ENABLED: bool = os.getenv("LOCAL_LLM_ENABLED", "false").lower() == "true"
        self.LOCAL_LLM_HOST: str = os.getenv("LOCAL_LLM_HOST", "localhost")
        self.LOCAL_LLM_PORT: int = int(os.getenv("LOCAL_LLM_PORT", "11434"))
        self.LOCAL_LLM_MODEL: str = os.getenv("LOCAL_LLM_MODEL", "llama3.1:8b")
        self.LOCAL_LLM_TIMEOUT: int = int(os.getenv("LOCAL_LLM_TIMEOUT", "60"))
        self.LOCAL_LLM_TEMPERATURE: float = float(os.getenv("LOCAL_LLM_TEMPERATURE", "0.7"))
        self.LOCAL_LLM_CONTEXT_LENGTH: int = int(os.getenv("LOCAL_LLM_CONTEXT_LENGTH", "8192"))
        self.LOCAL_LLM_MAX_TOKENS: int = int(os.getenv("LOCAL_LLM_MAX_TOKENS", "4096"))

        self.SERVER_HOST: str = os.getenv("SERVER_HOST", "127.0.0.1")
        self.SERVER_PORT: int = int(os.getenv("SERVER_PORT", "8000"))

        self.DB_URL: str = os.getenv("DB_URL", "")
        self.DB_SCHEMA: str = os.getenv("DB_SCHEMA", "")
        self.DB_DEBUG: bool = os.getenv("DB_DEBUG", "false").lower() == "true"
        print("DB_POOL_SIZE from env:", repr(os.getenv("DB_POOL_SIZE")))

        self.DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", ""))
        self.DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", ""))

        self.NIRDESH_DB_SERVICE_URL: str = str(os.getenv("NIRDESH_DB_SERVICE_URL", ""))

        self.KEYCLOAK_URL: str = os.getenv("KEYCLOAK_URL", "")
        self.KEYCLOAK_RESOURCE_REALM: str = os.getenv("KEYCLOAK_RESOURCE_REALM", "")
        self.KEYCLOAK_CLIENT_REALM: str = os.getenv("KEYCLOAK_CLIENT_REALM", "")
        self.KEYCLOAK_M2M_CLIENT_ID: str = os.getenv("KEYCLOAK_M2M_CLIENT_ID", "")
        self.KEYCLOAK_M2M_CLIENT_SECRET: str = os.getenv(
            "KEYCLOAK_M2M_CLIENT_SECRET", ""
        )
        self.KEYCLOAK_ADMIN_CLIENT_ID: str = os.getenv(
            "KEYCLOAK_ADMIN_CLIENT_ID", "saaransh_admin_client"
        )
        self.KEYCLOAK_ADMIN_CLIENT_SECRET: str = os.getenv(
            "KEYCLOAK_ADMIN_CLIENT_SECRET", "aBSGZszfaWV2VajidbWcI9oZzPab9xJu"
        )

        self.KC_SAARANSH_ADMIN_ROLE: str = os.getenv(
            "KC_SAARANSH_ADMIN_ROLE", "SAARANSH_ADMIN"
        )

        # Asana Integration Configuration
        self.ASANA_ACCESS_TOKEN: str = os.getenv("ASANA_ACCESS_TOKEN", "")
        
        # Asana OAuth Configuration
        self.ASANA_CLIENT_ID: str = os.getenv("ASANA_CLIENT_ID", "")
        self.ASANA_CLIENT_SECRET: str = os.getenv("ASANA_CLIENT_SECRET", "")
        self.ASANA_REDIRECT_URI: str = os.getenv("ASANA_REDIRECT_URI", "http://localhost:8000/api/v1/auth/asana/callback")
        self.ASANA_OAUTH_SCOPES: str = os.getenv("ASANA_OAUTH_SCOPES", "default")
        
        # Authentication Configuration
        self.JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
        self.JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
        self.JWT_EXPIRATION_HOURS: int = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
        
        # Session Configuration
        self.SESSION_SECRET_KEY: str = os.getenv("SESSION_SECRET_KEY", "your-session-secret-change-in-production")
        self.SESSION_COOKIE_NAME: str = os.getenv("SESSION_COOKIE_NAME", "saaransh_session")
        self.SESSION_EXPIRE_SECONDS: int = int(os.getenv("SESSION_EXPIRE_SECONDS", "86400"))  # 24 hours


settings = Settings()
