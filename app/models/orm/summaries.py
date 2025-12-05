from __future__ import annotations
from typing import Optional
from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, Text, Boolean, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import text

from app.models.orm.base import Base
from app.settings import settings


class Summary(Base):
    __tablename__ = "summaries"
    __table_args__ = {"schema": settings.DB_SCHEMA}
    __scd2__ = True

    summary_sk: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    summary_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), index=True, nullable=False
    )

    content: Mapped[Optional[str]] = mapped_column(Text)
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    status_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    meta_data: Mapped[Optional[dict]] = mapped_column("metadata", JSON)

    is_active: Mapped[bool] = mapped_column(
        Boolean, server_default=text("true"), nullable=False
    )

    created_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    created_by: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True))
    modified_by: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True))

    effective_from: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    effective_to: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    entity_type_id: Mapped[Optional[int]] = mapped_column(BigInteger)
