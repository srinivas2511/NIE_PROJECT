from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class SubTask(Base):
    __tablename__ = "sub_tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    request_id: Mapped[int] = mapped_column(
        ForeignKey("enterprise_requests.id"), nullable=False, index=True
    )
    agent_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    result: Mapped[str | None] = mapped_column(Text, nullable=True)
    # FR-6 (XAI): confidence (0.0-1.0) and the rationale behind it. Nullable
    # because pre-FR-6 rows and failed subtasks have neither.
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    request: Mapped["EnterpriseRequest"] = relationship(back_populates="subtasks")
