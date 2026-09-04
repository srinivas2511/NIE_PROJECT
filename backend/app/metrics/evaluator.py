from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.enterprise_request import EnterpriseRequest
from app.models.sub_task import SubTask
from app.models.workflow_execution import WorkflowExecution


def _avg(values: list[float]) -> float | None:
    values = [v for v in values if v is not None]
    return sum(values) / len(values) if values else None


def compute_accuracy_metrics(db: Session) -> dict:
    """FR-12: 'response accuracy'. No labeled ground-truth dataset exists, so
    this reports confidence-based proxies (field names say what they are),
    not a fabricated verified-correctness score."""
    subtasks = db.query(SubTask).all()
    total = len(subtasks)
    failed = [s for s in subtasks if s.status == "failed"]

    confidences_by_agent: dict[str, list[float]] = {}
    for s in subtasks:
        if s.confidence is not None:
            confidences_by_agent.setdefault(s.agent_type, []).append(s.confidence)

    rag_subtasks = [
        s for s in subtasks if s.agent_type == "rag" and s.status in ("completed", "pending_approval")
    ]
    rag_grounded = [s for s in rag_subtasks if s.result and "Sources:" in s.result]

    return {
        "total_subtasks": total,
        "failed_subtask_rate": len(failed) / total if total else None,
        "avg_confidence_overall": _avg([s.confidence for s in subtasks]),
        "avg_confidence_by_agent": {
            agent: _avg(vals) for agent, vals in confidences_by_agent.items()
        },
        "rag_grounded_rate": len(rag_grounded) / len(rag_subtasks) if rag_subtasks else None,
    }


def compute_timing_metrics(db: Session) -> dict:
    """FR-12/NFR-5: 'workflow completion time' -- end-to-end request latency,
    workflow-specific step-count context (FR-9), and a per-agent-type
    breakdown (NFR-5) that localizes *which* agent is slow, since the
    end-to-end number alone can't."""
    requests = (
        db.query(EnterpriseRequest).filter(EnterpriseRequest.completed_at.isnot(None)).all()
    )
    durations = [(r.completed_at - r.created_at).total_seconds() for r in requests]

    step_counts = (
        db.query(WorkflowExecution.subtask_id, func.count(WorkflowExecution.id))
        .group_by(WorkflowExecution.subtask_id)
        .all()
    )

    subtask_durations_by_agent: dict[str, list[float]] = {}
    for agent_type, duration_ms in db.query(SubTask.agent_type, SubTask.duration_ms).filter(
        SubTask.duration_ms.isnot(None)
    ):
        subtask_durations_by_agent.setdefault(agent_type, []).append(duration_ms / 1000)

    return {
        "requests_measured": len(durations),
        "avg_request_completion_seconds": _avg(durations),
        "avg_workflow_steps_per_subtask": _avg([count for _, count in step_counts]),
        "avg_subtask_duration_seconds_by_agent": {
            agent: _avg(vals) for agent, vals in subtask_durations_by_agent.items()
        },
    }


def compute_security_metrics(db: Session) -> dict:
    """FR-12: 'security-relevant metrics', drawn from the FR-8 audit log."""
    rbac_denials = db.query(AuditLog).filter(AuditLog.action == "rbac.deny").count()
    zero_trust_denials = db.query(AuditLog).filter(AuditLog.action == "zero_trust.deny").count()
    total_subtasks = db.query(SubTask).count()
    subtasks_with_log = (
        db.query(AuditLog.subtask_id)
        .filter(AuditLog.event_type == "agent_action", AuditLog.subtask_id.isnot(None))
        .distinct()
        .count()
    )

    return {
        "rbac_denials": rbac_denials,
        "zero_trust_denials": zero_trust_denials,
        "unauthorized_attempts_blocked": rbac_denials + zero_trust_denials,
        "total_audit_log_entries": db.query(AuditLog).count(),
        "audit_log_subtask_coverage": (
            subtasks_with_log / total_subtasks if total_subtasks else None
        ),
    }


def compute_hitl_metrics(db: Session) -> dict:
    """§11 bonus: HITL effectiveness -- cheap given approved_by/approved_at (FR-7)."""
    resolved = db.query(SubTask).filter(SubTask.approved_by.isnot(None)).all()
    turnaround = [
        (s.approved_at - s.created_at).total_seconds() for s in resolved if s.approved_at
    ]
    currently_pending = db.query(SubTask).filter(SubTask.status == "pending_approval").count()

    return {
        "currently_pending": currently_pending,
        "resolved_total": len(resolved),
        "approved": len([s for s in resolved if s.status == "completed"]),
        "rejected": len([s for s in resolved if s.status == "rejected"]),
        "avg_approval_turnaround_seconds": _avg(turnaround),
    }


def compute_explainability_metrics(db: Session) -> dict:
    """§11 bonus: explanation/confidence coverage -- expected near-100% given
    how thoroughly FR-6 wired this."""
    total = db.query(SubTask).count()
    with_explanation = db.query(SubTask).filter(SubTask.explanation.isnot(None)).count()
    with_confidence = db.query(SubTask).filter(SubTask.confidence.isnot(None)).count()

    return {
        "explanation_coverage_rate": with_explanation / total if total else None,
        "confidence_coverage_rate": with_confidence / total if total else None,
    }


def compute_metrics(db: Session) -> dict:
    return {
        "accuracy": compute_accuracy_metrics(db),
        "timing": compute_timing_metrics(db),
        "security": compute_security_metrics(db),
        "hitl": compute_hitl_metrics(db),
        "explainability": compute_explainability_metrics(db),
    }
