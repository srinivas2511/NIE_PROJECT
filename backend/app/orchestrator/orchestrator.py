from sqlalchemy.orm import Session

from app.agents.base import AgentResult
from app.agents.registry import get_agent
from app.audit.logger import log_event
from app.hitl.gate import requires_approval
from app.models.enterprise_request import EnterpriseRequest
from app.models.sub_task import SubTask
from app.orchestrator.decomposer import decompose
from app.rbac.roles import can_use_agent
from app.rbac.zero_trust import verify_continuous_access

DENIAL_CONFIDENCE = 1.0
DENIAL_EXPLANATION = "This is a certain policy match (access-control decision), not a hedge."


def compute_request_status(subtasks: list[SubTask]) -> str:
    """Priority: failed > pending_approval > partially_denied (covers both
    automated 'denied' and human 'rejected' subtasks) > completed."""
    statuses = {s.status for s in subtasks}
    if "failed" in statuses:
        return "failed"
    if "pending_approval" in statuses:
        return "pending_approval"
    if "denied" in statuses or "rejected" in statuses:
        return "partially_denied"
    return "completed"


def run_orchestration(request: EnterpriseRequest, db: Session) -> EnterpriseRequest:
    """Decompose the request into subtasks, assign each to its agent, run them,
    and persist the results. Runs synchronously -- agents are stubs for now.
    """
    plans = decompose(request.text)

    subtasks = [
        SubTask(request_id=request.id, agent_type=plan.agent_type, description=plan.description)
        for plan in plans
    ]
    db.add_all(subtasks)
    db.commit()
    for subtask in subtasks:
        db.refresh(subtask)

    prior_results: list[AgentResult] = []
    for subtask in subtasks:
        agent_result: AgentResult | None = None

        # Zero-Trust (FR-5): re-verify identity/authorization fresh immediately
        # before this subtask, rather than reusing a role captured once for
        # the whole request -- covers both this inter-agent dispatch and (for
        # the rag agent) the data-access it's about to perform.
        verification = verify_continuous_access(request.user_id, db)
        if not verification.verified:
            subtask.status = "denied"
            subtask.result = f"Zero-Trust verification failed: {verification.reason}."
            subtask.confidence = DENIAL_CONFIDENCE
            subtask.explanation = DENIAL_EXPLANATION
            audit_action = "zero_trust.deny"
        else:
            role = verification.role
            if not can_use_agent(role, subtask.agent_type):
                subtask.status = "denied"
                subtask.result = (
                    f"Access denied: role '{role}' is not permitted to use the "
                    f"'{subtask.agent_type}' agent. Contact an administrator if you believe "
                    "this is incorrect."
                )
                subtask.confidence = DENIAL_CONFIDENCE
                subtask.explanation = DENIAL_EXPLANATION
                audit_action = "rbac.deny"
            else:
                try:
                    agent = get_agent(subtask.agent_type)
                    agent_result = agent.run(subtask.description, prior_results, role)
                    subtask.result = agent_result.text
                    subtask.confidence = agent_result.confidence

                    # HITL (FR-7): sensitive or below-threshold decisions don't
                    # auto-complete -- they wait for a human approver
                    # (app/api/routes/approvals.py) instead of being trusted
                    # as a finished result.
                    flagged, reason = requires_approval(
                        subtask.agent_type, agent_result.confidence, agent_result.sensitive
                    )
                    if flagged:
                        subtask.status = "pending_approval"
                        subtask.explanation = (
                            f"{agent_result.explanation} [Flagged for human review: {reason}.]"
                        )
                    else:
                        subtask.status = "completed"
                        subtask.explanation = agent_result.explanation
                        prior_results.append(agent_result)
                    audit_action = f"{subtask.agent_type}.run"
                except Exception as exc:  # noqa: BLE001 -- isolate one agent's failure
                    subtask.status = "failed"
                    subtask.result = f"Agent error: {exc}"
                    subtask.confidence = None
                    subtask.explanation = (
                        "This subtask failed with an unexpected error; no confidence applies."
                    )
                    audit_action = f"{subtask.agent_type}.error"

        # FR-8: log every agent action, whatever the outcome -- including
        # denials, where no agent ever ran.
        log_event(
            db,
            event_type="agent_action",
            action=audit_action,
            user_id=request.user_id,
            role=verification.role,
            request_id=request.id,
            subtask_id=subtask.id,
            context={
                "agent_type": subtask.agent_type,
                "status": subtask.status,
                "confidence": subtask.confidence,
            },
        )

        # FR-8: data access -- the rag agent actually queried the vector store
        # whenever it ran, regardless of whether the answer was granted,
        # access-denied, or later flagged for approval.
        if subtask.agent_type == "rag" and agent_result is not None:
            log_event(
                db,
                event_type="data_access",
                action="rag.retrieve",
                user_id=request.user_id,
                role=verification.role,
                request_id=request.id,
                subtask_id=subtask.id,
                context={"sources": agent_result.sources, "sensitive": agent_result.sensitive},
            )

    request.status = compute_request_status(subtasks)
    db.commit()
    db.refresh(request)
    return request
