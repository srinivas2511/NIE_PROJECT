from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.models.role_permission import RolePermission
from app.rbac.roles import can_use_agent, get_agent_types, require_admin


def test_can_use_agent_true_when_permission_row_exists(db_session):
    db_session.add(RolePermission(role="employee", agent_type="rag"))
    db_session.commit()

    assert can_use_agent("employee", "rag", db_session) is True


def test_can_use_agent_false_when_no_permission_row(db_session):
    assert can_use_agent("employee", "security", db_session) is False


def test_get_agent_types_matches_registry():
    types = get_agent_types()
    assert types == {"rag", "security", "analytics", "workflow", "validation"}


def test_require_admin_allows_admin():
    require_admin(SimpleNamespace(role="admin"))  # must not raise


def test_require_admin_rejects_non_admin():
    with pytest.raises(HTTPException) as exc_info:
        require_admin(SimpleNamespace(role="employee"))
    assert exc_info.value.status_code == 403


def test_require_admin_uses_custom_detail_message():
    with pytest.raises(HTTPException) as exc_info:
        require_admin(SimpleNamespace(role="hr"), "Only admins may review pending approvals.")
    assert exc_info.value.detail == "Only admins may review pending approvals."
