from pydantic import BaseModel, Field
from typing import Any, Optional
from uuid import UUID, uuid4


class TaskModel(BaseModel):
    id: UUID = Field(default_factory=uuid4().hex)
    status: str
    message: Optional[str] = ""


class ScrapperTaskModel(TaskModel):
    id: str
    type: str
    data: list[Any] = Field(default_factory=list)


class GlobalTaskModel(TaskModel):
    subtasks: list[ScrapperTaskModel] = Field(default_factory=list)
    total_subtasks: int
    remaining_subtasks: int
