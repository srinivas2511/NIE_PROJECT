from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class EnterpriseRequest(Base):
    __tablename__ = "enterprise_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="received")
    # NFR-5 (Performance): indexed -- list_requests orders by this on every
    # page load of a user's request list.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )
    # FR-12: set when run_orchestration finishes, regardless of final status --
    # completed_at - created_at is the end-to-end orchestration latency.
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship(back_populates="requests")
    subtasks: Mapped[list["SubTask"]] = relationship(
        back_populates="request", cascade="all, delete-orphan", order_by="SubTask.id"
    )
