"""Add digest_logs table

This migration adds the digest_logs table for tracking email digest history.

Migration ID: 002
Created: 2026-02-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, Sequence[str], None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Apply schema changes to upgrade database."""
    # Create digest_logs table
    op.create_table(
        'digest_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sent_at', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('entry_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('feed_ids', sa.Text(), nullable=True),
        sa.Column('subject', sa.String(length=500), nullable=False),
        sa.Column('to_addresses', sa.Text(), nullable=False),
        sa.Column('summary_content', sa.Text(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_digest_logs_sent_at', 'digest_logs', ['sent_at'], unique=False)
    op.create_index('ix_digest_logs_status', 'digest_logs', ['status'], unique=False)


def downgrade() -> None:
    """Revert schema changes to downgrade database."""
    op.drop_index('ix_digest_logs_status', table_name='digest_logs')
    op.drop_index('ix_digest_logs_sent_at', table_name='digest_logs')
    op.drop_table('digest_logs')
