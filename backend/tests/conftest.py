import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import NullPool

from app.config import settings
from app.db.session import get_db
from app.main import app


@pytest.fixture(scope="session")
def engine():
    """
    One engine for the whole test session.
    NullPool: don't cache connections between tests — the DB stays clean.
    """
    eng = create_engine(settings.database_url, poolclass=NullPool)
    yield eng
    eng.dispose()


@pytest.fixture
def db(engine):
    """
    Each test gets its own connection + transaction.
    Endpoint's commit() becomes a savepoint release, not a real commit.
    At teardown, we rollback — nothing persists.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(db):
    """
    FastAPI TestClient with get_db overridden to hand out our test session.
    Guarantees every request in a test sees the same transaction.
    """
    def _get_db_override():
        yield db

    app.dependency_overrides[get_db] = _get_db_override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()