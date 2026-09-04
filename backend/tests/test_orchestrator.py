from types import SimpleNamespace

from app.orchestrator.orchestrator import compute_request_status


def _subtasks(*statuses):
    return [SimpleNamespace(status=s) for s in statuses]


def test_failed_takes_priority_over_everything():
    status = compute_request_status(_subtasks("completed", "pending_approval", "failed"))
    assert status == "failed"


def test_pending_approval_takes_priority_over_denied_and_completed():
    status = compute_request_status(_subtasks("completed", "denied", "pending_approval"))
    assert status == "pending_approval"


def test_denied_or_rejected_maps_to_partially_denied():
    assert compute_request_status(_subtasks("completed", "denied")) == "partially_denied"
    assert compute_request_status(_subtasks("completed", "rejected")) == "partially_denied"


def test_all_completed_is_completed():
    assert compute_request_status(_subtasks("completed", "completed")) == "completed"
