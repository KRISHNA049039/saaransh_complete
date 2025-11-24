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

        self.DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
        self.DATABASE_URL: str = os.getenv("DATABASE_URL", "")
        self.LLM_SDK: str = os.getenv("LLM_SDK", "litellm")

        self.SERVER_HOST: str = os.getenv("SERVER_HOST", "127.0.0.1")
        self.SERVER_PORT: int = int(os.getenv("SERVER_PORT", "8000"))

settings = Settings()
