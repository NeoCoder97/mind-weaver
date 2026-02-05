"""Data models for spider aggregation."""

from spider_aggregation.models.base import Base
from spider_aggregation.models.category import (
    CategoryCreate,
    CategoryListResponse,
    CategoryModel,
    CategoryResponse,
    CategoryUpdate,
)
from spider_aggregation.models.digest_log import (
    DigestLogCreate,
    DigestLogListResponse,
    DigestLogModel,
    DigestLogResponse,
    DigestLogUpdate,
)
from spider_aggregation.models.entry import (
    EntryCreate,
    EntryListResponse,
    EntryModel,
    EntryResponse,
    EntryUpdate,
)
from spider_aggregation.models.filter_rule import (
    FilterRuleCreate,
    FilterRuleListResponse,
    FilterRuleModel,
    FilterRuleResponse,
    FilterRuleUpdate,
)
from spider_aggregation.models.feed import (
    FeedCreate,
    FeedListResponse,
    FeedModel,
    FeedResponse,
    FeedUpdate,
    feed_categories,
)

__all__ = [
    "Base",
    "FeedModel",
    "FeedCreate",
    "FeedUpdate",
    "FeedResponse",
    "FeedListResponse",
    "feed_categories",
    "EntryModel",
    "EntryCreate",
    "EntryUpdate",
    "EntryResponse",
    "EntryListResponse",
    "FilterRuleModel",
    "FilterRuleCreate",
    "FilterRuleUpdate",
    "FilterRuleResponse",
    "FilterRuleListResponse",
    "CategoryModel",
    "CategoryCreate",
    "CategoryUpdate",
    "CategoryResponse",
    "CategoryListResponse",
    "DigestLogModel",
    "DigestLogCreate",
    "DigestLogUpdate",
    "DigestLogResponse",
    "DigestLogListResponse",
]
