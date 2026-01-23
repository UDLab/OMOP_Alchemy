import pytest
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, Session
from pathlib import Path
from omop_alchemy import get_engine_name, load_environment
from orm_loader.helpers import bootstrap


@pytest.fixture(scope="session")
def engine():
    """
    Session-scoped engine pointing at the test database.

    Created once per test run.
    """
    test_file = Path(__file__).parent / "fixtures" / "test.db"
    test_engine = f"sqlite:///{test_file}"
    engine = sa.create_engine(
        test_engine,
        future=True,
        echo=False,
    )

    bootstrap(engine, create=False)
    
    return engine


@pytest.fixture(scope="function")
def session(engine) -> Session: # type: ignore
    """
    Function-scoped SQLAlchemy session.

    Each test gets a clean transactional boundary.
    """
    SessionLocal = sessionmaker(
        bind=engine,
        future=True,
        expire_on_commit=False,
    )

    session = SessionLocal()

    try:
        yield session       # type: ignore
        session.rollback()  # safety: undo mutations
    finally:
        session.close()
