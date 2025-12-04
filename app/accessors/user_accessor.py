from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime, timezone

from app.accessors.base_db_accessor import BaseDBAccessor
from app.models.orm.users import User


class UserAccessor(BaseDBAccessor[User]):
    model = User

    async def close_active_record(self, user_id: UUID, session: AsyncSession):
        query = (
            update(User)
            .where(User.user_id == user_id, User.effective_to.is_(None))
            .values(effective_to=datetime.now(timezone.utc))
        )
        await session.execute(query)

    async def insert_commit(self, model: User, session: AsyncSession) -> User:
        session.add(model)
        await session.commit()
        await session.refresh(model)
        return model

    async def insert_flush(self, model: User, session: AsyncSession) -> User:
        session.add(model)
        await session.commit()
        await session.refresh(model)
        return model

    async def get_active_by_email(
        self, email: str, session: AsyncSession
    ) -> User | None:
        query = select(User).where(
            User.user_email == email, User.effective_to.is_(None)
        )
        result = await session.execute(query)
        return result.scalars().first()

    async def get_active_by_username(
        self, username: str, session: AsyncSession
    ) -> User | None:
        query = select(User).where(
            User.user_name == username, User.effective_to.is_(None)
        )
        result = await session.execute(query)
        return result.scalars().first()
