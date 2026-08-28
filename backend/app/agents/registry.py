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
