from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

from app.models.response.user_prompts_response import UserPromptsResponse


class SummaryResponse(BaseModel):
    summary_sk: int
    summary_id: UUID
    content: Optional[str]
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
    entity_type_id: Optional[int]

    class Config:
        from_attributes = True
