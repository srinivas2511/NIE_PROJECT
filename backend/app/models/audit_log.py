from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AuditLog(Base):
    """FR-8/NFR-6: append-only record of every agent action, data access,
    approval, auth event, and admin change. Immutability is enforced at the
    DB level, not just by app-code convention: a trigger
    (audit_logs_no_update_delete -> prevent_audit_log_mutation(), applied
    via a one-off migration -- see NFR-6) raises on any UPDATE or DELETE
    against this table, and fires for every role including superusers
    (the app's own DB role is one), so it can't be bypassed by a future
    app bug or a stray manual query the way an app-code-only convention
    could be."""

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
