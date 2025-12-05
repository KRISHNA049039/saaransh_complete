from abc import ABC, abstractmethod
from typing import Dict, Any
from typing import Optional


class LLMAccessor(ABC):

    @abstractmethod
    async def get_response(
        self,
        model: str,
        content: str,
        user_prompt: Optional[str],
        system_prompt: str,
        use_tools: bool = False,
        tool_schemas=None,
        tool_registry=None,
    ) -> str:
        """LLM response"""
        pass

    @abstractmethod
    async def get_token_count(self, text: str) -> int:
        """Calculates the token count for a given text"""
        pass
