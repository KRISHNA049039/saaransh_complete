from fastapi import APIRouter, Depends, Query
from app.builders.user_prompts_builder import UserPromptBuilder
from app.config.security.resource_server import get_security_context
from app.config.security.security_context import SecurityContext
from app.models.request.user_prompts_request import (
    UserPromptsCreateRequest,
    UserPromptsFetchFilter
)
from app.models.response.user_prompts_response import UserPromptsResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.builders.user_prompts_builder import UserPromptBuilder
from app.config.database import get_session
from app.utils.sort_util import SortQuery, parse_sort_query, sort_by

router = APIRouter(prefix="/userprompts", tags=["userprompts"])

@router.post("", response_model=UserPromptsResponse)
async def create_user_prompt(
    request: UserPromptsCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: SecurityContext = Depends(get_security_context),
):
    builder = UserPromptBuilder(session)
    user_prompt = await builder.build_create(request, context.user_id)
    return user_prompt

@router.get("", response_model=list[UserPromptsResponse])
async def fetch_user_prompts(
    filters: UserPromptsFetchFilter = Depends(),
    sort_query: SortQuery = Depends(parse_sort_query),
    session: AsyncSession = Depends(get_session),
    context: SecurityContext = Depends(get_security_context),
):
    DEFAULT_SORT = sort_by("-created_date")
    if not sort_query.sorts:
        sort_query = DEFAULT_SORT
    builder = UserPromptBuilder(session)
    return await builder.build_user_prompts_fetch(filters, sort_query)