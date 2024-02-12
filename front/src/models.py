from datetime import datetime, date
from enum import IntEnum
from pydantic import BaseModel


class State(IntEnum):
    new = 1
    started = 2
    ended = 3


class TaskModel(BaseModel):
    id: int
    text: str
    creation_date: datetime
    end_planned_date: date
    state: State
    category_id: int
    user_id: int


class CategoryModel(BaseModel):
    id: int
    name: str
    description: str | None = None
