from __future__ import annotations
from typing import Optional
from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import text

from app.models.orm.base import Base
from app.settings import settings


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": settings.DB_SCHEMA}
    __scd2__ = True

    user_sk: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    user_name: Mapped[Optional[str]] = mapped_column(String)
    user_email: Mapped[Optional[str]] = mapped_column(String)
    first_name: Mapped[Optional[str]] = mapped_column(String)
    last_name: Mapped[Optional[str]] = mapped_column(String)

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        server_default=text("true"),
        nullable=False
        )
    is_admin: Mapped[Optional[bool]] = mapped_column(Boolean)

    entity_type_id: Mapped[Optional[int]] = mapped_column(BigInteger)

    created_by: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True))

    created_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False
        )

    modified_by: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True))

    effective_from: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    effective_to: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))