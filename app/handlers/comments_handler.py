from fastapi import APIRouter, Depends, Query
from app.builders.comments_builder import CommentBuilder
from app.config.security.resource_server import get_security_context
from app.config.security.security_context import SecurityContext
from app.models.request.comments_request import (
    CommentCreateRequest,
    CommentEditRequest,
    CommentFetchFilter,
)
from app.models.response.comments_response import CommentResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.builders.comments_builder import CommentBuilder
from app.config.database import get_session
from app.utils.sort_util import SortQuery, parse_sort_query, sort_by

router = APIRouter(prefix="/comments", tags=["comments"])


@router.post("", response_model=CommentResponse)
async def create_comment(
    request: CommentCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: SecurityContext = Depends(get_security_context),
):
    builder = CommentBuilder(session)
    comment = await builder.build_create(request, context.user_id)
    return comment


@router.put("", response_model=CommentResponse)
async def edit_comment(
    request: CommentEditRequest,
    session: AsyncSession = Depends(get_session),
    context: SecurityContext = Depends(get_security_context),
):
    builder = CommentBuilder(session)
    comment = await builder.build_edit(request, context.user_id)
    return comment


@router.get("", response_model=list[CommentResponse])
async def fetch_comments(
    filters: CommentFetchFilter = Depends(),
    sort_query: SortQuery = Depends(parse_sort_query),
    session: AsyncSession = Depends(get_session),
    context: SecurityContext = Depends(get_security_context),
):
    DEFAULT_SORT = sort_by("-created_date")
    if not sort_query.sorts:
        sort_query = DEFAULT_SORT
    builder = CommentBuilder(session)
    return await builder.build_comments_fetch(filters, sort_query)
