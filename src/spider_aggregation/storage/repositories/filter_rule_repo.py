"""
Filter rule repository for database operations.
"""

from typing import Optional

from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from spider_aggregation.models.filter_rule import FilterRuleModel, FilterRuleCreate, FilterRuleUpdate
from spider_aggregation.storage.repositories.base import BaseRepository


class FilterRuleRepository(BaseRepository[FilterRuleModel, FilterRuleCreate, FilterRuleUpdate]):
    """Repository for FilterRule CRUD operations.

    Inherits common CRUD operations from BaseRepository.
    """

    def __init__(self, session: Session) -> None:
        """Initialize repository with a database session.

        Args:
            session: SQLAlchemy Session instance
        """
        super().__init__(session, FilterRuleModel)

    def get_by_name(self, name: str) -> Optional[FilterRuleModel]:
        """Get a filter rule by name.

        Args:
            name: Filter rule name

        Returns:
            FilterRuleModel instance or None
        """
        return self.session.query(FilterRuleModel).filter(
            FilterRuleModel.name == name
        ).first()

    def list(
        self,
        enabled_only: bool = False,
        rule_type: Optional[str] = None,
        match_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        order_by: str = "priority",
        order_desc: bool = True,
    ) -> list[FilterRuleModel]:
        """List filter rules with optional filtering.

        Args:
            enabled_only: Only return enabled rules
            rule_type: Filter by rule type
            match_type: Filter by match type
            limit: Maximum number of results
            offset: Number of results to skip
            order_by: Field to order by
            order_desc: Sort in descending order

        Returns:
            List of FilterRuleModel instances
        """
        filters = {}
        if enabled_only:
            filters["enabled"] = True

        query = self.session.query(FilterRuleModel)

        # Apply simple filters
        for key, value in filters.items():
            if value is not None and hasattr(FilterRuleModel, key):
                query = query.filter(getattr(FilterRuleModel, key) == value)

        # Apply complex filters
        if rule_type is not None:
            query = query.filter(FilterRuleModel.rule_type == rule_type)

        if match_type is not None:
            query = query.filter(FilterRuleModel.match_type == match_type)

        # Apply ordering
        order_column = getattr(FilterRuleModel, order_by, FilterRuleModel.priority)
        if order_desc:
            query = query.order_by(desc(order_column))
        else:
            query = query.order_by(asc(order_column))

        return query.limit(limit).offset(offset).all()

    def count(
        self,
        enabled_only: bool = False,
        rule_type: Optional[str] = None,
        match_type: Optional[str] = None,
    ) -> int:
        """Count filter rules.

        Args:
            enabled_only: Only count enabled rules
            rule_type: Filter by rule type
            match_type: Filter by match type

        Returns:
            Number of filter rules
        """
        query = self.session.query(FilterRuleModel)

        if enabled_only:
            query = query.filter(FilterRuleModel.enabled == True)

        if rule_type is not None:
            query = query.filter(FilterRuleModel.rule_type == rule_type)

        if match_type is not None:
            query = query.filter(FilterRuleModel.match_type == match_type)

        return query.count()

    def get_enabled_rules(self) -> list[FilterRuleModel]:
        """Get all enabled rules ordered by priority (descending).

        Returns:
            List of enabled FilterRuleModel instances
        """
        return (
            self.session.query(FilterRuleModel)
            .filter(FilterRuleModel.enabled == True)
            .order_by(desc(FilterRuleModel.priority))
            .all()
        )

    def delete_by_id(self, rule_id: int) -> bool:
        """Delete a filter rule by ID.

        Args:
            rule_id: Filter rule ID

        Returns:
            True if deleted, False if not found
        """
        rule = self.get_by_id(rule_id)
        if rule:
            self.delete(rule)
            return True
        return False

    def toggle_enabled(self, rule_id: int) -> Optional[FilterRuleModel]:
        """Toggle the enabled status of a filter rule.

        Args:
            rule_id: Filter rule ID

        Returns:
            Updated FilterRuleModel instance or None if not found
        """
        rule = self.get_by_id(rule_id)
        if rule:
            rule.enabled = not rule.enabled
            self.session.flush()
            self.session.refresh(rule)
            return rule
        return None
