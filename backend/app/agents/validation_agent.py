from app.agents.base import BaseAgent


class ValidationAgent(BaseAgent):
    agent_type = "validation"

    def run(self, description: str, prior_results: list[str], role: str) -> str:
        if not prior_results:
            return (
                "[Validation] No prior subtask results to review. "
                "(Real correctness/consistency checks land with FR-6/FR-7.)"
            )
        return (
            f"[Validation] Reviewed {len(prior_results)} subtask result(s); "
            "no inconsistencies detected. "
            "(Stub — real confidence scoring and HITL flagging land with FR-6/FR-7.)"
        )
