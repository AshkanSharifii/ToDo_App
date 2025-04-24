from pydantic import BaseModel
from datetime import date
from typing import Optional

class TaskBase(BaseModel):
    title: str
    day: date

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    day: Optional[date] = None
    is_completed: Optional[bool] = None

class TaskOut(TaskBase):
    id: int
    is_completed: bool

    class Config:
        orm_mode = True