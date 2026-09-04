"""NFR-4 (Scalability): adding a new agent type touches only a handful of
small, additive spots -- no orchestrator/API/schema redesign required:

1. Write the agent class (subclass BaseAgent, app/agents/).
2. Register an instance in AGENT_REGISTRY below -- this alone makes it
   invokable and immediately manageable in the FR-11 admin Permissions UI
   (app/rbac/roles.py's get_agent_types() derives from this registry).
3. Add a keyword-routing entry in app/orchestrator/decomposer.py's
   AGENT_KEYWORDS so requests actually reach it.
4. Optionally add it to app/hitl/gate.py's SENSITIVE_AGENT_TYPES if it
   should always require human approval regardless of confidence.

A startup check (app/main.py) validates steps 3-4 reference only agent
types that are actually registered here, catching a typo at deploy time
instead of at first-request time.
"""

from app.agents.analytics_agent import AnalyticsAgent
from app.agents.base import BaseAgent
from app.agents.rag_agent import RAGAgent
from app.agents.security_agent import SecurityAgent
from app.agents.validation_agent import ValidationAgent
from app.agents.workflow_agent import WorkflowAgent

AGENT_REGISTRY: dict[str, BaseAgent] = {
    "rag": RAGAgent(),
    "security": SecurityAgent(),
    "analytics": AnalyticsAgent(),
    "workflow": WorkflowAgent(),
    "validation": ValidationAgent(),
}


def get_agent(agent_type: str) -> BaseAgent:
    try:
        return AGENT_REGISTRY[agent_type]
    except KeyError:
        raise ValueError(f"No agent registered for type: {agent_type!r}") from None


# NFR-7 (Usability): user-facing label for an agent type, mirroring
# frontend/src/utils/labels.js's AGENT_LABELS -- used wherever backend code
# builds a sentence shown directly to a requester (RBAC denials, HITL flag
# reasons) so it doesn't leak the raw internal identifier (e.g. "workflow").
AGENT_LABELS: dict[str, str] = {
    "rag": "Knowledge Base",
    "security": "Security Check",
    "analytics": "Analytics",
    "workflow": "Task Automation",
    "validation": "Validation Review",
}


def humanize_agent_type(agent_type: str) -> str:
    return AGENT_LABELS.get(agent_type, agent_type.replace("_", " "))
