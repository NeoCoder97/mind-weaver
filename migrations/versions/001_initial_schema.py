"""Initial schema: create all tables

This migration creates the complete MindWeaver database schema including:
- feeds: RSS/Atom feed subscriptions
- entries: Feed articles/posts
- categories: Feed categorization
- filter_rules: Content filtering rules
- feed_categories: Many-to-many relationship between feeds and categories

Migration ID: 001
Created: 2026-02-02 21:00:00+08:00

IMPORTANT NOTES:
- This is the initial schema creation for fresh installations
- For existing databases, use 'alembic stamp head' instead
- Use 'alembic upgrade head' to apply this migration

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Apply schema changes to upgrade database.

    Creates all tables for the MindWeaver application.
    """
    # Create categories table
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('icon', sa.String(length=50), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index('ix_categories_id', 'categories', ['id'], unique=False)

    # Create feeds table
    op.create_table(
        'feeds',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('url', sa.String(length=2048), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=True),
        sa.Column('fetch_interval_minutes', sa.Integer(), nullable=True),
        sa.Column('max_entries_per_fetch', sa.Integer(), nullable=True),
        sa.Column('fetch_only_recent', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('last_fetched_at', sa.DateTime(), nullable=True),
        sa.Column('etag', sa.String(length=255), nullable=True),
        sa.Column('last_modified', sa.String(length=255), nullable=True),
        sa.Column('fetch_error_count', sa.Integer(), nullable=True),
        sa.Column('last_error', sa.Text(), nullable=True),
        sa.Column('last_error_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('url')
    )
    op.create_index('ix_feeds_id', 'feeds', ['id'], unique=False)

    # Create entries table
    op.create_table(
        'entries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('feed_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('link', sa.String(length=2048), nullable=False),
        sa.Column('author', sa.String(length=255), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('fetched_at', sa.DateTime(), nullable=True),
        sa.Column('title_hash', sa.String(length=64), nullable=True),
        sa.Column('link_hash', sa.String(length=64), nullable=True),
        sa.Column('content_hash', sa.String(length=64), nullable=True),
        sa.Column('tags', sa.Text(), nullable=True),
        sa.Column('language', sa.String(length=10), nullable=True),
        sa.Column('reading_time_seconds', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['feed_id'], ['feeds.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('link_hash')
    )
    op.create_index('ix_entries_feed_fetched', 'entries', ['feed_id', 'fetched_at'], unique=False)
    op.create_index('ix_entries_feed_id', 'entries', ['feed_id'], unique=False)
    op.create_index('ix_entries_feed_published', 'entries', ['feed_id', 'published_at'], unique=False)
    op.create_index('ix_entries_id', 'entries', ['id'], unique=False)
    op.create_index('ix_entries_link_hash', 'entries', ['link_hash'], unique=False)
    op.create_index('ix_entries_title_hash', 'entries', ['title_hash'], unique=False)

    # Create filter_rules table
    op.create_table(
        'filter_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=True),
        sa.Column('rule_type', sa.String(length=20), nullable=True),
        sa.Column('match_type', sa.String(length=10), nullable=True),
        sa.Column('pattern', sa.Text(), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index('ix_filter_rules_enabled_priority', 'filter_rules', ['enabled', 'priority'], unique=False)
    op.create_index('ix_filter_rules_id', 'filter_rules', ['id'], unique=False)

    # Create feed_categories junction table (many-to-many relationship)
    op.create_table(
        'feed_categories',
        sa.Column('feed_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
        sa.ForeignKeyConstraint(['feed_id'], ['feeds.id'], ),
        sa.PrimaryKeyConstraint('feed_id', 'category_id')
    )


def downgrade() -> None:
    """Revert schema changes to downgrade database.

    Drops all tables in reverse order of creation.
    """
    op.drop_table('feed_categories')
    op.drop_table('filter_rules')
    op.drop_table('entries')
    op.drop_table('feeds')
    op.drop_table('categories')
