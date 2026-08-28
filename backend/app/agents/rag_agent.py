from app.agents.base import AgentResult, BaseAgent
from app.rag.pipeline import answer_with_rag


class RAGAgent(BaseAgent):
    agent_type = "rag"

    def run(self, description: str, prior_results: list[AgentResult], role: str) -> AgentResult:
        try:
            result = answer_with_rag(description, role)
        except Exception as exc:  # noqa: BLE001 -- surface a clear inline error, don't crash
            return AgentResult(
                text=f"[RAG] Could not generate a grounded answer: {exc}",
                confidence=0.0,
                explanation="The RAG pipeline (retrieval or LLM call) failed, so no grounded "
                "answer could be produced.",
            )

        text = f"[RAG] {result.answer}"
        if result.sources:
            text += f"\n\nSources: {', '.join(result.sources)}"

        return AgentResult(text=text, confidence=result.confidence, explanation=result.explanation)
