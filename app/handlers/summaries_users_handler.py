from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.accessors.summaries_users_accessor import SummariesUsersAccessor
from app.builders.summaries_users_builder import SummariesUsersBuilder
from app.config.security.resource_server import get_security_context
from app.config.security.security_context import SecurityContext
from app.config.database import get_session

from app.models.request.summaries_users_request import (
    SummariesUsersCreateRequest,
    SummariesUsersFetchFilter,
)

from app.models.response.summaries_users_response import (
    SummariesUsersFullResponse,
    SummariesUsersResponse,
)
from app.utils.sort_util import SortQuery, parse_sort_query, sort_by


router = APIRouter(prefix="/share", tags=["share", "summaries", "users"])


@router.post("", response_model=SummariesUsersResponse)
async def create_summaries_user(
    request: SummariesUsersCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: SecurityContext = Depends(get_security_context),
):
    builder = SummariesUsersBuilder(session)
    summaries_user = await builder.build_create(request, context.user_id)
    return summaries_user


@router.get("/minimal", response_model=list[SummariesUsersResponse])
async def fetch_summaries_users(
    filters: SummariesUsersFetchFilter = Depends(),
    sort_query: SortQuery = Depends(parse_sort_query),
    session: AsyncSession = Depends(get_session),
):
    DEFAULT_SORT = sort_by("-created_date")
    if not sort_query.sorts:
        sort_query = DEFAULT_SORT

    builder = SummariesUsersBuilder(session)
    return await builder.build_fetch(filters, sort_query)


@router.get("", response_model=list[SummariesUsersFullResponse])
async def fetch_share(
    filters: SummariesUsersFetchFilter = Depends(),
    sort_query: SortQuery = Depends(parse_sort_query),
    session: AsyncSession = Depends(get_session),
):
    DEFAULT_SORT = sort_by("-created_date")
    if not sort_query.sorts:
        sort_query = DEFAULT_SORT

    builder = SummariesUsersBuilder(session)
    return await builder.build_expanded_fetch(filters, sort_query)
