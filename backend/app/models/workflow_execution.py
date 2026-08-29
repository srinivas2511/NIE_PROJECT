from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class WorkflowExecution(Base):
    """FR-9: one row per simulated-function step a WorkflowAgent ran -- a
    real persisted record of the automation, not just descriptive text."""

    __tablename__ = "workflow_executions"

    id: Mapped[int] = mapped_column(primary_key=True)
    subtask_id: Mapped[int] = mapped_column(ForeignKey("sub_tasks.id"), nullable=False, index=True)
    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    function_name: Mapped[str] = mapped_column(String(50), nullable=False)
    output: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
