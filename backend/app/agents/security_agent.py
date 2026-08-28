from app.agents.base import BaseAgent


class SecurityAgent(BaseAgent):
    agent_type = "security"

    def run(self, description: str, prior_results: list[str]) -> str:
        return (
            f"[Security] Would verify RBAC/Zero-Trust permissions for: '{description}'. "
            "(RBAC/Zero-Trust enforcement not yet implemented — see FR-4/FR-5.)"
        )
