from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

from app.models.response.summaries_response import SummaryResponse
from app.models.response.users_response import UserResponse


class SummariesUsersResponse(BaseModel):
    summaries_users_sk: Optional[int] = None
    summary_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    role_id: Optional[int] = None
    reviewed: Optional[bool] = None
    is_active: Optional[bool] = None
    created_by: Optional[UUID] = None
    created_date: Optional[datetime] = None

    model_config = {"from_attributes": True}


class SummaryExpanded(BaseModel):
    summary_sk: int
    summary_id: UUID
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    status_id: Optional[int]
    meta_data: Optional[Dict[str, Any]]
    is_active: Optional[bool]
    created_date: Optional[datetime]
    created_by: Optional[UUID]
    modified_by: Optional[UUID]
    effective_from: Optional[datetime]
    effective_to: Optional[datetime]

    class Config:
        from_attributes = True


class SummariesUsersFullResponse(BaseModel):
    summaries_users_sk: Optional[int] = None
    summary: SummaryExpanded
    user: UserResponse
    role_id: Optional[int] = None
    reviewed: Optional[bool] = None
    is_active: Optional[bool] = None
    created_by: Optional[UUID] = None
    created_date: Optional[datetime] = None

    model_config = {"from_attributes": True}
