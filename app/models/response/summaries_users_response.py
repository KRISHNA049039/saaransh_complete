from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


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
