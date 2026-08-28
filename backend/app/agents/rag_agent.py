from app.agents.base import BaseAgent


class RAGAgent(BaseAgent):
    agent_type = "rag"

    def run(self, description: str, prior_results: list[str]) -> str:
        return (
            f"[RAG] Would retrieve relevant enterprise documents for: '{description}'. "
            "(RAG pipeline not yet implemented — see FR-3.)"
        )
