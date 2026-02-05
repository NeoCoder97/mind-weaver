#!/usr/bin/env python3
"""
Migration script to add is_read column to entries table.

Run this script to add the is_read field to existing entries.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from spider_aggregation.config import get_config
from spider_aggregation.storage.database import DatabaseManager
from spider_aggregation.logger import get_logger

logger = get_logger(__name__)


def migrate():
    """Add is_read column to entries table."""
    config = get_config()
    db_path = config.database.path

    logger.info(f"Running migration on database: {db_path}")

    db_manager = DatabaseManager(db_path)

    try:
        with db_manager.session() as session:
            # Check if column already exists
            from sqlalchemy import inspect, text
            inspector = inspect(session.bind)
            columns = [col['name'] for col in inspector.get_columns('entries')]

            if 'is_read' in columns:
                logger.info("Column 'is_read' already exists in entries table")
                return

            # Add the column using raw SQL
            session.execute(text("ALTER TABLE entries ADD COLUMN is_read BOOLEAN NOT NULL DEFAULT 0"))
            session.commit()

            logger.info("Successfully added 'is_read' column to entries table")

            # Create index on is_read
            session.execute(text("CREATE INDEX IF NOT EXISTS ix_entries_is_read ON entries(is_read)"))
            session.commit()

            logger.info("Successfully created index on 'is_read' column")

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise


if __name__ == "__main__":
    migrate()
    print("Migration completed successfully!")
