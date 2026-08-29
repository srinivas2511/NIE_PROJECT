from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class RolePermission(Base):
    """FR-11: presence of a (role, agent_type) row means that role may use
    that agent type. Admin-editable via /api/admin/permissions; seeded once
    on first startup from app.rbac.roles.DEFAULT_ROLE_AGENT_PERMISSIONS."""

    __tablename__ = "role_permissions"
    __table_args__ = (UniqueConstraint("role", "agent_type", name="uq_role_agent_type"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    role: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    agent_type: Mapped[str] = mapped_column(String(50), nullable=False)
