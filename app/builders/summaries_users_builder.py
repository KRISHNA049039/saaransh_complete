import uuid
import logging
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm.summaries_users import SummariesUsers
from app.models.request.summaries_users_request import (
    SummariesUsersCreateRequest,
    SummariesUsersFetchFilter,
)
from app.accessors.summaries_users_accessor import SummariesUsersAccessor
from app.accessors.summaries_accessor import SummaryAccessor
from app.accessors.user_accessor import UserAccessor
from app.models.response.summaries_users_response import SummariesUsersFullResponse
from app.utils.sort_util import SortQuery

logger = logging.getLogger(__name__)


class SummariesUsersBuilder:
    def __init__(
        self,
        session: AsyncSession,
        accessor: SummariesUsersAccessor | None = None,
    ):
        self.session = session
        self.accessor = accessor or SummariesUsersAccessor()

        self.summary_accessor = SummaryAccessor()
        self.user_accessor = UserAccessor()

    async def _fk_validator(self, summary_id: uuid.UUID, user_id: uuid.UUID):
        summary = await self.summary_accessor.get_by_summary_id(
            session=self.session,
            summary_id=summary_id,
            effective_only=True,
            is_active=True,
        )
        if summary is None:
            raise ValueError(f"Summary {summary_id} does not exist or is inactive")

        user = await self.user_accessor.get_by_user_id(
            session=self.session,
            user_id=user_id,
            effective_only=True,
            is_active=True,
        )
        if user is None:
            raise ValueError(f"User {user_id} does not exist or is inactive")

    async def build_create(
        self, request: SummariesUsersCreateRequest, action_by: uuid.UUID
    ) -> SummariesUsers:
        try:
            await self._fk_validator(request.summary_id, request.user_id)

            model = SummariesUsers(
                summary_id=request.summary_id,
                user_id=request.user_id,
                role_id=request.role_id,
                created_by=action_by,
                created_date=datetime.now(timezone.utc),
            )

            logger.debug(
                f"Creating summaries_users record for summary {request.summary_id}, "
                f"user {request.user_id}"
            )

            return await self.accessor.insert(model, self.session)

        except Exception as exc:
            logger.error(
                f"Failed to create summaries_users entry: {exc}", exc_info=True
            )
            raise

    async def build_fetch(self, filters: SummariesUsersFetchFilter, sort: SortQuery):
        logger.debug(f"Fetching summaries_users with filters={filters} sort={sort}")
        try:
            return await self.accessor.fetch(
                session=self.session, filters=filters, sort=sort
            )
        except Exception as exc:
            logger.error(f"Failed to fetch summaries_users: {exc}", exc_info=True)
            raise

    async def build_expanded_fetch(
        self, filters: SummariesUsersFetchFilter, sort: SortQuery
    ) -> list[SummariesUsersFullResponse]:
        logger.debug(
            f"Fetching expanded summaries_users with filters={filters} sort={sort}"
        )
        try:
            results = await self.accessor.get_expanded(self.session, filters, sort)
            output = []

            for su, user, summary in results:
                output.append(
                    SummariesUsersFullResponse(
                        summaries_users_sk=su.summaries_users_sk,
                        role_id=su.role_id,
                        reviewed=su.reviewed,
                        is_active=su.is_active,
                        created_by=su.created_by,
                        created_date=su.created_date,
                        user=user,
                        summary=summary,
                    )
                )

            return output
        except Exception as exc:
            logger.error(f"Failed to fetch summaries_users: {exc}", exc_info=True)
            raise
