from typing import Protocol, Any

class SCD2Model(Protocol):
    effective_to: Any

from pydantic import BaseModel

class SCD2Filter(BaseModel):
    effective_only: bool = True