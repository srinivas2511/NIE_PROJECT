from app.agents.base import AgentResult, BaseAgent

STUB_CONFIDENCE = 0.4


class WorkflowAgent(BaseAgent):
    agent_type = "workflow"

    def run(self, description: str, prior_results: list[AgentResult], role: str) -> AgentResult:
        text = (
            f"[Workflow] Would execute the multi-step task automation for: '{description}'. "
            "(Task automation not yet implemented — see FR-9.)"
        )
        return AgentResult(
            text=text,
            confidence=STUB_CONFIDENCE,
            explanation="This agent is still a placeholder (no real task automation run) -- "
            "confidence is fixed low to avoid overstating certainty for unimplemented analysis.",
        )
