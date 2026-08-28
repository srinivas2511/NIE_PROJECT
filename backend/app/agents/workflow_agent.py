from app.agents.base import BaseAgent


class WorkflowAgent(BaseAgent):
    agent_type = "workflow"

    def run(self, description: str, prior_results: list[str]) -> str:
        return (
            f"[Workflow] Would execute the multi-step task automation for: '{description}'. "
            "(Task automation not yet implemented — see FR-9.)"
        )
