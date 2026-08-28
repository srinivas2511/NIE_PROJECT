from dataclasses import dataclass

from app.rag.llm import generate
from app.rag.vector_store import query

GROUNDING_PROMPT_TEMPLATE = """You are an enterprise assistant. Answer the question using ONLY the \
context below. If the context does not contain the answer, say so -- do not make up information.

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:"""

NO_MATCH_CONFIDENCE = 0.2
ACCESS_DENIED_CONFIDENCE = 1.0


@dataclass
class RAGResult:
    answer: str
    sources: list[str]
    confidence: float
    explanation: str
    access_denied: bool = False


def _distance_to_confidence(distance: float) -> float:
    # Embeddings are normalized (app/rag/embeddings.py), so L2 distance is
    # bounded to [0, 2]; map that to a [0, 1] confidence, closer = higher.
    return max(0.0, min(1.0, 1 - distance / 2))


def answer_with_rag(query_text: str, role: str, n_results: int = 3) -> RAGResult:
    chunks = query(query_text, n_results=n_results)

    if not chunks:
        return RAGResult(
            answer="No relevant enterprise documents were found for this question.",
            sources=[],
            confidence=NO_MATCH_CONFIDENCE,
            explanation="No document chunks matched this question in the vector store, so "
            "there is nothing to ground an answer on.",
        )

    # `chunks` is ordered by relevance (closest match first). Gate on the single best
    # match rather than "every retrieved chunk is denied" -- otherwise a highly relevant
    # restricted document can be silently dropped in favor of barely-relevant public ones,
    # producing a misleading "no information found" instead of an honest access denial.
    top_chunk = chunks[0]
    if role not in top_chunk.allowed_roles:
        return RAGResult(
            answer=(
                f"Access denied: the most relevant document for this question "
                f"({top_chunk.source}) requires a role this account does not have "
                f"(needs: {', '.join(sorted(top_chunk.allowed_roles))})."
            ),
            sources=[],
            confidence=ACCESS_DENIED_CONFIDENCE,
            explanation="This is a deterministic access-control decision based on document "
            "role classification, not a probabilistic judgment about answer quality.",
            access_denied=True,
        )

    allowed_chunks = [c for c in chunks if role in c.allowed_roles]
    context = "\n\n---\n\n".join(f"[{chunk.source}]\n{chunk.text}" for chunk in allowed_chunks)
    prompt = GROUNDING_PROMPT_TEMPLATE.format(context=context, question=query_text)
    answer = generate(prompt)

    sources = list(dict.fromkeys(chunk.source for chunk in allowed_chunks))
    best = allowed_chunks[0]
    confidence = _distance_to_confidence(best.distance)
    explanation = (
        f"Derived from vector-similarity between the question and the closest retrieved "
        f"chunk, from '{best.source}' (distance={best.distance:.3f}); lower distance "
        "yields higher confidence."
    )
    return RAGResult(
        answer=answer, sources=sources, confidence=confidence, explanation=explanation
    )
