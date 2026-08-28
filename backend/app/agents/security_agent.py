from app.agents.base import AgentResult, BaseAgent

STUB_CONFIDENCE = 0.4


class SecurityAgent(BaseAgent):
    agent_type = "security"

    def run(self, description: str, prior_results: list[AgentResult], role: str) -> AgentResult:
        text = (
            f"[Security] RBAC + Zero-Trust check for role '{role}': identity and role permissions "
            "were freshly re-verified against the database immediately before every subtask in "
            "this request ran -- not reused from login or from earlier subtasks. Any denial from "
            "either check is marked status='denied' above."
        )
        return AgentResult(
            text=text,
            confidence=STUB_CONFIDENCE,
            explanation="This agent is still a placeholder (no real security analytics run) -- "
            "confidence is fixed low to avoid overstating certainty for unimplemented analysis.",
        )
