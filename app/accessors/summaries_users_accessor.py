from typing import Optional
from uuid import UUID
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from app.accessors.base_db_accessor import BaseDBAccessor
from app.models.orm.summaries_users import SummariesUsers
from sqlalchemy import select


class SummariesUsersAccessor(BaseDBAccessor[SummariesUsers]):
    model = SummariesUsers

    async def delete(self, summaries_users_sk: int, session: AsyncSession):
        query = (
            update(SummariesUsers)
            .where(SummariesUsers.summaries_users_sk == summaries_users_sk)
            .values(is_active=False)
        )
        await session.execute(query)

    async def insert(
        self, summaries_user: SummariesUsers, session: AsyncSession
    ) -> SummariesUsers:
        session.add(summaries_user)
        await session.flush()
        await session.refresh(summaries_user)
        return summaries_user

    async def get_role(
        self,
        summary_id: UUID,
        user_id: UUID,
        session: AsyncSession,
    ) -> Optional[int]:
        query = select(SummariesUsers.role_id).where(
            SummariesUsers.summary_id == summary_id,
            SummariesUsers.user_id == user_id,
            SummariesUsers.is_active == True,
        )

        result = await session.execute(query)
        return result.scalar_one_or_none()
