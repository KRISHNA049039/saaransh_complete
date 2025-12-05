import logging
from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.accessors.content_embeddings_accessor import ContentEmbeddingsAccessor
from app.models.orm.content_embeddings import ContentEmbedding
from app.components.embeddings_model import EmbeddingModel
from app.models.task_data import UserData
import app.utils.formatters as fmt

logger = logging.getLogger(__name__)


class ContentEmbeddingsBuilder:
    def __init__(self):
        self.embedding_accessor = ContentEmbeddingsAccessor()
        self.embedding_model = EmbeddingModel()

    def chunk_task_data(self, user_data: UserData) -> List[str]:
        chunks = []
        for i, task in enumerate(user_data.tasks, 1):

            chunks.append(
                f"{fmt.employee(user_data)} \n "
                f"Task {i} - {task.title} Description: {task.description}"
            )

            if task.comments:
                comments_text = (
                    f"Task {i} - {task.title} Description: {task.description}\nComments:\n"
                    + "\n".join(
                        [
                            f"- ({idx+1}) {comment.text}"
                            for idx, comment in enumerate(task.comments)
                        ]
                    )
                )
                chunks.append(comments_text)

            if task.logs:
                logs_text = (
                    f"Task {i} - {task.title} Description: {task.description}\nActivity Logs:\n"
                    + "\n".join(
                        [
                            f"- ({idx+1}) {log.content}"
                            for idx, log in enumerate(task.logs)
                        ]
                    )
                )
                chunks.append(logs_text)

        return chunks

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        logger.debug(f"Generating embeddings for {len(texts)} input chunks")
        embeddings = self.embedding_model.embed(texts)
        logger.debug("Embedding generation complete")
        return embeddings

    async def process_and_store_embeddings(
        self, summary_id: UUID | None, content: UserData, session: AsyncSession
    ) -> List[ContentEmbedding]:

        chunks = self.chunk_task_data(content)
        logger.debug(f"Generated {len(chunks)} text chunks for embedding")

        embeddings = self.embedding_model.embed(chunks)
        logger.debug(
            f"Generated {len(embeddings)} embeddings for summary_id={summary_id}"
        )

        results = []
        for idx, (chunk_text, emb) in enumerate(zip(chunks, embeddings)):
            record = ContentEmbedding(
                summary_id=summary_id,
                chunk_index=idx,
                content=chunk_text,
                embedding=emb,
                is_active=True,
            )
            inserted = await self.embedding_accessor.insert(record, session)
            results.append(inserted)

        logger.debug(
            f"Stored {len(results)} embeddings into DB for summary_id={summary_id}"
        )

        return results
