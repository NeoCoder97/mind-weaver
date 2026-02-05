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
        self.blueprint = Blueprint("system", __name__, url_prefix="/api")
        self._register_routes()

    def _register_routes(self):
        """Register all system and dashboard routes."""
        # Statistics
        self.blueprint.add_url_rule("/stats", view_func=self._stats, methods=["GET"])
        # Dashboard activity
        self.blueprint.add_url_rule(
            "/dashboard/activity", view_func=self._dashboard_activity, methods=["GET"]
        )
        # Dashboard feed health
        self.blueprint.add_url_rule(
            "/dashboard/feed-health", view_func=self._dashboard_feed_health, methods=["GET"]
        )
        # System cleanup
        self.blueprint.add_url_rule("/system/cleanup", view_func=self._cleanup, methods=["POST"])
        # Export entries
        self.blueprint.add_url_rule(
            "/system/export/entries", view_func=self._export_entries, methods=["GET"]
        )
        # Export feeds
        self.blueprint.add_url_rule(
            "/system/export/feeds", view_func=self._export_feeds, methods=["GET"]
        )
        # Configuration - Get all
        self.blueprint.add_url_rule("/system/config", view_func=self._get_config, methods=["GET"])
        # Configuration - Update LLM
        self.blueprint.add_url_rule(
            "/system/config/llm", view_func=self._update_llm_config, methods=["PUT"]
        )
        # Configuration - Test LLM
        self.blueprint.add_url_rule(
            "/system/config/llm/test", view_func=self._test_llm, methods=["POST"]
        )
        # Configuration - Update Email
        self.blueprint.add_url_rule(
            "/system/config/email", view_func=self._update_email_config, methods=["PUT"]
        )
        # Configuration - Test Email
        self.blueprint.add_url_rule(
            "/system/config/email/test", view_func=self._test_email, methods=["POST"]
        )
        # Configuration - Update Digest
        self.blueprint.add_url_rule(
            "/system/config/digest", view_func=self._update_digest_config, methods=["PUT"]
        )
        # Settings - Get and Update
        self.blueprint.add_url_rule("/settings", view_func=self._settings, methods=["GET"])
        self.blueprint.add_url_rule("/settings", view_func=self._update_settings, methods=["PUT"])
        # Settings - Database size
        self.blueprint.add_url_rule("/settings/db-size", view_func=self._db_size, methods=["GET"])

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

            # Calculate today's entries
            from datetime import datetime, timedelta, timezone

            china_tz = timezone(timedelta(hours=8))
            today_start = datetime.now(china_tz).replace(hour=0, minute=0, second=0, microsecond=0)
            today_entries = entry_repo.count_by_date(today_start)

            stats = {
                "total_entries": entry_stats["total"],
                "total_feeds": feed_count,
                "enabled_feeds": enabled_feed_count,
                "total_rules": rule_count,
                "total_categories": category_count,
                "today_entries": today_entries,
                "language_counts": entry_stats["language_counts"],
                "most_recent": (
                    entry_stats["most_recent"].isoformat() if entry_stats["most_recent"] else None
                ),
            }

        return api_response(success=True, data=stats)

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

            data = []
            for e in entries:
                d = entry_to_dict(e)
                d["feed_name"] = e.feed.name if e.feed else None
                data.append(d)

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
                health_data.append(
                    {
                        "id": feed.id,
                        "name": feed.name or feed.url,
                        "url": feed.url,
                        "enabled": feed.enabled,
                        "error_count": feed.fetch_error_count,
                        "last_fetched": (
                            feed.last_fetched_at.isoformat() if feed.last_fetched_at else None
                        ),
                        "has_error": bool(feed.last_error),
                    }
                )

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
            message=f"已清理 {deleted_count} 篇旧文章",
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

    def _get_config(self):
        """Get all configuration.

        Returns:
            API response with current configuration (excluding sensitive data)
        """
        from spider_aggregation.config import get_config

        config = get_config()

        # Convert to dict, excluding sensitive data
        data = {
            "llm": {
                "enabled": config.llm.enabled,
                "provider": config.llm.provider,
                "api_base": config.llm.api_base,
                "model": config.llm.model,
                "temperature": config.llm.temperature,
                "max_tokens": config.llm.max_tokens,
                # Never include api_key
            },
            "email": {
                "enabled": config.email.enabled,
                "smtp_host": config.email.smtp_host,
                "smtp_port": config.email.smtp_port,
                "username": config.email.username,
                "from_address": config.email.from_address,
                "to_addresses": config.email.to_addresses,
                # Never include password
            },
            "digest": {
                "enabled": config.digest.enabled,
                "schedules": config.digest.schedules,
                "entries_per_feed": config.digest.entries_per_feed,
                "max_age_hours": config.digest.max_age_hours,
                "mode": config.digest.mode,
                "subject_prefix": config.digest.subject_prefix,
            },
        }

        return api_response(success=True, data=data)

    def _update_llm_config(self):
        """Update LLM configuration.

        Request body:
            LLM configuration fields (only provided fields will be updated)

        Returns:
            API response with update result
        """
        from spider_aggregation.config import get_config, reload_config

        data = request.get_json() or {}

        # Read current config file path
        import yaml
        from pathlib import Path

        config = get_config()
        config_path = Path(config.config_dir) / "config.yaml"

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                yaml_config = yaml.safe_load(f) or {}

            # Update LLM section
            if "llm" not in yaml_config:
                yaml_config["llm"] = {}

            for key, value in data.items():
                if value is not None:
                    yaml_config["llm"][key] = value

            # Write back
            with open(config_path, "w", encoding="utf-8") as f:
                yaml.dump(yaml_config, f, allow_unicode=True, default_flow_style=False)

            # Reload configuration
            reload_config()

            return api_response(success=True, message="LLM 配置已更新")
        except Exception as e:
            return api_response(success=False, error=str(e), status=500)

    def _test_llm(self):
        """Test LLM connection.

        Request body:
            {
                "provider": "openai|zhipuai|deepseek",
                "api_key": "test-key",
                "api_base": "optional",
                "model": "optional"
            }

        Returns:
            API response with test result
        """
        from spider_aggregation.core.llm_client import LLMClientFactory

        data = request.get_json() or {}
        provider = data.get("provider", "openai")
        api_key = data.get("api_key")
        api_base = data.get("api_base")
        model = data.get("model")

        if not api_key:
            return api_response(success=False, error="API Key 是必需的")

        try:
            client = LLMClientFactory.create(
                provider=provider,
                api_key=api_key,
                api_base=api_base,
                model=model,
            )

            # Simple test call
            result = client.chat("Hello", system_prompt="You are a helpful assistant.")

            if result.success:
                return api_response(success=True, message="LLM 连接测试成功")
            else:
                return api_response(success=False, error=result.error or "连接失败")

        except Exception as e:
            return api_response(success=False, error=str(e))

    def _update_email_config(self):
        """Update Email configuration.

        Request body:
            Email configuration fields (only provided fields will be updated)

        Returns:
            API response with update result
        """
        from spider_aggregation.config import get_config, reload_config

        data = request.get_json() or {}

        # Read current config file
        import yaml
        from pathlib import Path

        config = get_config()
        config_path = Path(config.config_dir) / "config.yaml"

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                yaml_config = yaml.safe_load(f) or {}

            # Update Email section
            if "email" not in yaml_config:
                yaml_config["email"] = {}

            for key, value in data.items():
                if value is not None:
                    yaml_config["email"][key] = value

            # Write back
            with open(config_path, "w", encoding="utf-8") as f:
                yaml.dump(yaml_config, f, allow_unicode=True, default_flow_style=False)

            # Reload configuration
            reload_config()

            return api_response(success=True, message="邮件配置已更新")
        except Exception as e:
            return api_response(success=False, error=str(e), status=500)

    def _test_email(self):
        """Test email connection.

        Request body:
            {
                "smtp_host": "smtp.example.com",
                "smtp_port": 587,
                "username": "user@example.com",
                "password": "password"
            }

        Returns:
            API response with test result
        """
        from spider_aggregation.application.email_service import EmailService

        data = request.get_json() or {}
        smtp_host = data.get("smtp_host")
        smtp_port = data.get("smtp_port", 587)
        username = data.get("username")
        password = data.get("password")

        if not all([smtp_host, username, password]):
            return api_response(success=False, error="SMTP 配置不完整")

        try:
            service = EmailService(
                smtp_host=smtp_host,
                smtp_port=smtp_port,
                username=username,
                password=password,
            )

            result = service.test_connection()

            if result.success:
                return api_response(success=True, message="SMTP 连接测试成功")
            else:
                return api_response(success=False, error=result.error or "连接失败")

        except Exception as e:
            return api_response(success=False, error=str(e))

    def _update_digest_config(self):
        """Update Digest configuration.

        Request body:
            Digest configuration fields (only provided fields will be updated)

        Returns:
            API response with update result
        """
        from spider_aggregation.config import get_config, reload_config

        data = request.get_json() or {}

        # Read current config file
        import yaml
        from pathlib import Path

        config = get_config()
        config_path = Path(config.config_dir) / "config.yaml"

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                yaml_config = yaml.safe_load(f) or {}

            # Update Digest section
            if "digest" not in yaml_config:
                yaml_config["digest"] = {}

            for key, value in data.items():
                if value is not None:
                    yaml_config["digest"][key] = value

            # Write back
            with open(config_path, "w", encoding="utf-8") as f:
                yaml.dump(yaml_config, f, allow_unicode=True, default_flow_style=False)

            # Reload configuration
            reload_config()

            return api_response(success=True, message="聚合配置已更新")
        except Exception as e:
            return api_response(success=False, error=str(e), status=500)

    def _settings(self):
        """Get application settings.

        Returns:
            API response with current application settings
        """
        from spider_aggregation.config import get_config
        from pathlib import Path

        config = get_config()
        db_path = Path(config.database.path)

        return api_response(
            success=True,
            data={
                "scheduler_interval": 60,
                "max_workers": 3,
                "entry_retention_days": 0,
                "max_content_length": 500000,
                "auto_fetch_content": False,
                "enable_summarization": config.llm.enabled if hasattr(config, "llm") else False,
                "ai_api_key": "",
                "ai_api_url": config.llm.api_base if hasattr(config, "llm") else "",
                "timezone": "Asia/Shanghai",
                "db_path": str(db_path),
            },
        )

    def _update_settings(self):
        """Update application settings.

        Request body:
            Settings fields to update

        Returns:
            API response with update result
        """
        from spider_aggregation.config import get_config, reload_config

        data = request.get_json() or {}

        # Read current config file
        import yaml
        from pathlib import Path

        config = get_config()
        config_path = Path(config.config_dir) / "config.yaml"

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                yaml_config = yaml.safe_load(f) or {}

            # Map frontend field names to config structure
            if data.get("ai_api_key"):
                if "llm" not in yaml_config:
                    yaml_config["llm"] = {}
                yaml_config["llm"]["api_key"] = data["ai_api_key"]

            if data.get("ai_api_url"):
                if "llm" not in yaml_config:
                    yaml_config["llm"] = {}
                yaml_config["llm"]["api_base"] = data["ai_api_url"]

            if "enable_summarization" in data:
                if "llm" not in yaml_config:
                    yaml_config["llm"] = {}
                yaml_config["llm"]["enabled"] = data["enable_summarization"]

            if "max_workers" in data:
                yaml_config["scheduler"]["max_workers"] = data["max_workers"]

            if "auto_fetch_content" in data:
                if "content" not in yaml_config:
                    yaml_config["content"] = {}
                yaml_config["content"]["auto_fetch"] = data["auto_fetch_content"]

            if "max_content_length" in data:
                if "content" not in yaml_config:
                    yaml_config["content"] = {}
                yaml_config["content"]["max_length"] = data["max_content_length"]

            if "timezone" in data:
                yaml_config["timezone"] = data["timezone"]

            # Write back
            with open(config_path, "w", encoding="utf-8") as f:
                yaml.dump(yaml_config, f, allow_unicode=True, default_flow_style=False)

            # Reload configuration
            reload_config()

            return api_response(success=True, message="设置保存成功")
        except Exception as e:
            return api_response(success=False, error=str(e), status=500)

    def _db_size(self):
        """Get database file size.

        Returns:
            API response with database size in bytes
        """
        from spider_aggregation.config import get_config
        from pathlib import Path

        config = get_config()
        db_path = Path(config.database.path)

        size = db_path.stat().st_size if db_path.exists() else 0

        return api_response(success=True, data={"size": size, "path": str(db_path)})
