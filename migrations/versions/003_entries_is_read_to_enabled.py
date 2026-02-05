"""Replace entries.is_read with entries.enabled

- Add column enabled (Boolean, default True)
- If is_read exists: set enabled = NOT is_read, then drop is_read
- Create index on enabled

Migration ID: 003
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "003"
down_revision: Union[str, Sequence[str], None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    cols = [c["name"] for c in insp.get_columns("entries")]

    # Add enabled column if not present (idempotent for partial re-runs)
    if "enabled" not in cols:
        op.add_column(
            "entries",
            sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        )
        cols.append("enabled")

    if "is_read" in cols:
        # Migrate: enabled = NOT is_read
        dialect_name = conn.dialect.name
        if dialect_name == "sqlite":
            conn.execute(
                sa.text(
                    "UPDATE entries SET enabled = CASE WHEN is_read = 1 THEN 0 ELSE 1 END"
                )
            )
        else:
            conn.execute(sa.text("UPDATE entries SET enabled = NOT is_read"))
        # Drop index on is_read first (SQLite requires this before dropping the column)
        index_names = [idx["name"] for idx in insp.get_indexes("entries")]
        if "ix_entries_is_read" in index_names:
            op.drop_index("ix_entries_is_read", table_name="entries")
        op.drop_column("entries", "is_read")

    # Create index on enabled if not present
    insp = sa.inspect(conn)
    index_names = [idx["name"] for idx in insp.get_indexes("entries")]
    if "ix_entries_enabled" not in index_names:
        op.create_index(
            "ix_entries_enabled", "entries", ["enabled"], unique=False
        )


def downgrade() -> None:
    op.drop_index("ix_entries_enabled", table_name="entries")

    # Restore is_read: add column, migrate enabled -> is_read, drop enabled
    op.add_column(
        "entries",
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    conn = op.get_bind()
    dialect_name = conn.dialect.name
    if dialect_name == "sqlite":
        conn.execute(
            sa.text(
                "UPDATE entries SET is_read = CASE WHEN enabled = 1 THEN 0 ELSE 1 END"
            )
        )
    else:
        conn.execute(sa.text("UPDATE entries SET is_read = NOT enabled"))
    op.drop_column("entries", "enabled")
