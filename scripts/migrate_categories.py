#!/usr/bin/env python3
"""
Migration script for adding categories feature.

This script adds the categories and feed_categories tables to support
organizing feeds into categories.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy import inspect
from spider_aggregation.storage.database import DatabaseManager
from spider_aggregation.logger import get_logger

logger = get_logger(__name__)


def check_has_categories(db_path: str) -> bool:
    """Check if categories table exists.

    Args:
        db_path: Path to the database file

    Returns:
        True if categories table exists
    """
    manager = DatabaseManager(db_path)

    with manager.session() as session:
        inspector = inspect(session.connection())
        tables = inspector.get_table_names()
        return "categories" in tables


def migrate_categories(db_path: str) -> bool:
    """Migrate database to add categories support.

    Args:
        db_path: Path to the database file

    Returns:
        True if migration successful
    """
    logger.info(f"Migrating database at {db_path} to add categories...")

    if check_has_categories(db_path):
        logger.info("Categories table already exists")
        return True

    manager = DatabaseManager(db_path)

    try:
        from spider_aggregation.models.category import CategoryModel
        from spider_aggregation.models.feed import feed_categories

        logger.info("Creating categories and feed_categories tables...")
        CategoryModel.metadata.create_all(
            manager.engine,
            tables=[CategoryModel.__table__, feed_categories],
        )

        logger.info("Categories migration completed successfully")
        return True

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def rollback_categories(db_path: str) -> bool:
    """Rollback categories feature by dropping the tables.

    Args:
        db_path: Path to the database file

    Returns:
        True if rollback successful
    """
    logger.info(f"Rolling back categories at {db_path}...")

    if not check_has_categories(db_path):
        logger.info("Categories table does not exist, nothing to rollback")
        return True

    manager = DatabaseManager(db_path)

    try:
        with manager.session() as session:
            # Drop junction table first (due to foreign key constraints)
            logger.info("Dropping feed_categories table...")
            session.execute("DROP TABLE IF EXISTS feed_categories")

            # Then drop categories table
            logger.info("Dropping categories table...")
            session.execute("DROP TABLE IF EXISTS categories")

        logger.info("Categories rollback completed successfully")
        return True

    except Exception as e:
        logger.error(f"Rollback failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def seed_default_categories(db_path: str) -> bool:
    """Seed default categories.

    Args:
        db_path: Path to the database file

    Returns:
        True if seeding successful
    """
    logger.info(f"Seeding default categories at {db_path}...")

    if not check_has_categories(db_path):
        logger.error("Categories table does not exist, run migration first")
        return False

    manager = DatabaseManager(db_path)

    # Default categories with colors and icons
    default_categories = [
        {
            "name": "技术博客",
            "description": "技术文章和博客",
            "color": "#3b82f6",
            "icon": "blog",
        },
        {
            "name": "新闻资讯",
            "description": "新闻和资讯内容",
            "color": "#ef4444",
            "icon": "news",
        },
        {
            "name": "开发工具",
            "description": "开发工具和库",
            "color": "#10b981",
            "icon": "tools",
        },
        {
            "name": "Python",
            "description": "Python 相关内容",
            "color": "#3776ab",
            "icon": "python",
        },
        {
            "name": "AI/ML",
            "description": "AI 和机器学习",
            "color": "#8b5cf6",
            "icon": "psychology",
        },
        {
            "name": "娱乐",
            "description": "娱乐内容",
            "color": "#f59e0b",
            "icon": "sports_esports",
        },
        {
            "name": "其他",
            "description": "其他内容",
            "color": "#6b7280",
            "icon": "folder",
        },
    ]

    try:
        with manager.session() as session:
            from spider_aggregation.storage.repositories.category_repo import CategoryRepository

            category_repo = CategoryRepository(session)
            created_count = 0

            for cat_data in default_categories:
                # Check if category already exists
                existing = category_repo.get_by_name(cat_data["name"])
                if existing:
                    logger.info(f"Category '{cat_data['name']}' already exists, skipping")
                    continue

                # Create new category
                category_repo.create(
                    name=cat_data["name"],
                    description=cat_data["description"],
                    color=cat_data["color"],
                    icon=cat_data["icon"],
                )
                created_count += 1
                logger.info(f"Created category: {cat_data['name']}")

        logger.info(f"Seeded {created_count} default categories")
        return True

    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Migrate mind-weaver database for categories feature"
    )
    parser.add_argument(
        "--db-path",
        default="data/spider_aggregation.db",
        help="Path to the database file",
    )
    parser.add_argument(
        "--rollback",
        action="store_true",
        help="Rollback categories feature",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check if categories feature is enabled",
    )
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Seed default categories",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force migration even if categories exist (for development)",
    )

    args = parser.parse_args()

    # Ensure database file exists
    db_file = Path(args.db_path)
    if not db_file.exists():
        logger.error(f"Database not found at {args.db_path}")
        logger.error("Please run 'python scripts/init_db.py' first")
        sys.exit(1)

    if args.check:
        has_categories = check_has_categories(args.db_path)
        if has_categories:
            print("Categories feature is enabled")
            sys.exit(0)
        else:
            print("Categories feature is not enabled")
            sys.exit(1)

    if args.rollback:
        success = rollback_categories(args.db_path)
        sys.exit(0 if success else 1)

    if args.seed:
        success = seed_default_categories(args.db_path)
        sys.exit(0 if success else 1)

    # Migrate (default action)
    success = migrate_categories(args.db_path)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
