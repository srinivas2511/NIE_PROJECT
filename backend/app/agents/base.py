from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class AgentResult:
    """FR-6 (XAI): every agent decision carries a confidence score and an
    explanation of how that confidence was derived, alongside its text."""

    text: str
    confidence: float
    explanation: str


class BaseAgent(ABC):
    """Common interface every specialized agent implements.

    Real agent logic lands with later FRs (FR-3 RAG done; FR-7 HITL next);
    security/analytics/workflow are still deterministic stubs so the
    orchestrator's decomposition/routing/aggregation can be built and
    tested now -- their confidence reflects that honestly (fixed, low).
    `role` is the requesting user's role -- most agents ignore it (the
    orchestrator already gates *whether* an agent runs at all per FR-4);
    RAGAgent uses it to gate *which documents* it may ground on.
    """

    agent_type: str

    @abstractmethod
    def run(self, description: str, prior_results: list[AgentResult], role: str) -> AgentResult:
        """Execute the subtask and return its result, confidence, and explanation."""
        raise NotImplementedError
