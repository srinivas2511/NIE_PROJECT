from app.agents.base import AgentResult, BaseAgent

STUB_CONFIDENCE = 0.4


class SecurityAgent(BaseAgent):
    agent_type = "security"

    def run(self, description: str, prior_results: list[AgentResult], role: str) -> AgentResult:
        text = (
            f"Access and permissions check for role '{role}': your identity and permissions "
            "were freshly re-checked against current records immediately before this step ran -- "
            "not reused from login or from earlier steps. If either check fails, this subtask "
            "is marked as denied above."
        )
        return AgentResult(
            text=text,
            confidence=STUB_CONFIDENCE,
            explanation="This is a simulated security check for demonstration, not a full "
            "analysis -- confidence is kept low so it isn't mistaken for a verified finding.",
        )
