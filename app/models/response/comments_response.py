from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class CommentResponse(BaseModel):
    comment_sk: Optional[int] = None
    comment_id: Optional[UUID] = None
    summary_id: Optional[UUID] = None
    content: Optional[str] = None
    is_active: Optional[bool] = None
    created_by: Optional[UUID] = None
    created_date: Optional[datetime] = None
    modified_by: Optional[UUID] = None
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None

    model_config = {"from_attributes": True}
