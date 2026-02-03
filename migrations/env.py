"""Alembic migration environment configuration for MindWeaver.

This file is configured to work with MindWeaver's:
- Pydantic-based configuration system
- SQLAlchemy models in src/spider_aggregation/models/
- SQLite database with custom PRAGMA settings
"""

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import MindWeaver configuration and models
from spider_aggregation.config import get_config
from spider_aggregation.models import Base

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Get MindWeaver configuration
mind_config = get_config()

# Set database URL from MindWeaver config
# This ensures migrations use the same database as the application
db_path = mind_config.database.path
if not db_path.startswith("sqlite:///") and not db_path.startswith("sqlite://"):
    db_path = f"sqlite:///{db_path}"

config.set_main_option("sqlalchemy.url", db_path)

# Target metadata for autogenerate support
# This includes all SQLAlchemy models: feeds, entries, categories, filter_rules
target_metadata = Base.metadata

# Additional values from the config
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # SQLite-specific settings
        render_as_batch=True,  # Required for SQLite ALTER TABLE operations
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Create engine configuration
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = db_path

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.StaticPool,  # StaticPool for SQLite
        connect_args={
            "check_same_thread": False,  # Required for SQLite with threading
        },
    )

    # Enable SQLite foreign keys and WAL mode
    # This matches the application's database configuration
    from sqlalchemy import event

    @event.listens_for(connectable, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # SQLite-specific settings
            render_as_batch=True,  # Required for SQLite ALTER TABLE operations
            # Compare type defaults (e.g., server_default values)
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
