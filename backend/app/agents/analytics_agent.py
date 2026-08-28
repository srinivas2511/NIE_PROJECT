from app.agents.base import AgentResult, BaseAgent

STUB_CONFIDENCE = 0.4


class AnalyticsAgent(BaseAgent):
    agent_type = "analytics"

    def run(self, description: str, prior_results: list[AgentResult], role: str) -> AgentResult:
        text = (
            f"[Analytics] Would analyze enterprise data and produce a report for: "
            f"'{description}'. (Analytics pipeline not yet implemented.)"
        )
        return AgentResult(
            text=text,
            confidence=STUB_CONFIDENCE,
            explanation="This agent is still a placeholder (no real data analysis run) -- "
            "confidence is fixed low to avoid overstating certainty for unimplemented analysis.",
        )
