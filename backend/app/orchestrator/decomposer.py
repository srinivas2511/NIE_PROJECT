from dataclasses import dataclass

# Rule-based keyword routing. No LLM/API key dependency yet -- swap in a
# real LLM-based planner once FR-3's RAG/LLM layer exists.
AGENT_KEYWORDS: dict[str, list[str]] = {
    "security": ["access", "permission", "role", "authoriz", "security", "who can"],
    "analytics": ["report", "analy", "data", "metric", "trend", "statistic", "dashboard", "summar"],
    "rag": ["policy", "document", "knowledge", "find", "lookup", "what is", "explain", "search"],
    "workflow": ["create", "update", "schedule", "approve", "submit", "process", "automate", "task"],
}

FALLBACK_AGENT_TYPE = "workflow"
VALIDATION_AGENT_TYPE = "validation"


@dataclass
class SubTaskPlan:
    agent_type: str
    description: str


def decompose(text: str) -> list[SubTaskPlan]:
    """Route a request's text to one or more specialized agents by keyword.

    Every request always yields at least one content subtask (falling back
    to `workflow` when nothing matches) plus a trailing `validation`
    subtask that reviews the others' results.
    """
    lowered = text.lower()
    matched_types = [
        agent_type
        for agent_type, keywords in AGENT_KEYWORDS.items()
        if any(keyword in lowered for keyword in keywords)
    ]

    if not matched_types:
        matched_types = [FALLBACK_AGENT_TYPE]

    plans = [SubTaskPlan(agent_type=agent_type, description=text) for agent_type in matched_types]
    plans.append(SubTaskPlan(agent_type=VALIDATION_AGENT_TYPE, description=text))
    return plans
