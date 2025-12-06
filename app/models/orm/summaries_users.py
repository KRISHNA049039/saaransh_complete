from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import BigInteger, Boolean, DateTime, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.models.orm.base import Base
from app.settings import settings


class SummariesUsers(Base):
    __tablename__ = "summaries_users"
    __table_args__ = {"schema": settings.DB_SCHEMA}

    summaries_users_sk: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
    )

    summary_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
    )

    user_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
    )

    role_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
    )

    reviewed: Mapped[Optional[bool]] = mapped_column(Boolean)

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        server_default=text("true"),
        nullable=False,
    )

    created_by: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
    )

    created_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
