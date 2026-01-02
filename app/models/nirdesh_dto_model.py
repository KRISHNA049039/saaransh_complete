from pydantic import BaseModel
from typing import List, Optional


class TaskDTO(BaseModel):
    id: str
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class SaaranshResponseDTO(BaseModel):
    Tasks: List[TaskDTO]


class SaaranshUserDTO(BaseModel):
    email: str
    name: Optional[str] = None
