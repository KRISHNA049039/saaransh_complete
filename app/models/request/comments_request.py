from pydantic import BaseModel, UUID4
from typing import Optional
from app.utils.scd2_protocol import SCD2Filter

class CommentCreateRequest(BaseModel):
    comment_id: Optional[UUID4] = None
    summary_id: UUID4
    content: str

class CommentFetchFilter(SCD2Filter):
    comment_sk: Optional[int] = None
    comment_id: Optional[UUID4] = None
    summary_id: Optional[UUID4] = None
    is_active: Optional[bool] = None
  