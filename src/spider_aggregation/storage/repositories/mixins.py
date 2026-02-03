"""
Repository mixins for common query patterns.

This module provides mixin classes that encapsulate common query patterns
shared across multiple repositories.
"""

from typing import TypeVar, Generic, Optional, List

from sqlalchemy import desc

ModelType = TypeVar("ModelType")


class CategoryQueryMixin(Generic[ModelType]):
    """Mixin for category-based queries.

    This mixin provides common methods for querying records by category
    relationships. It's designed to work with models that have a many-to-many
    relationship with categories via the feed_categories junction table.

    The mixin is generic and can work with different model types (FeedModel,
    EntryModel, etc.) that participate in category relationships.
    """

    def _query_by_category(
        self,
        category_id: int,
        enabled_only: bool = False,
    ):
        """Build base query for category filtering.

        This protected method builds the base query for filtering by category.
        It should be used as a starting point for more specific queries.

        Args:
            category_id: Category ID to filter by
            enabled_only: Only return enabled records

        Returns:
            SQLAlchemy query object
        """
        from spider_aggregation.models import feed_categories

        query = (
            self.session.query(self.model)
            .join(feed_categories, self.model.id == feed_categories.c.feed_id)
            .filter(feed_categories.c.category_id == category_id)
        )

        if enabled_only and hasattr(self.model, "enabled"):
            query = query.filter(self.model.enabled == True)

        return query

    def get_by_category(
        self,
        category_id: int,
        enabled_only: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> List[ModelType]:
        """Get records by category ID.

        Args:
            category_id: Category ID
            enabled_only: Only return enabled records
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of model instances
        """
        return (
            self._query_by_category(category_id, enabled_only)
            .order_by(desc(self.model.created_at))
            .limit(limit)
            .offset(offset)
            .all()
        )

    def get_by_category_name(
        self,
        category_name: str,
        enabled_only: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> List[ModelType]:
        """Get records by category name.

        Args:
            category_name: Category name
            enabled_only: Only return enabled records
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of model instances
        """
        from spider_aggregation.models import CategoryModel, feed_categories

        query = (
            self.session.query(self.model)
            .join(feed_categories, self.model.id == feed_categories.c.feed_id)
            .join(CategoryModel)
            .filter(CategoryModel.name == category_name)
        )

        if enabled_only and hasattr(self.model, "enabled"):
            query = query.filter(self.model.enabled == True)

        return query.order_by(desc(self.model.created_at)).limit(limit).offset(offset).all()

    def get_by_categories(
        self,
        category_ids: List[int],
        enabled_only: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> List[ModelType]:
        """Get records by multiple category IDs (records in any of the categories).

        Args:
            category_ids: List of category IDs
            enabled_only: Only return enabled records
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of model instances
        """
        from spider_aggregation.models import feed_categories

        if not category_ids:
            return []

        query = (
            self.session.query(self.model)
            .join(feed_categories, self.model.id == feed_categories.c.feed_id)
            .filter(feed_categories.c.category_id.in_(category_ids))
        )

        if enabled_only and hasattr(self.model, "enabled"):
            query = query.filter(self.model.enabled == True)

        return query.order_by(desc(self.model.created_at)).limit(limit).offset(offset).all()

    def count_by_category(self, category_id: int, enabled_only: bool = False) -> int:
        """Count records by category ID.

        Args:
            category_id: Category ID
            enabled_only: Only count enabled records

        Returns:
            Number of records in the category
        """
        return self._query_by_category(category_id, enabled_only).count()
