"""${message}

This migration manages database schema changes for MindWeaver.

Migration ID: ${up_revision}
Created: ${create_date}

IMPORTANT NOTES:
- Always test migrations on a copy of production data first
- Use 'alembic upgrade head' to apply this migration
- Use 'alembic downgrade -1' to rollback this migration
- For SQLite, ALTER TABLE operations are handled as batch operations

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}


# revision identifiers, used by Alembic.
revision: str = ${repr(up_revision)}
down_revision: Union[str, Sequence[str], None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    """Apply schema changes to upgrade database.

    This function should contain all the changes needed to move from
    the previous schema version to this one.
    """
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    """Revert schema changes to downgrade database.

    This function should reverse all changes made in upgrade().
    It should restore the database to the state it was in before
    this migration was applied.
    """
    ${downgrades if downgrades else "pass"}
