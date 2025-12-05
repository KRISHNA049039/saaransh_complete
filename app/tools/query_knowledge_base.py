from typing import Optional
from uuid import UUID

from app.components.embeddings_model import EmbeddingModel
from app.accessors.content_embeddings_accessor import ContentEmbeddingsAccessor
from app.config.database import SessionLocal
import logging

logger = logging.getLogger(__name__)

embedding_model = EmbeddingModel()
content_embedding_accessor = ContentEmbeddingsAccessor()


async def query_knowledge_base(
    query: str,
    summary_id: UUID,
    top_k: int = 5,
) -> str:

    async with SessionLocal() as session:
        try:
            query_vector = embedding_model.embed([query])[0]
            results = await content_embedding_accessor.find_similar(
                session=session,
                embedding=query_vector,
                summary_id=summary_id,
                limit=top_k,
            )

            if not results:
                return "No relevant context found."

            formatted_chunks = [
                f"[Match {i}] (chunk {rec.chunk_index})\n{rec.content}"
                for i, rec in enumerate(results, start=1)
            ]

            return "\n\n".join(formatted_chunks)

        except Exception as e:
            logger.exception("Error querying knowledge base")
            return f"Error querying knowledge base: {e}"


def make_query_knowledge_base_wrapper(summary_id: UUID):
    async def wrapper(query: str, top_k: int = 5):
        return await query_knowledge_base(
            query=query,
            summary_id=summary_id,
            top_k=top_k,
        )

    return wrapper


tool_query_knowledge_base_definition = {
    "type": "function",
    "function": {
        "name": "query_knowledge_base",
        "description": "Search the vector knowledge base for relevant context. minimum top_k is 3 and you can call this tool any number of times but only use it when you think rag is required for the user instruction",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "top_k": {"type": "integer"},
            },
            "required": ["query"],
        },
    },
}
