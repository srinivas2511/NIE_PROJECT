from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.sub_task import SubTaskOut


class RequestCreate(BaseModel):
    text: str = Field(min_length=1, max_length=8000)


class RequestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    text: str
    status: str
    created_at: datetime
    subtasks: list[SubTaskOut] = []
