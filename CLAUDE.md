# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Spider Aggregation is a personal knowledge/research dynamic monitoring tool that automatically fetches, deduplicates, stores, and retrieves RSS/Atom feed content. Built with Python 3.14+, Flask, SQLite, and SQLAlchemy.

**Current Status:** Phase 2 complete (Web interface, content extraction, keyword extraction, filtering). Phase 3-4 planned.

## Common Commands

### Running the Application
```bash
# Start web application (primary interface)
uv run spider-aggregation

# With custom host/port
export SPIDER_WEB_HOST=0.0.0.0
export SPIDER_WEB_PORT=8000
uv run spider-aggregation
```

### Development
```bash
# Install dependencies
uv sync

# Install dev dependencies
uv sync --dev

# Run tests
uv run pytest                      # All tests
uv run pytest tests/unit/          # Unit tests only
uv run pytest tests/integration/   # Integration tests only

# Code quality
uv run black src/ tests/           # Format code
uv run ruff check src/ tests/      # Lint
uv run ruff check --fix src/ tests/

# Coverage
uv run pytest --cov=src/spider_aggregation --cov-report=html
```

### Utility Scripts
```bash
python scripts/init_db.py              # Initialize database
python scripts/seed_feeds.py           # Seed sample feeds
python scripts/migrate_phase2.py       # Phase 2 database migration
python scripts/test_real_feed.py       # Test real feed fetching
```

## Architecture

The codebase follows a layered architecture with clear separation of concerns:

```
Web Layer (Flask + Jinja2)
    ↓
Core Logic Layer (fetcher, parser, deduplicator, scheduler, filter_engine, keyword_extractor, content_fetcher, summarizer)
    ↓
Data Access Layer (Repository Pattern: FeedRepository, EntryRepository, FilterRuleRepository)
    ↓
Storage Layer (SQLite + SQLAlchemy ORM)
```

### Key Modules

**Core Layer (`src/spider_aggregation/core/`):**
- `fetcher.py` - RSS/Atom feed fetching with ETag/304 support
- `parser.py` - Content normalization, HTML cleaning, language detection, date parsing
- `deduplicator.py` - Multi-strategy deduplication (strict/medium/relaxed)
- `scheduler.py` - APScheduler-based task scheduling with thread pool
- `content_fetcher.py` - Full article content extraction (Trafilatura)
- `filter_engine.py` - Rule-based filtering (keyword/regex/tag/language)
- `keyword_extractor.py` - NLP-based keyword extraction (NLTK/jieba)
- `summarizer.py` - Extractive and AI-based summarization

**Storage Layer (`src/spider_aggregation/storage/`):**
- `database.py` - DatabaseManager for SQLAlchemy session management
- `repositories/feed_repo.py` - Feed CRUD operations
- `repositories/entry_repo.py` - Entry CRUD operations with search/filter
- `repositories/filter_rule_repo.py` - Filter rule management

**Web Layer (`src/spider_aggregation/web/`):**
- `app.py` - Flask application with REST API endpoints
- `__main__.py` - Entry point for `spider-aggregation` command
- `templates/` - Jinja2 HTML templates (dashboard, feeds, entries, filter_rules, settings)

### Data Flow

```
Scheduler triggers → Fetcher.fetch_feed() → Parser.parse_entry()
→ Deduplicator.check_duplicate() → FilterEngine.apply()
→ ContentFetcher/KeywordExtractor/Summarizer (Phase 2 features)
→ Repository.create() → Database
```

## Configuration

Configuration priority: Environment variables (`SPIDER_*`) > `config/config.yaml` > defaults.

Key environment variables:
- `SPIDER_WEB_HOST` - Web server host (default: 127.0.0.1)
- `SPIDER_WEB_PORT` - Web server port (default: 8000)
- `SPIDER_DB_PATH` - Database file path (default: data/spider_aggregation.db)

## Code Standards

- **Style:** PEP 8, enforced by Black (line-length: 100) and Ruff
- **Type annotations:** Required for public APIs
- **Docstrings:** Google-style docstrings
- **Naming:** snake_case for modules/functions, PascalCase for classes
- **Commit conventions:** Conventional Commits (feat:, fix:, docs:, test:, refactor:, chore:)

## Testing

- Unit tests in `tests/unit/` - test individual modules with mocks
- Integration tests in `tests/integration/` - test with real RSS feeds
- Fixtures in `tests/conftest.py` - db_manager, db_session, feed
- Mock external HTTP requests in unit tests
- Use `@pytest.mark.integration` and `@pytest.mark.slow` for test organization

## Database Models

**Feeds table:** URL, name, description, enabled, interval, ETag, errors
**Entries table:** title, link, content, hashes (title_hash, link_hash, content_hash), tags, language, reading_time
**Filter_rules table:** keyword/regex/tag/language filtering rules

## Design Patterns

- Repository pattern for data access (DAO layer)
- Factory functions (`create_fetcher()`, `create_parser()`, etc.)
- Dependency injection (session injection for repositories)
- Strategy pattern for deduplication strategies
- Data classes for result objects

## Important Notes

- **Primary interface:** Web-only (Flask-based) as of v0.3.0
- **ETag support:** Feeds support conditional requests with 304 Not Modified
- **Deduplication:** Three strategies - strict, medium (default), relaxed
- **Error handling:** 10 consecutive failures auto-disable feeds
- **Concurrency:** Default 3 worker threads for scheduler (configurable)
- **Content length:** Default max 10,000 characters for summary, 500,000 for full content
