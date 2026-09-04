from app.agents.base import AgentResult, BaseAgent

STUB_CONFIDENCE = 0.4


class AnalyticsAgent(BaseAgent):
    agent_type = "analytics"

    def run(self, description: str, prior_results: list[AgentResult], role: str) -> AgentResult:
        text = (
            f"This is a simulated analytics response for: '{description}'. A full analytics "
            "pipeline is not yet available."
        )
        return AgentResult(
            text=text,
            confidence=STUB_CONFIDENCE,
            explanation="This is a simulated analysis for demonstration, not a full analytics "
            "pipeline -- confidence is kept low so it isn't mistaken for a verified finding.",
        )
