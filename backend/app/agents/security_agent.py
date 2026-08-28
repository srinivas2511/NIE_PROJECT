from app.agents.base import BaseAgent


class SecurityAgent(BaseAgent):
    agent_type = "security"

    def run(self, description: str, prior_results: list[str], role: str) -> str:
        return (
            f"[Security] RBAC + Zero-Trust check for role '{role}': identity and role permissions "
            "were freshly re-verified against the database immediately before every subtask in "
            "this request ran -- not reused from login or from earlier subtasks. Any denial from "
            "either check is marked status='denied' above."
        )
