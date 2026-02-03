# Alembic Database Migration Guide

## Quick Reference

| Command | Description |
|---------|-------------|
| `alembic current` | Show current migration version |
| `alembic history` | Show migration history |
| `alembic upgrade head` | Apply all pending migrations |
| `alembic downgrade -1` | Rollback last migration |
| `alembic downgrade base` | Rollback all migrations |
| `alembic revision -m "description"` | Create new empty migration |
| `alembic revision --autogenerate -m "desc"` | Auto-generate migration from models |
| `alembic stamp head` | Mark database as current without running migrations |

## Initial Setup

### For Fresh Installation

```bash
# Apply all migrations to create database schema
alembic upgrade head
```

### For Existing Database (Already Has Tables)

```bash
# Mark current database state without running migrations
alembic stamp head

# Verify current version
alembic current
```

## Daily Workflow

### 1. Modify SQLAlchemy Models

Edit files in `src/spider_aggregation/models/`:

```python
# src/spider_aggregation/models/feed.py
class FeedModel(Base):
    # ... existing fields ...
    favicon_url = Column(String(2048))  # New field
```

### 2. Generate Migration

```bash
# Auto-generate migration script
alembic revision --autogenerate -m "add feed favicon URL"

# Or create empty migration for complex changes
alembic revision -m "migrate user data"
```

### 3. Review Generated Migration

```bash
# View the generated file
cat migrations/versions/2026_02_02_XXXX_XXX_add_feed_favicon_url.py
```

**Important:** Always review auto-generated migrations before applying!

### 4. Test Migration

```bash
# Apply migration
alembic upgrade head

# Verify changes in database
sqlite3 data/spider_aggregation.db ".schema feeds"

# Rollback if needed
alembic downgrade -1
```

### 5. Commit Changes

```bash
git add migrations/versions/2026_02_02_XXXX_XXX_add_feed_favicon_url.py
git commit -m "feat: add feed favicon URL field"
```

## Common Scenarios

### Adding a New Column

```python
# Model change
class FeedModel(Base):
    favicon_url = Column(String(2048), nullable=True)
```

```bash
alembic revision --autogenerate -m "add feed favicon"
```

### Creating a New Table

```python
# New model
class UserFavorite(Base):
    __tablename__ = "user_favorites"
    id = Column(Integer, primary_key=True)
    entry_id = Column(Integer, ForeignKey("entries.id"))
```

```bash
alembic revision --autogenerate -m "add user favorites table"
```

### Renaming a Column

```python
# In migration script (manual)
def upgrade():
    op.alter_column('feeds', 'name', new_column_name='display_name')

def downgrade():
    op.alter_column('feeds', 'display_name', new_column_name='name')
```

### Data Migration

```python
def upgrade():
    # Step 1: Add new column
    op.add_column('feeds', sa.Column('summary', sa.Text(), nullable=True))

    # Step 2: Migrate data
    connection = op.get_bind()
    results = connection.execute('SELECT id, description FROM feeds')
    for row in results:
        feed_id, description = row
        if description and len(description) > 100:
            summary = description[:100] + '...'
            connection.execute(
                'UPDATE feeds SET summary = ? WHERE id = ?',
                summary, feed_id
            )

def downgrade():
    op.drop_column('feeds', 'summary')
```

## Production Deployment

### Pre-Deployment Checklist

- [ ] Test migration on staging database
- [ ] Backup production database
- [ ] Review rollback plan
- [ ] Estimate migration time for large tables

### Deployment Script

```bash
#!/bin/bash
# deploy.sh

# 1. Backup database
cp data/spider_aggregation.db backups/spider_aggregation_$(date +%Y%m%d_%H%M%S).db

# 2. Pull latest code
git pull origin main

# 3. Apply migrations
alembic upgrade head

# 4. Verify migration
alembic current

# 5. Restart application
systemctl restart mind-weaver

# 6. Health check
curl -f http://localhost:8000/health || exit 1
```

### Rollback Procedure

```bash
# Rollback last migration
alembic downgrade -1

# Restore from backup if needed
cp backups/spider_aggregation_YYYYMMDD_HHMMSS.db data/spider_aggregation.db

# Restart application
systemctl restart mind-weaver
```

## Troubleshooting

### Migration Conflicts

```bash
# If two developers create migrations with the same down_revision
alembic merge -m "merge conflicting migrations" head1 head2

# Then continue
alembic upgrade head
```

### Database Out of Sync

```bash
# If database is behind migrations
alembic upgrade head

# If database is ahead of migrations (development only)
alembic stamp head

# To reset completely (DANGEROUS - deletes data)
rm data/spider_aggregation.db
alembic upgrade head
```

### SQLite Limitations

SQLite has limited ALTER TABLE support. Alembic uses "batch mode" to work around this:

```python
# Automatic in migrations (render_as_batch=True in env.py)
with op.batch_alter_table('feeds') as batch_op:
    batch_op.add_column(sa.Column('new_field', sa.String()))
    batch_op.drop_column('old_field')
```

## Migration Best Practices

### DO

- ✅ Always test migrations on a copy of production data
- ✅ Review auto-generated migrations before applying
- ✅ Write descriptive migration messages
- ✅ Include data migrations when changing schema
- ✅ Use transactions for atomic operations
- ✅ Document breaking changes in commit messages

### DON'T

- ❌ Don't modify committed migrations (create new ones instead)
- ❌ Don't hard-code IDs or data in migrations
- ❌ Don't use ORM models in migrations (use raw SQL or op.execute())
- ❌ Don't ignore warnings in auto-generated migrations
- ❌ Don't run destructive migrations without backups

## File Structure

```
migrations/
├── versions/
│   ├── 001_initial_schema.py           # Create all tables
│   ├── 002_add_feed_indexes.py         # Performance improvements
│   └── 003_add_categories_table.py     # Phase 3 feature
├── env.py                              # Environment configuration
├── script.py.mako                      # Migration file template
└── README                              # This file
```

## Further Reading

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLite ALTER TABLE Limitations](https://www.sqlite.org/lang_altertable.html)
- [SQLAlchemy Migration Patterns](https://alembic.sqlalchemy.org/en/latest/cookbook.html)
