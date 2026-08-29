from dataclasses import dataclass, field

from app.rag.llm import generate
from app.rag.pipeline import answer_with_rag

BASELINE_PROMPT_TEMPLATE = (
    "Answer this question directly and concisely, based on your own knowledge.\n\n"
    "QUESTION:\n{question}\n\nANSWER:"
)


@dataclass
class EvalCase:
    question: str
    # Any one match (case-insensitive substring) counts as correct.
    expected_keywords: list[str]


# Each fact below is an invented, company-specific number pulled directly from
# the seed documents' actual text (app/rag/documents/) -- verified against the
# files, not guessed. No real-world LLM could know these without retrieval,
# which is what makes correctness on them a clean proxy for grounding rather
# than the model's general knowledge (NFR-2).
EVAL_CASES: list[EvalCase] = [
    EvalCase(
        "How many days per week can employees work remotely under our policy?",
        ["three", "3"],
    ),
    EvalCase(
        "What is the minimum number of characters required in a password under "
        "our IT security policy?",
        ["12", "twelve"],
    ),
    EvalCase(
        "How many business days in advance must a PTO request be submitted?",
        ["5", "five"],
    ),
    EvalCase(
        "What is the maximum number of PTO days that can be carried over into "
        "the next calendar year?",
        ["10", "ten"],
    ),
    EvalCase(
        "What is the daily meal allowance while traveling for business?",
        ["75", "$75"],
    ),
    EvalCase(
        "How many months of base salary severance do VPs receive if terminated "
        "without cause?",
        ["6", "six"],
    ),
]


@dataclass
class EvalCaseResult:
    question: str
    expected_keywords: list[str]
    baseline_answer: str
    baseline_correct: bool
    grounded_answer: str
    grounded_correct: bool
    grounded_sources: list[str]


@dataclass
class EvaluationReport:
    cases: list[EvalCaseResult] = field(default_factory=list)
    baseline_accuracy: float = 0.0
    grounded_accuracy: float = 0.0


def _contains_keyword(text: str, keywords: list[str]) -> bool:
    lowered = text.lower()
    return any(keyword.lower() in lowered for keyword in keywords)


def run_case(case: EvalCase, role: str) -> EvalCaseResult:
    baseline_answer = generate(BASELINE_PROMPT_TEMPLATE.format(question=case.question))
    grounded = answer_with_rag(case.question, role)

    return EvalCaseResult(
        question=case.question,
        expected_keywords=case.expected_keywords,
        baseline_answer=baseline_answer,
        baseline_correct=_contains_keyword(baseline_answer, case.expected_keywords),
        grounded_answer=grounded.answer,
        grounded_correct=_contains_keyword(grounded.answer, case.expected_keywords),
        grounded_sources=grounded.sources,
    )


def run_evaluation(role: str = "admin") -> EvaluationReport:
    """NFR-2: run every case through both an ungrounded ('single-agent
    baseline') LLM call and the real RAG pipeline, and measure the accuracy
    gap. role="admin" by default so every seed doc (including the admin-only
    one) is reachable, same as any other case."""
    results = [run_case(case, role) for case in EVAL_CASES]
    total = len(results)
    return EvaluationReport(
        cases=results,
        baseline_accuracy=sum(r.baseline_correct for r in results) / total if total else 0.0,
        grounded_accuracy=sum(r.grounded_correct for r in results) / total if total else 0.0,
    )
