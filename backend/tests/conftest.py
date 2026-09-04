import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models import *  # noqa: F401,F403 -- register every model with Base before create_all


@pytest.fixture()
def db_session():
    """In-memory SQLite session -- no Docker/Postgres needed to run tests
    (NFR-9: independent testing). Fresh schema per test, discarded after."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()
