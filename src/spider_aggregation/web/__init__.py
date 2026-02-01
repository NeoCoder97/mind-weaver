"""
Web UI for spider-aggregation.

Simple Flask application for browsing entries and feeds.
"""

from spider_aggregation.web.app import create_app

__all__ = ["create_app"]
