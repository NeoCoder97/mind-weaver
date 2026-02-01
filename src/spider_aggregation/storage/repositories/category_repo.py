"""
Category repository for database operations.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Select, asc, desc
from sqlalchemy.orm import Session

from spider_aggregation.models import CategoryModel
from spider_aggregation.models.category import CategoryCreate, CategoryUpdate
from spider_aggregation.models.feed import FeedModel


class CategoryRepository:
    """Repository for Category CRUD operations."""

    def __init__(self, session: Session) -> None:
        """Initialize repository with a database session.

        Args:
            session: SQLAlchemy Session instance
        """
        self.session = session

    def create(
        self,
        name: str,
        description: Optional[str] = None,
        color: Optional[str] = None,
        icon: Optional[str] = None,
        enabled: bool = True,
    ) -> CategoryModel:
        """Create a new category.

        Args:
            name: Category name (must be unique)
            description: Optional description
            color: Optional hex color code (e.g., #ff5733)
            icon: Optional icon name or class
            enabled: Whether the category is enabled (default: True)

        Returns:
            Created CategoryModel instance
        """
        category = CategoryModel(
            name=name,
            description=description,
            color=color,
            icon=icon,
            enabled=enabled,
        )

        self.session.add(category)
        self.session.flush()
        self.session.refresh(category)
        return category

    def get_by_id(self, category_id: int) -> Optional[CategoryModel]:
        """Get a category by ID.

        Args:
            category_id: Category ID

        Returns:
            CategoryModel instance or None
        """
        return (
            self.session.query(CategoryModel)
            .filter(CategoryModel.id == category_id)
            .first()
        )

    def get_by_name(self, name: str) -> Optional[CategoryModel]:
        """Get a category by name.

        Args:
            name: Category name

        Returns:
            CategoryModel instance or None
        """
        return (
            self.session.query(CategoryModel).filter(CategoryModel.name == name).first()
        )

    def list(
        self, enabled_only: bool = False, limit: int = 1000, offset: int = 0
    ) -> list[CategoryModel]:
        """List categories with optional filtering.

        Args:
            enabled_only: Only return enabled categories
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of CategoryModel instances
        """
        query = self.session.query(CategoryModel)

        if enabled_only:
            query = query.filter(CategoryModel.enabled == True)

        return query.order_by(CategoryModel.name).limit(limit).offset(offset).all()

    def update(self, category: CategoryModel, **kwargs) -> CategoryModel:
        """Update a category.

        Args:
            category: CategoryModel instance to update
            **kwargs: Fields to update (name, description, color, icon, enabled)

        Returns:
            Updated CategoryModel instance
        """
        for key, value in kwargs.items():
            if hasattr(category, key):
                setattr(category, key, value)

        self.session.flush()
        self.session.refresh(category)
        return category

    def delete(self, category: CategoryModel) -> None:
        """Delete a category.

        Args:
            category: CategoryModel instance to delete
        """
        self.session.delete(category)
        self.session.flush()

    def add_feed_to_category(
        self, feed: FeedModel, category: CategoryModel
    ) -> None:
        """Add a feed to a category.

        Args:
            feed: FeedModel instance
            category: CategoryModel instance
        """
        if category not in feed.categories:
            feed.categories.append(category)
            self.session.flush()

    def remove_feed_from_category(
        self, feed: FeedModel, category: CategoryModel
    ) -> None:
        """Remove a feed from a category.

        Args:
            feed: FeedModel instance
            category: CategoryModel instance
        """
        if category in feed.categories:
            feed.categories.remove(category)
            self.session.flush()

    def get_feeds_by_category(
        self,
        category_id: int,
        enabled_only: bool = False,
        limit: int = 1000,
        offset: int = 0,
    ) -> list[FeedModel]:
        """Get all feeds in a category.

        Args:
            category_id: Category ID
            enabled_only: Only return enabled feeds
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of FeedModel instances
        """
        query = (
            self.session.query(FeedModel)
            .join(FeedModel.categories)
            .filter(CategoryModel.id == category_id)
        )

        if enabled_only:
            query = query.filter(FeedModel.enabled == True)

        return query.order_by(desc(FeedModel.created_at)).limit(limit).offset(offset).all()

    def get_feed_count_by_category(self, category_id: int, enabled_only: bool = False) -> int:
        """Count feeds in a category.

        Args:
            category_id: Category ID
            enabled_only: Only count enabled feeds

        Returns:
            Number of feeds in the category
        """
        query = (
            self.session.query(FeedModel)
            .join(FeedModel.categories)
            .filter(CategoryModel.id == category_id)
        )

        if enabled_only:
            query = query.filter(FeedModel.enabled == True)

        return query.count()

    def set_categories_for_feed(
        self, feed: FeedModel, category_ids: list[int]
    ) -> FeedModel:
        """Set categories for a feed (replaces existing categories).

        Args:
            feed: FeedModel instance
            category_ids: List of category IDs

        Returns:
            Updated FeedModel instance
        """
        # Fetch all category objects
        categories = (
            self.session.query(CategoryModel)
            .filter(CategoryModel.id.in_(category_ids))
            .all()
        )

        # Replace existing categories
        feed.categories = categories
        feed.updated_at = datetime.utcnow()
        self.session.flush()
        self.session.refresh(feed)
        return feed

    def count(self, enabled_only: bool = False) -> int:
        """Count categories.

        Args:
            enabled_only: Only count enabled categories

        Returns:
            Number of categories
        """
        query = self.session.query(CategoryModel)

        if enabled_only:
            query = query.filter(CategoryModel.enabled == True)

        return query.count()
