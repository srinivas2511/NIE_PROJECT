from app.agents.base import AgentResult, BaseAgent

NEUTRAL_CONFIDENCE = 0.5


class ValidationAgent(BaseAgent):
    agent_type = "validation"

    def run(self, description: str, prior_results: list[AgentResult], role: str) -> AgentResult:
        if not prior_results:
            return AgentResult(
                text="[Validation] No prior subtask results to review.",
                confidence=NEUTRAL_CONFIDENCE,
                explanation="No subtasks completed before validation ran, so there is nothing "
                "to aggregate a confidence score from; 0.5 is a neutral default.",
            )

        confidences = [r.confidence for r in prior_results]
        avg_confidence = sum(confidences) / len(confidences)
        breakdown = ", ".join(f"{c:.0%}" for c in confidences)

        text = (
            f"[Validation] Reviewed {len(prior_results)} subtask result(s); "
            f"aggregate confidence {avg_confidence:.0%}. No inconsistencies detected. "
            "(Stub — real correctness/consistency checks and HITL flagging land with FR-7.)"
        )
        explanation = (
            f"Aggregated as the mean of this request's prior subtask confidences "
            f"({breakdown}); a low aggregate here is the signal FR-7's HITL gate will act on."
        )
        return AgentResult(text=text, confidence=avg_confidence, explanation=explanation)
