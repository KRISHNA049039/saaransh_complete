from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class UserResponse(BaseModel):
    user_sk: int | None = None
    user_id: UUID | None = None
    user_name: str | None = None
    user_email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool | None = None
    is_admin: bool | None = None
    effective_from: datetime | None = None
    effective_to: datetime | None = None
    created_by: UUID | None = None
    created_date: datetime | None = None
    error: str | None = None

    model_config = {"from_attributes": True}


class BulkUserCreateResponse(BaseModel):
    success: bool
    partial: bool
    results: list[UserResponse]
