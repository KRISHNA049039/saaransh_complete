from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import JSON

class UserPromptsResponse(BaseModel):
    user_prompt_sk: Optional[int] = None
    content: Optional[str] = None
    summary_id: Optional[UUID] = None
    #meta_data: Optional[JSON] = None
    is_active: Optional[bool] = None
    created_by: Optional[UUID] = None
    created_date: Optional[datetime] = None

    model_config = {"from_attributes": True}