from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.user import User


@dataclass
class VerificationResult:
    verified: bool
    role: str | None
    reason: str | None = None


def verify_continuous_access(user_id: int, db: Session) -> VerificationResult:
    """Re-derive identity/authorization fresh from the DB.

    Never trust a role or account-status value captured earlier in the
    request or at login (FR-5) -- call this immediately before every
    inter-agent dispatch and data-access, not once per request.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        return VerificationResult(verified=False, role=None, reason="account no longer exists")
    if not user.is_active:
        return VerificationResult(verified=False, role=user.role, reason="account is deactivated")
    return VerificationResult(verified=True, role=user.role)
