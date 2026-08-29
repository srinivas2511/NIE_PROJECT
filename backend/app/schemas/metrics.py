from pydantic import BaseModel


class AccuracyMetrics(BaseModel):
    total_subtasks: int
    failed_subtask_rate: float | None
    avg_confidence_overall: float | None
    avg_confidence_by_agent: dict[str, float | None]
    rag_grounded_rate: float | None


class TimingMetrics(BaseModel):
    requests_measured: int
    avg_request_completion_seconds: float | None
    avg_workflow_steps_per_subtask: float | None


class SecurityMetrics(BaseModel):
    rbac_denials: int
    zero_trust_denials: int
    unauthorized_attempts_blocked: int
    total_audit_log_entries: int
    audit_log_subtask_coverage: float | None


class HitlMetrics(BaseModel):
    currently_pending: int
    resolved_total: int
    approved: int
    rejected: int
    avg_approval_turnaround_seconds: float | None


class ExplainabilityMetrics(BaseModel):
    explanation_coverage_rate: float | None
    confidence_coverage_rate: float | None


class EvaluationReport(BaseModel):
    accuracy: AccuracyMetrics
    timing: TimingMetrics
    security: SecurityMetrics
    hitl: HitlMetrics
    explainability: ExplainabilityMetrics
