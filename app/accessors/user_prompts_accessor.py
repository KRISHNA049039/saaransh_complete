from sqlalchemy import select, update
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.orm.user_prompts import User_Prompt
from app.accessors.base_db_accessor import BaseDBAccessor

class UserPromptAccessor(BaseDBAccessor[User_Prompt]):
    model = User_Prompt

    async def close_active_record(self, user_prompt_sk, session: AsyncSession):
        query = (
            update(User_Prompt)
            .where(
                User_Prompt.user_prompt_sk == user_prompt_sk,
            )
        )
        await session.execute(query)

    async def insert(self, user_prompt: User_Prompt, session: AsyncSession) -> User_Prompt:
        session.add(user_prompt)
        await session.flush()
        await session.refresh(user_prompt)
        return user_prompt