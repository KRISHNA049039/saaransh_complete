from typing import Optional
from app.accessors.llm.llm_accessor import LLMAccessor
from app.accessors.llm.litellm_accessor import LiteLLMAccessor
from app.settings import settings


def get_llm_accessor(llm_sdk: Optional[str] = None) -> LLMAccessor:

    llm_sdk = settings.LLM_SDK.strip().lower() or "litellm"

    if llm_sdk == "litellm":
        return LiteLLMAccessor()
    
    else:
        raise ValueError(f"Unknown LLM sdk: {llm_sdk}")
