from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def log_event(
    db: Session,
    *,
    event_type: str,
    action: str,
    user_id: int | None = None,
    role: str | None = None,
    request_id: int | None = None,
    subtask_id: int | None = None,
    context: dict | None = None,
) -> AuditLog:
    """FR-8: record an audit entry. Adds to the session without committing --
    it lands atomically in whichever transaction the caller is about to
    commit, so the log write and the state change succeed or fail together."""
    entry = AuditLog(
        event_type=event_type,
        action=action,
        user_id=user_id,
        role=role,
        request_id=request_id,
        subtask_id=subtask_id,
        context=context,
    )
    db.add(entry)
    return entry
