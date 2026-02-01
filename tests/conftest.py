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


@pytest.fixture
def client():
    """Create a Flask test client with in-memory database."""
    from spider_aggregation.web.app import create_app
    from spider_aggregation.storage.database import DatabaseManager

    # Use a file-based database instead of in-memory for better test isolation
    # This allows the Flask app and test code to share the same database
    import tempfile
    import os

    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    try:
        # Create app with test database
        app = create_app(db_path=db_path, debug=True)

        # Initialize database
        db_manager = DatabaseManager(db_path)
        db_manager.init_db()

        yield app.test_client()

    finally:
        # Cleanup
        try:
            os.unlink(db_path)
        except OSError:
            pass

