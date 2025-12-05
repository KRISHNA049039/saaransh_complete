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

class User_Prompt(Base):
        __tablename__ = "user_prompts"
        __table_args__ = {"schema": settings.DB_SCHEMA}
        __scd2__ = False

        user_prompt_sk: Mapped[int] = mapped_column(BigInteger, primary_key=True)
        content: Mapped[Optional[str]] = mapped_column(Text)
        summary_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True))
        meta_data: Mapped[Optional[dict]] = mapped_column("metadata", JSON)
        is_active: Mapped[bool] = mapped_column(
            Boolean, server_default=text("true"), nullable=False
        )
        created_by: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True))
        created_date: Mapped[datetime] = mapped_column(
            DateTime(timezone=True),
            server_default=text("CURRENT_TIMESTAMP"),
            nullable=False,
        )
        entity_type_id: Mapped[int] = mapped_column(
                BigInteger, 
                default=5,
                nullable=False,
        )