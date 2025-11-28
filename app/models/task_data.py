from pydantic import BaseModel
from typing import List, Optional


class Log(BaseModel):
    content: str

class Comment(BaseModel):
    text: str

class Task(BaseModel):
    title: str
    description: str
    comments: List[Comment]
    logs: List[Log]

class Employee(BaseModel):
    name: str
    role: str

class UserData(BaseModel):
    employee: Employee
    tasks: List[Task]