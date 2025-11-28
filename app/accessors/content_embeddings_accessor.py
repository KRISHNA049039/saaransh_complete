from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.accessors.base_db_accessor import BaseDBAccessor
from app.models.orm.content_embeddings import ContentEmbedding


class ContentEmbeddingsAccessor(BaseDBAccessor[ContentEmbedding]):
    model = ContentEmbedding

    async def insert(
        self,
        embedding_obj: ContentEmbedding,
        session: AsyncSession
    ) -> ContentEmbedding:
        session.add(embedding_obj)
        await session.flush()
        await session.refresh(embedding_obj)
        return embedding_obj

    async def find_similar(
        self,
        session: AsyncSession,
        embedding: list[float],
        limit: int = 5,
        summary_id: UUID | None = None
    ):
        query = select(self.model)

        if summary_id:
            query = query.where(self.model.summary_id == summary_id)

        query = query.order_by(self.model.embedding.cosine_distance(embedding))
        query = query.limit(limit)

        result = await session.execute(query)
        return result.scalars().all()