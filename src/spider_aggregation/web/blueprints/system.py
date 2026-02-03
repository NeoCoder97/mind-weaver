"""
System and Dashboard API blueprint.

This module contains statistics, dashboard, and system management API endpoints.
"""

from flask import request, jsonify
from spider_aggregation.web.serializers import api_response, entry_to_dict, feed_to_dict


class SystemBlueprint:
    """Blueprint for system management and dashboard operations."""

    def __init__(self, db_path: str):
        """Initialize the system blueprint.

        Args:
            db_path: Path to the database file
        """
        from flask import Blueprint

        self.db_path = db_path
        self.blueprint = Blueprint(
            "system",
            __name__,
            url_prefix="/api"
        )
        self._register_routes()

    def _register_routes(self):
        """Register all system and dashboard routes."""
        # Statistics
        self.blueprint.add_url_rule(
            "/stats",
            view_func=self._stats,
            methods=["GET"]
        )
        # Dashboard activity
        self.blueprint.add_url_rule(
            "/dashboard/activity",
            view_func=self._dashboard_activity,
            methods=["GET"]
        )
        # Dashboard feed health
        self.blueprint.add_url_rule(
            "/dashboard/feed-health",
            view_func=self._dashboard_feed_health,
            methods=["GET"]
        )
        # System cleanup
        self.blueprint.add_url_rule(
            "/system/cleanup",
            view_func=self._cleanup,
            methods=["POST"]
        )
        # Export entries
        self.blueprint.add_url_rule(
            "/system/export/entries",
            view_func=self._export_entries,
            methods=["GET"]
        )
        # Export feeds
        self.blueprint.add_url_rule(
            "/system/export/feeds",
            view_func=self._export_feeds,
            methods=["GET"]
        )

    def _stats(self):
        """Get overall statistics.

        Returns:
            API response with system statistics
        """
        from spider_aggregation.storage.database import DatabaseManager
        from spider_aggregation.storage.repositories.entry_repo import EntryRepository
        from spider_aggregation.storage.repositories.feed_repo import FeedRepository
        from spider_aggregation.storage.repositories.filter_rule_repo import FilterRuleRepository
        from spider_aggregation.storage.repositories.category_repo import CategoryRepository

        db_manager = DatabaseManager(self.db_path)

        with db_manager.session() as session:
            entry_repo = EntryRepository(session)
            feed_repo = FeedRepository(session)
            rule_repo = FilterRuleRepository(session)
            cat_repo = CategoryRepository(session)

            entry_stats = entry_repo.get_stats()
            feed_count = feed_repo.count()
            enabled_feed_count = feed_repo.count(enabled_only=True)
            rule_count = rule_repo.count()
            category_count = cat_repo.count()

            stats = {
                "total_entries": entry_stats["total"],
                "total_feeds": feed_count,
                "enabled_feeds": enabled_feed_count,
                "total_rules": rule_count,
                "total_categories": category_count,
                "language_counts": entry_stats["language_counts"],
                "most_recent": entry_stats["most_recent"].isoformat()
                if entry_stats["most_recent"]
                else None,
            }

        return jsonify(stats)

    def _dashboard_activity(self):
        """Get recent activity for dashboard.

        Query params:
            limit: Number of entries to return (default: 10)

        Returns:
            API response with recent entries
        """
        from spider_aggregation.storage.database import DatabaseManager
        from spider_aggregation.storage.repositories.entry_repo import EntryRepository

        limit = request.args.get("limit", 10, type=int)

        db_manager = DatabaseManager(self.db_path)

        with db_manager.session() as session:
            entry_repo = EntryRepository(session)
            entries = entry_repo.list(
                limit=limit,
                order_by="fetched_at",
                order_desc=True,
            )

            data = [entry_to_dict(e) for e in entries]

        return api_response(
            success=True,
            data=data,
        )

    def _dashboard_feed_health(self):
        """Get feed health status for dashboard.

        Returns:
            API response with feed health data
        """
        from spider_aggregation.storage.database import DatabaseManager
        from spider_aggregation.storage.repositories.feed_repo import FeedRepository

        db_manager = DatabaseManager(self.db_path)

        with db_manager.session() as session:
            feed_repo = FeedRepository(session)
            feeds = feed_repo.list(limit=1000)

            health_data = []
            for feed in feeds:
                health_data.append({
                    "id": feed.id,
                    "name": feed.name or feed.url,
                    "url": feed.url,
                    "enabled": feed.enabled,
                    "error_count": feed.fetch_error_count,
                    "last_fetched": feed.last_fetched_at.isoformat() if feed.last_fetched_at else None,
                    "has_error": bool(feed.last_error),
                })

        return api_response(success=True, data=health_data)

    def _cleanup(self):
        """Clean up old entries.

        Request body:
            {"days": 90}  # Number of days to keep

        Returns:
            API response with cleanup results
        """
        from spider_aggregation.storage.database import DatabaseManager
        from spider_aggregation.storage.repositories.entry_repo import EntryRepository

        data = request.get_json() or {}
        days = data.get("days", 90)

        db_manager = DatabaseManager(self.db_path)

        with db_manager.session() as session:
            entry_repo = EntryRepository(session)
            deleted_count = entry_repo.cleanup_old_entries(days=days)

        return api_response(
            success=True,
            data={"deleted_count": deleted_count},
            message=f"已清理 {deleted_count} 篇旧文章"
        )

    def _export_entries(self):
        """Export entries as JSON file.

        Query params:
            feed_id: Optional feed ID to filter
            limit: Maximum entries to export (default: 1000)

        Returns:
            JSON file response
        """
        from spider_aggregation.storage.database import DatabaseManager
        from spider_aggregation.storage.repositories.entry_repo import EntryRepository

        feed_id = request.args.get("feed_id", type=int)
        limit = request.args.get("limit", 1000, type=int)

        db_manager = DatabaseManager(self.db_path)

        with db_manager.session() as session:
            entry_repo = EntryRepository(session)
            entries = entry_repo.list(
                feed_id=feed_id,
                limit=limit,
                order_by="published_at",
                order_desc=True,
            )

            data = [entry_to_dict(e) for e in entries]

        response = jsonify(data)
        response.headers["Content-Disposition"] = "attachment; filename=entries.json"
        response.headers["Content-Type"] = "application/json"
        return response

    def _export_feeds(self):
        """Export feeds as JSON file.

        Returns:
            JSON file response
        """
        from spider_aggregation.storage.database import DatabaseManager
        from spider_aggregation.storage.repositories.feed_repo import FeedRepository

        db_manager = DatabaseManager(self.db_path)

        with db_manager.session() as session:
            feed_repo = FeedRepository(session)
            feeds = feed_repo.list(limit=1000)

            data = [feed_to_dict(f) for f in feeds]

        response = jsonify(data)
        response.headers["Content-Disposition"] = "attachment; filename=feeds.json"
        response.headers["Content-Type"] = "application/json"
        return response
