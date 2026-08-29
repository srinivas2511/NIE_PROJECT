from datetime import datetime

from pydantic import BaseModel

from app.schemas.admin import AuditLogOut
from app.schemas.sub_task import SubTaskOut


class TraceRequestContext(BaseModel):
    id: int
    text: str
    requester_email: str
    status: str
    created_at: datetime
    completed_at: datetime | None


class DecisionTraceOut(BaseModel):
    subtask: SubTaskOut
    request: TraceRequestContext
    audit_trail: list[AuditLogOut]
