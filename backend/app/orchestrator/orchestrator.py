from sqlalchemy.orm import Session

from app.agents.base import AgentResult
from app.agents.registry import get_agent
from app.models.enterprise_request import EnterpriseRequest
from app.models.sub_task import SubTask
from app.orchestrator.decomposer import decompose
from app.rbac.roles import can_use_agent
from app.rbac.zero_trust import verify_continuous_access

DENIAL_CONFIDENCE = 1.0
DENIAL_EXPLANATION = "This is a certain policy match (access-control decision), not a hedge."


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
    any_failed = False
    any_denied = False
    for subtask in subtasks:
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
            any_denied = True
            continue

        role = verification.role
        if not can_use_agent(role, subtask.agent_type):
            subtask.status = "denied"
            subtask.result = (
                f"Access denied: role '{role}' is not permitted to use the "
                f"'{subtask.agent_type}' agent. Contact an administrator if you believe this "
                "is incorrect."
            )
            subtask.confidence = DENIAL_CONFIDENCE
            subtask.explanation = DENIAL_EXPLANATION
            any_denied = True
            continue

        try:
            agent = get_agent(subtask.agent_type)
            agent_result = agent.run(subtask.description, prior_results, role)
            subtask.status = "completed"
            subtask.result = agent_result.text
            subtask.confidence = agent_result.confidence
            subtask.explanation = agent_result.explanation
            prior_results.append(agent_result)
        except Exception as exc:  # noqa: BLE001 -- isolate one agent's failure from the rest
            subtask.status = "failed"
            subtask.result = f"Agent error: {exc}"
            subtask.confidence = None
            subtask.explanation = "This subtask failed with an unexpected error; no confidence applies."
            any_failed = True

    if any_failed:
        request.status = "failed"
    elif any_denied:
        request.status = "partially_denied"
    else:
        request.status = "completed"
    db.commit()
    db.refresh(request)
    return request
