"""Shared pytest fixtures for all tests."""

import pytest
from sqlalchemy.orm import Session

from spider_aggregation.storage.database import DatabaseManager


@pytest.fixture
def db_manager():
    """Create a test database manager."""
    manager = DatabaseManager(":memory:")
    manager.init_db()
    yield manager
    manager.close()


@pytest.fixture
def db_session(db_manager: DatabaseManager) -> Session:
    """Create a test database session."""
    with db_manager.session() as session:
        yield session
        # Always rollback to clean up test data
        # This also handles the case where the session is in a pending rollback state
        try:
            session.rollback()
        except Exception:
            pass  # Session may already be closed or in a bad state
