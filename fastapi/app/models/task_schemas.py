from pydantic import BaseModel, Field
from typing import Any, Optional
from uuid import UUID, uuid4
from datetime import datetime


class QueryBase(BaseModel):
    id: UUID = Field(default_factory=uuid4().hex)
    status: str
    message: Optional[str] = ""


class QueryTask(QueryBase):
    id: str
    type: str
    data: list[Any] = Field(default_factory=list)


class Query(QueryBase):
    subtasks: list[QueryTask] = Field(default_factory=list)
    creation_date: datetime = Field(default_factory=datetime.now)
    total_subtasks: int
    remaining_subtasks: int
