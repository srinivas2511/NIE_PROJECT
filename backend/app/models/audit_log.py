from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AuditLog(Base):
    """FR-8/NFR-6: append-only record of every agent action, data access, and
    approval. Never updated or deleted by app code -- that omission is the
    immutability guarantee at the app-code level."""

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    # Role at the time of the action -- not just derived from user_id, since a
    # user's role can change later (FR-5) and the log should reflect the past.
    role: Mapped[str | None] = mapped_column(String(50), nullable=True)
    request_id: Mapped[int | None] = mapped_column(
        ForeignKey("enterprise_requests.id"), nullable=True, index=True
    )
    subtask_id: Mapped[int | None] = mapped_column(ForeignKey("sub_tasks.id"), nullable=True)
    context: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )

    user: Mapped["User | None"] = relationship()

    @property
    def user_email(self) -> str | None:
        return self.user.email if self.user else None
