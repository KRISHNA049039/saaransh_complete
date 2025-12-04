from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_session
from app.builders.users_builder import UserBuilder
from app.config.security.resource_server import get_security_context
from app.config.security.security_context import SecurityContext
from app.models.request.users_request import (
    UserCreateRequest,
    UserEditRequest,
    UserFetchFilter,
)
from app.models.response.users_response import BulkUserCreateResponse, UserResponse
from app.utils.sort_util import SortQuery, parse_sort_query, sort_by
from app.accessors.user_accessor import UserAccessor

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=BulkUserCreateResponse)
async def create_users(
    requests: list[UserCreateRequest],
    session: AsyncSession = Depends(get_session),
    context: SecurityContext = Depends(get_security_context),
):
    builder = UserBuilder(session)
    response = await builder.build_create_users(
        requests=requests, created_by=context.user_id
    )

    if not response.success:
        return JSONResponse(status_code=400, content=response.model_dump())

    return response


@router.get("", response_model=list[UserResponse])
async def fetch_users(
    filters: UserFetchFilter = Depends(),
    sort_query: SortQuery = Depends(parse_sort_query),
    session: AsyncSession = Depends(get_session),
):
    DEFAULT_SORT = sort_by("-created_date")

    if not sort_query.sorts:
        sort_query = DEFAULT_SORT

    accessor = UserAccessor()
    return await accessor.fetch(session, filters=filters, sort=sort_query)


@router.put("", response_model=UserResponse)
async def update_users(
    request: UserEditRequest,
    session: AsyncSession = Depends(get_session),
    context: SecurityContext = Depends(get_security_context),
):
    builder = UserBuilder(session)
    return await builder.build_update_users(request, context.user_id)
