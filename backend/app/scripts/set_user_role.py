"""Dev/demo bootstrap for assigning roles to users.

Full role administration through a UI is FR-11's job. Until that exists,
this is how an hr/admin test account gets created for FR-4 (registration
always assigns "employee" -- self-service signup can never self-elevate).

Usage:
    python -m app.scripts.set_user_role <email> <role>
"""

import sys

from app.core.database import SessionLocal
from app.models.user import User
from app.rbac.roles import VALID_ROLES


def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: python -m app.scripts.set_user_role <email> <role>")
        print(f"Valid roles: {', '.join(sorted(VALID_ROLES))}")
        sys.exit(1)

    email, role = sys.argv[1], sys.argv[2]
    if role not in VALID_ROLES:
        print(f"Invalid role '{role}'. Valid roles: {', '.join(sorted(VALID_ROLES))}")
        sys.exit(1)

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            print(f"No user found with email '{email}'")
            sys.exit(1)
        user.role = role
        db.commit()
        print(f"Updated {email} -> role '{role}'")
    finally:
        db.close()


if __name__ == "__main__":
    main()
