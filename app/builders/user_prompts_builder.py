from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from torch import Value

from app.models.orm.user_prompts import User_Prompt
from app.models.request.user_prompts_request import (
    UserPromptsCreateRequest,
    UserPromptsFetchFilter,
)
from app.accessors.user_prompts_accessor import UserPromptAccessor
from app.utils.sort_util import SortQuery

import logging

logger = logging.getLogger(__name__)

class UserPromptBuilder:
    def __init__(self, session: AsyncSession, accessor: UserPromptAccessor | None = None):
        self.session = session
        self.user_prompts_accessor = accessor or UserPromptAccessor()

    async def build_create(
            self, request: UserPromptsCreateRequest, action_by: uuid.UUID
    ) -> User_Prompt:
        try:
            if request.summary_id is None:
                raise ValueError("Summary_id is required")
            
            model = User_Prompt(
                content = request.content,
                summary_id = request.summary_id,
                created_by = action_by    
            )
            logger.debug(
                f"Creating user_prompt linked to summary {model.summary_id}"
            )
            return await self.user_prompts_accessor.insert(model, self.session)
        except Exception as exception:
            logger.error(f"Failed to create user_prompt: {exception}", exc_info=True)
            raise

    async def build_user_prompts_fetch(self, filters: UserPromptsFetchFilter, sort: SortQuery):
        logger.debug(f"Fetching user_prompts with filters={filters} sort={sort}")
        try:
            return await self.user_prompts_accessor.fetch(
                session=self.session, filters=filters, sort=sort
            )
        except Exception as exc:
            logger.error(f"Failed to fetch user_prompt: {exc}", exc_info=True)
            raise