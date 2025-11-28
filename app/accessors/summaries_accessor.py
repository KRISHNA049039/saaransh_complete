from sqlalchemy import update
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm.summaries import Summary
from app.accessors.base_db_accessor import BaseDBAccessor


class SummaryAccessor(BaseDBAccessor[Summary]):
    model = Summary

    async def close_active_record(self, summary_id, session: AsyncSession):
        query = (
            update(Summary)
            .where(
                Summary.summary_id == summary_id,
                Summary.effective_to.is_(None)
            )
            .values(effective_to=func.now())
        )
        await session.execute(query)

    async def insert(self, summary: Summary, session: AsyncSession) -> Summary:
        session.add(summary)
        await session.flush()
        await session.refresh(summary)
        return summary
