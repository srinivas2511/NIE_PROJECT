from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.audit.logger import log_event
from app.metrics.evaluator import compute_metrics
from app.models.audit_log import AuditLog
from app.models.rag_evaluation_run import RagEvaluationRun
from app.models.role_permission import RolePermission
from app.models.sub_task import SubTask
from app.models.user import User
from app.rag.evaluation import run_evaluation
from app.rbac.roles import VALID_ROLES, get_agent_types
from app.schemas.admin import (
    AuditLogOut,
    PermissionsMatrixOut,
    PermissionToggleRequest,
    UserAdminOut,
    UserUpdateRequest,
)
from app.schemas.metrics import EvaluationReport
from app.schemas.rag_evaluation import RagEvaluationRunOut
from app.schemas.trace import DecisionTraceOut, TraceRequestContext

router = APIRouter(prefix="/api/admin", tags=["admin"])

DEFAULT_AUDIT_LOG_LIMIT = 100
MAX_AUDIT_LOG_LIMIT = 500


def _require_admin(current_user: User) -> None:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only admins may access this."
        )


def _build_matrix(db: Session) -> PermissionsMatrixOut:
    rows = db.query(RolePermission).all()
    matrix: dict[str, list[str]] = {role: [] for role in sorted(VALID_ROLES)}
    for row in rows:
        matrix.setdefault(row.role, []).append(row.agent_type)
    for role in matrix:
        matrix[role].sort()
    return PermissionsMatrixOut(
        roles=sorted(VALID_ROLES), agent_types=sorted(get_agent_types()), matrix=matrix
    )


@router.get("/users", response_model=list[UserAdminOut])
def list_users(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[User]:
    _require_admin(current_user)
    return db.query(User).order_by(User.created_at).all()


@router.patch("/users/{user_id}", response_model=UserAdminOut)
def update_user(
    user_id: int,
    payload: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    _require_admin(current_user)

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user.id == current_user.id and (
        (payload.role is not None and payload.role != "admin")
        or (payload.is_active is not None and not payload.is_active)
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot demote or deactivate your own account.",
        )

    if payload.role is not None:
        if payload.role not in VALID_ROLES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role. Valid roles: {', '.join(sorted(VALID_ROLES))}",
            )
        user.role = payload.role
    if payload.is_active is not None:
        user.is_active = payload.is_active

    log_event(
        db,
        event_type="admin",
        action="admin.user_update",
        user_id=current_user.id,
        role=current_user.role,
        context={
            "target_user_id": user.id,
            "target_email": user.email,
            "new_role": payload.role,
            "new_is_active": payload.is_active,
        },
    )
    db.commit()
    db.refresh(user)
    return user


@router.get("/permissions", response_model=PermissionsMatrixOut)
def get_permissions(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> PermissionsMatrixOut:
    _require_admin(current_user)
    return _build_matrix(db)


@router.post("/permissions/toggle", response_model=PermissionsMatrixOut)
def toggle_permission(
    payload: PermissionToggleRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PermissionsMatrixOut:
    _require_admin(current_user)

    if payload.role not in VALID_ROLES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role.")
    if payload.agent_type not in get_agent_types():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid agent type.")

    existing = (
        db.query(RolePermission)
        .filter(RolePermission.role == payload.role, RolePermission.agent_type == payload.agent_type)
        .first()
    )
    if payload.allowed and existing is None:
        db.add(RolePermission(role=payload.role, agent_type=payload.agent_type))
        log_event(
            db,
            event_type="admin",
            action="admin.permission_grant",
            user_id=current_user.id,
            role=current_user.role,
            context={"role": payload.role, "agent_type": payload.agent_type},
        )
        db.commit()
    elif not payload.allowed and existing is not None:
        db.delete(existing)
        log_event(
            db,
            event_type="admin",
            action="admin.permission_revoke",
            user_id=current_user.id,
            role=current_user.role,
            context={"role": payload.role, "agent_type": payload.agent_type},
        )
        db.commit()

    return _build_matrix(db)


@router.get("/audit-logs", response_model=list[AuditLogOut])
def list_audit_logs(
    event_type: str | None = None,
    user_id: int | None = None,
    limit: int = Query(default=DEFAULT_AUDIT_LOG_LIMIT, le=MAX_AUDIT_LOG_LIMIT, ge=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[AuditLog]:
    _require_admin(current_user)
    query = db.query(AuditLog)
    if event_type:
        query = query.filter(AuditLog.event_type == event_type)
    if user_id is not None:
        query = query.filter(AuditLog.user_id == user_id)
    return query.order_by(AuditLog.created_at.desc()).limit(limit).all()


@router.get("/metrics", response_model=EvaluationReport)
def get_metrics(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> EvaluationReport:
    _require_admin(current_user)
    return EvaluationReport(**compute_metrics(db))


@router.post("/rag-evaluation/run", response_model=RagEvaluationRunOut)
def run_rag_evaluation(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> RagEvaluationRun:
    # NFR-2: admin-triggered on demand, not automatic -- this makes ~12 real
    # LLM calls and realistically takes a couple of minutes.
    _require_admin(current_user)
    report = run_evaluation()
    run = RagEvaluationRun(
        baseline_accuracy=report.baseline_accuracy,
        grounded_accuracy=report.grounded_accuracy,
        cases=[asdict(c) for c in report.cases],
    )
    db.add(run)
    log_event(
        db,
        event_type="admin",
        action="admin.rag_evaluation_run",
        user_id=current_user.id,
        role=current_user.role,
        context={
            "baseline_accuracy": report.baseline_accuracy,
            "grounded_accuracy": report.grounded_accuracy,
        },
    )
    db.commit()
    db.refresh(run)
    return run


@router.get("/rag-evaluation", response_model=RagEvaluationRunOut | None)
def get_latest_rag_evaluation(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> RagEvaluationRun | None:
    _require_admin(current_user)
    return db.query(RagEvaluationRun).order_by(RagEvaluationRun.created_at.desc()).first()


@router.get("/trace/{subtask_id}", response_model=DecisionTraceOut)
def get_decision_trace(
    subtask_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DecisionTraceOut:
    """NFR-3: assemble the full causal trail for one decision -- the subtask's
    own detail, its parent request's context, and every audit log entry tied
    to it, in order -- rather than requiring manual cross-referencing across
    three separate views."""
    _require_admin(current_user)

    subtask = db.query(SubTask).filter(SubTask.id == subtask_id).first()
    if subtask is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subtask not found")

    audit_trail = (
        db.query(AuditLog)
        .filter(AuditLog.subtask_id == subtask_id)
        .order_by(AuditLog.created_at)
        .all()
    )

    return DecisionTraceOut(
        subtask=subtask,
        request=TraceRequestContext(
            id=subtask.request.id,
            text=subtask.request.text,
            requester_email=subtask.request.user.email,
            status=subtask.request.status,
            created_at=subtask.request.created_at,
            completed_at=subtask.request.completed_at,
        ),
        audit_trail=audit_trail,
    )
