from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EvalCaseOut(BaseModel):
    question: str
    expected_keywords: list[str]
    baseline_answer: str
    baseline_correct: bool
    grounded_answer: str
    grounded_correct: bool
    grounded_sources: list[str]


class RagEvaluationRunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    baseline_accuracy: float
    grounded_accuracy: float
    cases: list[EvalCaseOut]
    created_at: datetime
