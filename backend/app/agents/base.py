from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """Common interface every specialized agent implements.

    Real agent logic lands with later FRs (FR-3 RAG, FR-6 XAI, FR-7 HITL);
    for FR-2 most of these are still deterministic stubs so the
    orchestrator's decomposition/routing/aggregation can be built and
    tested now. `role` is the requesting user's role -- most agents
    ignore it (the orchestrator already gates *whether* an agent runs
    at all per FR-4); RAGAgent uses it to gate *which documents* it may
    ground on.
    """

    agent_type: str

    @abstractmethod
    def run(self, description: str, prior_results: list[str], role: str) -> str:
        """Execute the subtask and return a human-readable result string."""
        raise NotImplementedError
