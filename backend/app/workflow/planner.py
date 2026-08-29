from dataclasses import dataclass

# Rule-based routing to one or more simulated functions -- same approach as
# app/orchestrator/decomposer.py, no LLM dependency. Order matters: a
# request matching multiple categories runs as a sensible pipeline
# (gather data -> report on it -> mark status), which is what makes
# "multi-step" concrete and demonstrable.
STEP_KEYWORDS: dict[str, list[str]] = {
    "retrieve_data": ["data", "retrieve", "look up", "headcount", "expense"],
    "generate_report": ["report", "generate"],
    "update_status": ["status", "update"],
}

FALLBACK_FUNCTION = "generate_report"


@dataclass
class WorkflowStepPlan:
    function_name: str


def plan_steps(description: str) -> list[WorkflowStepPlan]:
    lowered = description.lower()
    steps = [
        WorkflowStepPlan(function_name=name)
        for name, keywords in STEP_KEYWORDS.items()
        if any(keyword in lowered for keyword in keywords)
    ]
    if not steps:
        steps = [WorkflowStepPlan(function_name=FALLBACK_FUNCTION)]
    return steps
