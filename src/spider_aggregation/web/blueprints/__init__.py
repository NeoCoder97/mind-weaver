"""
API blueprints for the MindWeaver web application.

This module contains all API blueprints organized by resource.
"""

from spider_aggregation.web.blueprints.feeds import FeedBlueprint
from spider_aggregation.web.blueprints.categories import CategoryBlueprint
from spider_aggregation.web.blueprints.filter_rules import FilterRuleBlueprint
from spider_aggregation.web.blueprints.entries import EntryBlueprint
from spider_aggregation.web.blueprints.scheduler import SchedulerBlueprint, set_scheduler
from spider_aggregation.web.blueprints.system import SystemBlueprint

__all__ = [
    "FeedBlueprint",
    "CategoryBlueprint",
    "FilterRuleBlueprint",
    "EntryBlueprint",
    "SchedulerBlueprint",
    "SystemBlueprint",
    "set_scheduler",
]
