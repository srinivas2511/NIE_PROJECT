from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SubTaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    agent_type: str
    description: str
    status: str
    result: str | None
    confidence: float | None
    explanation: str | None
    created_at: datetime
