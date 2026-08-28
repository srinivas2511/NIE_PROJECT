from app.agents.base import BaseAgent


class AnalyticsAgent(BaseAgent):
    agent_type = "analytics"

    def run(self, description: str, prior_results: list[str], role: str) -> str:
        return (
            f"[Analytics] Would analyze enterprise data and produce a report for: "
            f"'{description}'. (Analytics pipeline not yet implemented.)"
        )
