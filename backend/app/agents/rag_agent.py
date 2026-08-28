from app.agents.base import BaseAgent
from app.rag.pipeline import answer_with_rag


class RAGAgent(BaseAgent):
    agent_type = "rag"

    def run(self, description: str, prior_results: list[str], role: str) -> str:
        try:
            result = answer_with_rag(description, role)
        except Exception as exc:  # noqa: BLE001 -- surface a clear inline error, don't crash
            return f"[RAG] Could not generate a grounded answer: {exc}"

        if not result.sources:
            return f"[RAG] {result.answer}"

        return f"[RAG] {result.answer}\n\nSources: {', '.join(result.sources)}"
