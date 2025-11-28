from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

class SummaryResponse(BaseModel):
    comment_id: UUID
    summary_id: UUID | None
    content: str | None
    created_date: datetime
    is_active: bool

    model_config = { "from_attributes": True }