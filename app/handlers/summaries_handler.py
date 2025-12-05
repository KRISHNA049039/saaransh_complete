from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import UUID4, BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.accessors.llm.llm_accessor import LLMAccessor
from app.accessors.llm.llm_factory import get_llm_accessor
from app.builders.summaries_builder import SummaryBuilder
from app.builders.user_prompts_builder import UserPromptBuilder
from app.config.database import get_session
from app.config.security.resource_server import get_security_context
from app.config.security.security_context import SecurityContext
from app.models.request.summaries_request import (
    StagingCreateRequest,
    SummaryCreateRequest,
    SummaryEditRequest,
    SummarySaveRequest,
    SummaryFetchFilter,
)
from app.models.request.user_prompts_request import UserPromptsCreateRequest
from app.models.response.summaries_response import SummaryResponse
from app.utils.sort_util import SortQuery, parse_sort_query, sort_by

router = APIRouter(prefix="/summaries", tags=["summaries"])


@router.post("/staging", response_model=SummaryResponse)
async def create_staging_summary(
    request: StagingCreateRequest,
    session: AsyncSession = Depends(get_session),
    llm_accessor: LLMAccessor = Depends(get_llm_accessor),
    context: SecurityContext = Depends(get_security_context),
):
    builder = SummaryBuilder(session=session, llm_accessor=llm_accessor)
    return await builder.build_staging_summary(request, context.user_id)


@router.post("/final", response_model=SummaryResponse)
async def create_final_summaries(
    request: SummaryCreateRequest,
    session: AsyncSession = Depends(get_session),
    llm_accessor: LLMAccessor = Depends(get_llm_accessor),
    context: SecurityContext = Depends(get_security_context),
):
    builder = SummaryBuilder(session=session, llm_accessor=llm_accessor)
    return await builder.build_summary_from_staging(request, context.user_id)


@router.get("", response_model=list[SummaryResponse])
async def fetch_summaries(
    filters: SummaryFetchFilter = Depends(),
    sort_query: SortQuery = Depends(parse_sort_query),
    session: AsyncSession = Depends(get_session),
):
    DEFAULT_SORT = sort_by("-created_date")
    if not sort_query.sorts:
        sort_query = DEFAULT_SORT
    builder = SummaryBuilder(session)
    return await builder.build_summaries_fetch(filters, sort_query)


@router.put("/save", response_model=list[SummaryResponse])
async def save_modified_summary(
    request: SummarySaveRequest,
    session: AsyncSession = Depends(get_session),
    context: SecurityContext = Depends(get_security_context),
):
    builder = SummaryBuilder(session)
    return await builder.save_modified_summary(
        summary_id=request.summary_id,
        summary_sk=request.summary_sk,
        modified_content=request.content,
        action_by=context.user_id,
    )


@router.put("/edit", response_model=SummaryResponse)
async def edit_summary_via_LLM(
    request: SummaryEditRequest,
    session: AsyncSession = Depends(get_session),
    context: SecurityContext = Depends(get_security_context),
):
    summary_builder = SummaryBuilder(session)
    summary_response = await summary_builder.edit_summary_via_LLM(
        summary_id=request.summary_id,
        summary_sk=request.summary_sk,
        content=request.content,
        user_query=request.user_prompt,
        staging=request.staging,
        action_by=context.user_id,
    )

    prompt_builder = UserPromptBuilder(session)
    user_prompt = UserPromptsCreateRequest(
        summary_id=request.summary_id,
        content=request.user_prompt,
    )
    await prompt_builder.build_create(user_prompt, context.user_id)
    return summary_response
