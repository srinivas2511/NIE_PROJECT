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


@dataclass
class RAGResult:
    answer: str
    sources: list[str]
    access_denied: bool = False


def answer_with_rag(query_text: str, role: str, n_results: int = 3) -> RAGResult:
    chunks = query(query_text, n_results=n_results)

    if not chunks:
        return RAGResult(
            answer="No relevant enterprise documents were found for this question.",
            sources=[],
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
            access_denied=True,
        )

    allowed_chunks = [c for c in chunks if role in c.allowed_roles]
    context = "\n\n---\n\n".join(f"[{chunk.source}]\n{chunk.text}" for chunk in allowed_chunks)
    prompt = GROUNDING_PROMPT_TEMPLATE.format(context=context, question=query_text)
    answer = generate(prompt)

    sources = list(dict.fromkeys(chunk.source for chunk in allowed_chunks))
    return RAGResult(answer=answer, sources=sources)
