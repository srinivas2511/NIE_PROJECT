"""Dev/demo bootstrap for activating/deactivating users.

Mirrors set_user_role.py. Used to demonstrate FR-5 Zero-Trust
verification: a deactivated account is cut off immediately, even with
an already-issued, unexpired token -- see app/rbac/zero_trust.py.

Usage:
    python -m app.scripts.set_user_active <email> <true|false>
"""

import sys

from app.core.database import SessionLocal
from app.models.user import User


def main() -> None:
    if len(sys.argv) != 3 or sys.argv[2].lower() not in ("true", "false"):
        print("Usage: python -m app.scripts.set_user_active <email> <true|false>")
        sys.exit(1)

    email = sys.argv[1]
    is_active = sys.argv[2].lower() == "true"

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            print(f"No user found with email '{email}'")
            sys.exit(1)
        user.is_active = is_active
        db.commit()
        print(f"Updated {email} -> is_active={is_active}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
