# Role administration (creating/editing roles and permissions through a UI)
# is FR-11's job. This module just defines the roles and the agent
# permissions FR-4 enforces.

VALID_ROLES = {"employee", "hr", "admin"}

ROLE_AGENT_PERMISSIONS: dict[str, set[str]] = {
    "employee": {"rag", "workflow", "validation"},
    "hr": {"rag", "workflow", "validation", "security", "analytics"},
    "admin": {"rag", "workflow", "validation", "security", "analytics"},
}


def can_use_agent(role: str, agent_type: str) -> bool:
    return agent_type in ROLE_AGENT_PERMISSIONS.get(role, set())
