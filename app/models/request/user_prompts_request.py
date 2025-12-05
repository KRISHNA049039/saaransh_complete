from pydantic import BaseModel, UUID4
from typing import Optional
from app.utils.scd2_protocol import SCD2Filter

class UserPromptsCreateRequest(BaseModel):
    summary_id: UUID4
    content: str

class UserPromptsFetchFilter(BaseModel):
    user_prompt_sk: Optional[int] = None
    summary_id: Optional[UUID4] = None
    is_active: Optional[bool] = None