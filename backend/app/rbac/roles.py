from sqlalchemy.orm import Session

from app.models.role_permission import RolePermission

VALID_ROLES = {"employee", "hr", "admin"}
AGENT_TYPES = {"rag", "security", "analytics", "workflow", "validation"}

# What a fresh system starts with -- used only by app.rbac.seed's one-time
# seed. Live permission checks (can_use_agent) read from the DB
# (role_permissions), which is admin-editable per FR-11.
DEFAULT_ROLE_AGENT_PERMISSIONS: dict[str, set[str]] = {
    "employee": {"rag", "workflow", "validation"},
    "hr": {"rag", "workflow", "validation", "security", "analytics"},
    "admin": {"rag", "workflow", "validation", "security", "analytics"},
}


def can_use_agent(role: str, agent_type: str, db: Session) -> bool:
    return (
        db.query(RolePermission)
        .filter(RolePermission.role == role, RolePermission.agent_type == agent_type)
        .first()
        is not None
    )
