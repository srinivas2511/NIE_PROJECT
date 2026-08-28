from app.agents.base import BaseAgent


class SecurityAgent(BaseAgent):
    agent_type = "security"

    def run(self, description: str, prior_results: list[str], role: str) -> str:
        return (
            f"[Security] RBAC check for role '{role}': agent permissions for this request were "
            "already enforced during orchestration -- any denied subtask is marked "
            "status='denied' above. Continuous Zero-Trust verification per request/session is "
            "not yet implemented — see FR-5."
        )
