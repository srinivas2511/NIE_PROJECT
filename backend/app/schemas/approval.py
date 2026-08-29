from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PendingApprovalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    agent_type: str
    description: str
    status: str
    result: str | None
    confidence: float | None
    explanation: str | None
    created_at: datetime
    request_id: int
    request_text: str
    requester_email: str


class RejectRequest(BaseModel):
    reason: str | None = None
