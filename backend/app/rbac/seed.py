from sqlalchemy.orm import Session

from app.models.role_permission import RolePermission
from app.rbac.roles import DEFAULT_ROLE_AGENT_PERMISSIONS


def seed_default_permissions(db: Session) -> int:
    """One-time seed: if role_permissions is empty, populate it from
    DEFAULT_ROLE_AGENT_PERMISSIONS. A no-op on every later startup, so it
    never overwrites an admin's edits made through the FR-11 UI."""
    if db.query(RolePermission).count() > 0:
        return 0

    rows = [
        RolePermission(role=role, agent_type=agent_type)
        for role, agent_types in DEFAULT_ROLE_AGENT_PERMISSIONS.items()
        for agent_type in agent_types
    ]
    db.add_all(rows)
    db.commit()
    return len(rows)
