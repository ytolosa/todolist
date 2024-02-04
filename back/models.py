from datetime import datetime, date
from enum import IntEnum
from typing import Optional

from pydantic import BaseModel, FutureDate
from sqlmodel import Field, SQLModel, create_engine, Relationship


class State(IntEnum):
    new = 1
    started = 2
    ended = 3


class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    description: str = None
    tasks: "Task" = Relationship(back_populates="category")


class TaskIn(BaseModel):
    text: str
    end_planned_date: FutureDate
    state: State
    category_id: int


class TaskInModify(BaseModel):
    text: str = None
    end_planned_date: FutureDate = None
    state: State = None
    category_id: int = None


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, )
    text: str
    creation_date: datetime = Field(default_factory=datetime.now)
    end_planned_date: FutureDate
    state: State
    category_id: int = Field(default=None, foreign_key="category.id")
    user_id: int = Field(default=None, foreign_key="user.id")
    user: "User" = Relationship(back_populates="tasks")
    category: Category = Relationship(back_populates="tasks")


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(default=None, unique=True)
    password: str
    tasks: list[Task] = Relationship(back_populates="user")


engine = create_engine("sqlite:///database.db", echo=True)

SQLModel.metadata.create_all(engine)


class Token(BaseModel):
    access_token: str
    token_type: str
