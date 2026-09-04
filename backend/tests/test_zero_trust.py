from app.core.security import hash_password
from app.models.user import User
from app.rbac.zero_trust import verify_continuous_access


def test_unknown_user_id_fails_verification(db_session):
    result = verify_continuous_access(user_id=999, db=db_session)
    assert result.verified is False
    assert result.role is None
    assert "no longer exists" in result.reason


def test_deactivated_user_fails_verification(db_session):
    user = User(
        email="deactivated@example.com",
        hashed_password=hash_password("supersecret1"),
        full_name="Deactivated User",
        role="employee",
        is_active=False,
    )
    db_session.add(user)
    db_session.commit()

    result = verify_continuous_access(user_id=user.id, db=db_session)
    assert result.verified is False
    assert result.role == "employee"
    assert "deactivated" in result.reason


def test_active_user_passes_verification(db_session):
    user = User(
        email="active@example.com",
        hashed_password=hash_password("supersecret1"),
        full_name="Active User",
        role="hr",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()

    result = verify_continuous_access(user_id=user.id, db=db_session)
    assert result.verified is True
    assert result.role == "hr"
    assert result.reason is None
