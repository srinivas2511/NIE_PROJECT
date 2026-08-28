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


def answer_with_rag(query_text: str, n_results: int = 3) -> RAGResult:
    chunks = query(query_text, n_results=n_results)

    if not chunks:
        return RAGResult(
            answer="No relevant enterprise documents were found for this question.",
            sources=[],
        )

    context = "\n\n---\n\n".join(f"[{chunk.source}]\n{chunk.text}" for chunk in chunks)
    prompt = GROUNDING_PROMPT_TEMPLATE.format(context=context, question=query_text)
    answer = generate(prompt)

    sources = list(dict.fromkeys(chunk.source for chunk in chunks))
    return RAGResult(answer=answer, sources=sources)
