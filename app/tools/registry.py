from app.tools.query_knowledge_base import query_knowledge_base, tool_query_knowledge_base_definition
from typing import Callable, Dict, Any


TOOL_REGISTRY: Dict[str, Callable[..., Any]] = {
    "query_knowledge_base": query_knowledge_base,
}


TOOL_DEFINITIONS = [
    tool_query_knowledge_base_definition
]
