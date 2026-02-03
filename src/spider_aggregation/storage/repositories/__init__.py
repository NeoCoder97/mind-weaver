"""Repository pattern implementations for data access."""

from spider_aggregation.storage.repositories.base import BaseRepository
from spider_aggregation.storage.repositories.mixins import CategoryQueryMixin
from spider_aggregation.storage.repositories.entry_repo import EntryRepository
from spider_aggregation.storage.repositories.feed_repo import FeedRepository
from spider_aggregation.storage.repositories.filter_rule_repo import FilterRuleRepository
from spider_aggregation.storage.repositories.category_repo import CategoryRepository

__all__ = [
    "BaseRepository",
    "CategoryQueryMixin",
    "EntryRepository",
    "FeedRepository",
    "FilterRuleRepository",
    "CategoryRepository",
]
