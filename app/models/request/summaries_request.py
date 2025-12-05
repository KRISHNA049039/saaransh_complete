from token import OP
from pydantic import BaseModel, UUID4
from typing import Optional
from app.models.task_data import UserData
from app.utils.scd2_protocol import SCD2Filter


class StagingCreateRequest(BaseModel):
    model: Optional[str] = None
    user_prompt: Optional[str] = None
    user_data: UserData


class SummaryFetchFilter(SCD2Filter):
    summary_sk: Optional[int] = None
    summary_id: Optional[UUID4] = None
    is_active: Optional[bool] = None


class SummaryCreateRequest(BaseModel):
    model: Optional[str] = None
    summary_id: Optional[UUID4] = None
    summary_sk: Optional[int] = None
    user_prompt: Optional[str] = None


class SummarySaveRequest(BaseModel):
    summary_sk: Optional[int] = None
    summary_id: Optional[UUID4] = None
    content: str


class SummaryEditRequest(BaseModel):
    summary_id: UUID4
    summary_sk: Optional[int] = None
    content: Optional[str] = None
    user_prompt: str
    staging: bool
