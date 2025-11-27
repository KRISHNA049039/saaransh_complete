from sqlalchemy import select, update
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.orm.comments import Comment
from app.accessors.base_db_accessor import BaseDBAccessor

class CommentAccessor(BaseDBAccessor[Comment]):
    model = Comment

    async def close_active_record(self, comment_id, session: AsyncSession):
        query = (
            update(Comment)
            .where(
                Comment.comment_id == comment_id,
                Comment.effective_to.is_(None)
            )
            .values(effective_to=func.now())
        )
        await session.execute(query)

    async def insert(self, comment: Comment, session: AsyncSession) -> Comment:
        session.add(comment)
        await session.flush()
        await session.refresh(comment)
        return comment
    
    
