from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Float
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class RagEvaluationRun(Base):
    """NFR-2: one row per admin-triggered RAG-vs-baseline evaluation run."""

    __tablename__ = "rag_evaluation_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    baseline_accuracy: Mapped[float] = mapped_column(Float, nullable=False)
    grounded_accuracy: Mapped[float] = mapped_column(Float, nullable=False)
    cases: Mapped[list] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
