from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """Common interface every specialized agent implements.

    Real agent logic lands with later FRs (FR-3 RAG, FR-4/5 Security,
    FR-6 XAI, FR-7 HITL); for FR-2 these are deterministic stubs so the
    orchestrator's decomposition/routing/aggregation can be built and
    tested now.
    """

    agent_type: str

    @abstractmethod
    def run(self, description: str, prior_results: list[str]) -> str:
        """Execute the subtask and return a human-readable result string."""
        raise NotImplementedError
