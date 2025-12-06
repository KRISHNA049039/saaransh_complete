from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.models.orm.comments import Comment
from app.models.request.comments_request import (
    CommentCreateRequest,
    CommentEditRequest,
    CommentFetchFilter,
)
from app.accessors.comments_accessor import CommentAccessor
from app.utils.sort_util import SortQuery

import logging

logger = logging.getLogger(__name__)


class CommentBuilder:
    def __init__(self, session: AsyncSession, accessor: CommentAccessor | None = None):
        self.session = session
        self.comments_accessor = accessor or CommentAccessor()

    async def build_create(
        self, request: CommentCreateRequest, action_by: uuid.UUID
    ) -> Comment:
        try:
            if request.summary_id is None:
                raise ValueError("Summary_id is required")

            new_comment_id = uuid.uuid4()

            model = Comment(
                comment_id=new_comment_id,
                summary_id=request.summary_id,
                content=request.content,
                created_by=action_by,
                effective_from=datetime.now(timezone.utc),
                effective_to=None,
            )
            logger.debug(
                f"Creating comment {new_comment_id} linked to summary {model.summary_id}"
            )
            return await self.comments_accessor.insert(model, self.session)
        except Exception as exception:
            logger.error(f"Failed to create comment: {exception}", exc_info=True)
            raise

    async def build_edit(
        self, request: CommentEditRequest, action_by: uuid.UUID
    ) -> Comment:
        try:
            if request.comment_id is None:
                raise ValueError("comment_id is required")

            filters = CommentFetchFilter(comment_id=request.comment_id)
            response = await self.comments_accessor.fetch(
                session=self.session, filters=filters, sort=None
            )

            if response is None or "":
                raise Exception("comment doesn't exist")

            old_record = response[0]

            await self.comments_accessor.close_active_record(
                request.comment_id, self.session
            )

            model = Comment(
                comment_id=request.comment_id,
                summary_id=old_record.summary_id,
                content=request.content,
                created_by=old_record.created_by,
                modified_by=action_by,
                created_date=old_record.created_date,
                effective_from=datetime.now(timezone.utc),
                effective_to=None,
            )
            logger.debug(f"Updating comment {request.comment_id}")
            return await self.comments_accessor.insert(model, self.session)
        except Exception as exception:
            logger.error(f"Failed to create comment: {exception}", exc_info=True)
            raise

    async def build_comments_fetch(self, filters: CommentFetchFilter, sort: SortQuery):
        logger.debug(f"Fetching comments with filters={filters} sort={sort}")
        try:
            return await self.comments_accessor.fetch(
                session=self.session, filters=filters, sort=sort
            )
        except Exception as exc:
            logger.error(f"Failed to fetch comments: {exc}", exc_info=True)
            raise
