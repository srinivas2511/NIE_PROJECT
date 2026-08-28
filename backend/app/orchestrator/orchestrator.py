from sqlalchemy.orm import Session

from app.agents.registry import get_agent
from app.models.enterprise_request import EnterpriseRequest
from app.models.sub_task import SubTask
from app.orchestrator.decomposer import decompose
from app.rbac.roles import can_use_agent


def run_orchestration(request: EnterpriseRequest, db: Session) -> EnterpriseRequest:
    """Decompose the request into subtasks, assign each to its agent, run them,
    and persist the results. Runs synchronously -- agents are stubs for now.
    """
    plans = decompose(request.text)
    role = request.user.role

    subtasks = [
        SubTask(request_id=request.id, agent_type=plan.agent_type, description=plan.description)
        for plan in plans
    ]
    db.add_all(subtasks)
    db.commit()
    for subtask in subtasks:
        db.refresh(subtask)

    prior_results: list[str] = []
    any_failed = False
    any_denied = False
    for subtask in subtasks:
        if not can_use_agent(role, subtask.agent_type):
            subtask.status = "denied"
            subtask.result = (
                f"Access denied: role '{role}' is not permitted to use the "
                f"'{subtask.agent_type}' agent. Contact an administrator if you believe this "
                "is incorrect."
            )
            any_denied = True
            continue

        try:
            agent = get_agent(subtask.agent_type)
            result = agent.run(subtask.description, prior_results, role)
            subtask.status = "completed"
            subtask.result = result
            prior_results.append(result)
        except Exception as exc:  # noqa: BLE001 -- isolate one agent's failure from the rest
            subtask.status = "failed"
            subtask.result = f"Agent error: {exc}"
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
