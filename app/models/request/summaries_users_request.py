from pydantic import BaseModel, UUID4
from typing import Optional


class SummariesUsersCreateRequest(BaseModel):
    summary_id: UUID4
    user_id: UUID4
    role_id: int


class SummariesUsersFetchFilter(BaseModel):
    summaries_users_sk: Optional[int] = None
    summary_id: Optional[UUID4] = None
    user_id: Optional[UUID4] = None
    role_id: Optional[int] = None
    reviewed: Optional[bool] = None
    is_active: Optional[bool] = None
