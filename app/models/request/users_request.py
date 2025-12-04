from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from app.utils.scd2_protocol import SCD2Filter

class UserCreateRequest(BaseModel):
    user_email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    enabled: bool = True
    is_admin: bool = False

class UserFetchFilter(SCD2Filter):
    user_sk: Optional[int] = None
    user_id: Optional[UUID] = None
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    created_by: Optional[UUID] = None
