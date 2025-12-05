from queue import Empty
import asyncio, logging, uuid
from uuid import UUID

from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.accessors.llm.llm_accessor import LLMAccessor
from app.accessors.llm.llm_factory import get_llm_accessor
from app.accessors.summaries_accessor import SummaryAccessor
from app.builders.content_embeddings_builder import ContentEmbeddingsBuilder
from app.models.orm.summaries import Summary
from app.models.request.summaries_request import (
    StagingCreateRequest,
    SummaryCreateRequest,
    SummaryFetchFilter,
)
from app.models.task_data import UserData
from typing import List, Optional
from app.settings import settings
import app.utils.prompts as prompts_template

import app.utils.formatters as fmt
from app.utils.sort_util import SortQuery


logger = logging.getLogger(__name__)


class SummaryBuilder:
    def __init__(
        self,
        session: AsyncSession,
        summary_accessor: SummaryAccessor | None = None,
        llm_accessor: LLMAccessor | None = None,
    ):
        self.session = session
        self.summary_accessor = summary_accessor or SummaryAccessor()
        self.llm_accessor = llm_accessor or get_llm_accessor()
        self.embedding_builder = ContentEmbeddingsBuilder()

    async def build_prompts_not_chunked(
        self, user_data: UserData
    ) -> List[tuple[str, List[str]]]:
        employee_info = fmt.employee(user_data)
        all_tasks_str = fmt.all_tasks(user_data.tasks)
        task_titles = [task.title for task in user_data.tasks]
        full_prompt = f"{employee_info}Tasks:\n{all_tasks_str}"
        return [(full_prompt, task_titles)]

    async def build_staging_summary(self, request: StagingCreateRequest):
        try:
            prompts = await self.build_prompts_not_chunked(request.user_data)
            (prompt, _) = prompts[0]

            summary_id = uuid.uuid4()
            model_name = request.model or settings.DEFAULT_LLM_MODEL

            llm_future = self.llm_accessor.get_response(
                model_name,
                prompt,
                request.user_prompt,
                prompts_template.STAGING_SUMMARY_PROMPT,
            )

            embedding_future = self.embedding_builder.process_and_store_embeddings(
                summary_id=summary_id,
                content=request.user_data,
                session=self.session,
            )

            llm_text, _ = await asyncio.gather(llm_future, embedding_future)

            summary = Summary(
                summary_id=summary_id,
                content=llm_text,
                start_date=None,
                end_date=None,
                meta_data={"model": model_name},
                effective_from=datetime.now(timezone.utc),
                effective_to=None,
            )
            response = await self.summary_accessor.insert(summary, self.session)
            logger.debug(
                f"Staging summary with summary_id:{summary_id} generated and inserted"
            )
            return response

        except Exception as e:
            raise

    async def build_summary_from_staging(self, request: SummaryCreateRequest):
        try:
            model_name = request.model or settings.DEFAULT_LLM_MODEL
            db_response = None
            if request.summary_sk is None and request.summary_id is None:
                raise ValueError("Either summary_sk or summary_id must be provided.")

            filters = SummaryFetchFilter(
                summary_sk=request.summary_sk,
                summary_id=request.summary_id,
                effective_only=bool(request.summary_id),
            )
            result = await self.summary_accessor.fetch(
                session=self.session, filters=filters, sort=None
            )
            db_response = result[0] if result else None

            if not db_response:
                raise ValueError("No summary found for given summary_sk/summary_id.")

            intermediate_summary = db_response.content or ""

            response = await self.llm_accessor.get_response(
                model_name,
                intermediate_summary,
                request.user_prompt,
                prompts_template.SUMMARY_PROMPT,
            )

            summary_id = uuid.uuid4()

            summary = Summary(
                summary_id=summary_id,
                content=response,
                start_date=None,
                end_date=None,
                meta_data={"model": model_name},
                effective_from=datetime.now(timezone.utc),
                effective_to=None,
            )

            inserted = await self.summary_accessor.insert(summary, self.session)

            logger.debug(
                f"Final summary created from staging summary_sk={request.summary_sk}, "
                f"summary_id={summary_id}"
            )

            return inserted

        except Exception as e:
            logger.exception("Error building summary from staging")
            raise

    async def build_summaries_fetch(self, filters: SummaryFetchFilter, sort: SortQuery):
        logger.debug(f"Fetching comments with filters={filters} sort={sort}")
        try:
            return await self.summary_accessor.fetch(
                session=self.session, filters=filters, sort=sort
            )
        except Exception as exc:
            logger.error(f"Failed to fetch comments: {exc}", exc_info=True)
            raise

    async def edit_summary_via_LLM(
        self,
        user_query: str,
        staging: bool,
        content: Optional[str] = None,
        model_name: str = settings.DEFAULT_LLM_MODEL,
        summary_sk: Optional[int] = None,
        summary_id: Optional[UUID] = None,
    ):
        if staging:
            system_prompt = prompts_template.EDIT_STAGING_PROMPT
        else:
            system_prompt = prompts_template.EDIT_PROMPT

        if content is None or "":
            filters = SummaryFetchFilter(
                summary_id=summary_id,
                summary_sk=summary_sk,
                effective_only=bool(summary_id),
            )
            result = await self.summary_accessor.fetch(
                session=self.session, filters=filters, sort=None
            )
            summary = result[0].content or ""
            if not result:
                raise ValueError(f"No summary found for summary_id={summary_id}")
        else:
            summary = content

        if summary is None or "":
            raise ValueError(f"content can't be empty")

        response = await self.llm_accessor.get_response(
            model=model_name,
            content=summary,
            user_prompt=f"{user_query} summary_id={summary_id}",
            system_prompt=system_prompt,
            use_tools=True,
        )

        await self.summary_accessor.close_active_record(
            summary_id=summary_id,
            session=self.session,
        )

        new_summary = Summary(
            summary_id=summary_id,
            content=response,
            start_date=None,
            end_date=None,
            meta_data={"model": model_name},
            effective_from=datetime.now(timezone.utc),
            effective_to=None,
        )

        inserted = await self.summary_accessor.insert(new_summary, self.session)
        return inserted

    async def save_modified_summary(
        self,
        modified_content: str,
        summary_sk: int | None = None,
        summary_id: UUID | None = None,
    ):

        filters = SummaryFetchFilter(
            summary_sk=summary_sk,
            summary_id=summary_id,
            effective_only=bool(summary_id),
        )

        result = await self.summary_accessor.fetch(
            session=self.session, filters=filters, sort=None
        )

        if not result:
            raise ValueError(f"No summary found with summary_id={summary_id}")

        old_record = result[0]

        await self.summary_accessor.close_active_record(
            summary_id=summary_id,
            session=self.session,
        )

        summary = Summary(
            summary_id=summary_id,
            content=modified_content,
            start_date=old_record.start_date,
            end_date=old_record.end_date,
            meta_data=old_record.meta_data,
            effective_from=datetime.now(timezone.utc),
            effective_to=None,
        )

        inserted = await self.summary_accessor.insert(summary, self.session)

        logger.debug(f"Saved modified summary {summary_id}")

        return inserted
