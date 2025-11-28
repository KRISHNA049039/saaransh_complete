from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Integer, Text, TIMESTAMP, func, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector

from app.models.orm.base import Base
from app.settings import settings


class ContentEmbedding(Base):
    __tablename__ = "content_embeddings"
    __table_args__ = (
        Index(
            "content_embeddings_embedding_idx",
            "embedding",
            postgresql_using="ivfflat",
            postgresql_with={"lists": 100},
            postgresql_ops={"embedding": "vector_cosine_ops"}
        ),

        Index(
            "content_embeddings_metadata_gin",
            "metadata",
            postgresql_using="gin"
        ),

        Index(
            "content_embeddings_summary_id_idx",
            "summary_id"
        ),
        {"schema": settings.DB_SCHEMA},
    )

    embedding_sk: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )

    summary_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))

    chunk_index: Mapped[int | None] = mapped_column(Integer)

    content: Mapped[str] = mapped_column(Text, nullable=False)

    embedding: Mapped[list[float] | None] = mapped_column(Vector(768))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    meta_data: Mapped[dict | None] = mapped_column("metadata",JSONB)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )
