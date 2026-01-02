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


settings = Settings()
