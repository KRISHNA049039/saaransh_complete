
from uuid import UUID


async def query_knowledge_base(
    query: str, 
    summary_id: UUID, 
    top_k: int = 5
) -> str:
    try:
       

        return "not implemented"

    except Exception as e:
        return f"Error querying knowledge base: {e}"

tool_query_knowledge_base_definition = {
    "type": "function",
    "function": {
        "name": "query_knowledge_base",
        "description": "Search the vector knowledge base for relevant context.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "summary_id": {"type": "string"},
                "top_k": {"type": "integer"},
            },
            "required": ["query", "summary_id"]
        }
    }
}
