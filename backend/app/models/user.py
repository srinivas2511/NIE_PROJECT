from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    # Default role for every new user; enforced per FR-4 (app/rbac/roles.py).
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="employee")
    # Continuously re-checked per FR-5 (app/rbac/zero_trust.py) -- deactivating
    # a user cuts off access immediately, not just at their next login.
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    requests: Mapped[list["EnterpriseRequest"]] = relationship(back_populates="user")
