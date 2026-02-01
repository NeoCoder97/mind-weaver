"""Unit tests for configuration management."""

import os
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from spider_aggregation.config import (
    Config,
    DatabaseConfig,
    DeduplicatorConfig,
    FetcherConfig,
    FeedConfig,
    LoggingConfig,
    SchedulerConfig,
    WebConfig,
    get_config,
    load_config_from_yaml,
    reload_config,
)


class TestDatabaseConfig:
    """Tests for DatabaseConfig."""

    def test_default_values(self):
        """Test default database configuration."""
        config = DatabaseConfig()
        assert config.path == "data/spider_aggregation.db"
        assert config.echo is False
        assert config.pool_size == 5
        assert config.max_overflow == 10

    def test_directory_creation(self, tmp_path):
        """Test that database directory is created."""
        db_path = tmp_path / "subdir" / "test.db"
        config = DatabaseConfig(path=str(db_path))
        assert db_path.parent.exists()

    def test_env_prefix(self, monkeypatch):
        """Test environment variable loading."""
        monkeypatch.setenv("DB_PATH", "/tmp/test.db")
        monkeypatch.setenv("DB_ECHO", "true")
        config = DatabaseConfig()
        assert config.path == "/tmp/test.db"
        assert config.echo is True

    def test_validation(self):
        """Test configuration validation."""
        with pytest.raises(ValidationError):
            DatabaseConfig(pool_size=0)  # Must be >= 1

        with pytest.raises(ValidationError):
            DatabaseConfig(pool_size=101)  # Must be <= 100


class TestSchedulerConfig:
    """Tests for SchedulerConfig."""

    def test_default_values(self):
        """Test default scheduler configuration."""
        config = SchedulerConfig()
        assert config.enabled is True
        assert config.timezone == "Asia/Shanghai"
        assert config.default_interval_minutes == 60
        assert config.min_interval_minutes == 10
        assert config.max_workers == 3

    def test_validation(self):
        """Test configuration validation."""
        with pytest.raises(ValidationError):
            SchedulerConfig(default_interval_minutes=0)  # Must be >= 1

        with pytest.raises(ValidationError):
            SchedulerConfig(max_workers=0)  # Must be >= 1


class TestFetcherConfig:
    """Tests for FetcherConfig."""

    def test_default_values(self):
        """Test default fetcher configuration."""
        config = FetcherConfig()
        assert config.timeout_seconds == 30
        assert config.max_retries == 3
        assert config.follow_redirects is True

    def test_user_agent(self):
        """Test user agent configuration."""
        config = FetcherConfig()
        assert "Mind-Aggregation" in config.user_agent

    def test_validation(self):
        """Test configuration validation."""
        with pytest.raises(ValidationError):
            FetcherConfig(timeout_seconds=0)  # Must be >= 1

        with pytest.raises(ValidationError):
            FetcherConfig(max_retries=11)  # Must be <= 10


class TestDeduplicatorConfig:
    """Tests for DeduplicatorConfig."""

    def test_default_values(self):
        """Test default deduplicator configuration."""
        config = DeduplicatorConfig()
        assert config.enabled is True
        assert config.link_hash_method == "sha256"
        assert config.title_similarity_threshold == 0.85

    def test_validation(self):
        """Test configuration validation."""
        with pytest.raises(ValidationError):
            DeduplicatorConfig(title_similarity_threshold=1.5)  # Must be <= 1.0

        with pytest.raises(ValidationError):
            DeduplicatorConfig(title_similarity_threshold=-0.1)  # Must be >= 0.0


class TestLoggingConfig:
    """Tests for LoggingConfig."""

    def test_default_values(self):
        """Test default logging configuration."""
        config = LoggingConfig()
        assert config.level == "INFO"
        assert config.file_enabled is True
        assert config.console_enabled is True

    def test_level_validation(self):
        """Test log level validation."""
        config = LoggingConfig(level="debug")
        assert config.level == "DEBUG"  # Should be uppercased

        with pytest.raises(ValidationError):
            LoggingConfig(level="INVALID")

    def test_directory_creation(self, tmp_path):
        """Test that log directory is created."""
        log_path = tmp_path / "subdir" / "test.log"
        config = LoggingConfig(file_path=str(log_path))
        assert log_path.parent.exists()


class TestFeedConfig:
    """Tests for FeedConfig."""

    def test_default_values(self):
        """Test default feed configuration."""
        config = FeedConfig()
        assert config.validate_url is True
        assert config.max_consecutive_errors == 10


class TestWebConfig:
    """Tests for WebConfig."""

    def test_default_values(self):
        """Test default web configuration."""
        config = WebConfig()
        assert config.enabled is False
        assert config.host == "127.0.0.1"
        assert config.port == 8000

    def test_validation(self):
        """Test port validation."""
        with pytest.raises(ValidationError):
            WebConfig(port=0)  # Must be >= 1

        with pytest.raises(ValidationError):
            WebConfig(port=70000)  # Must be <= 65535


class TestConfig:
    """Tests for main Config."""

    def test_default_values(self):
        """Test default configuration."""
        config = Config()
        assert config.app_name == "MindWeaver"
        assert config.debug is False
        assert isinstance(config.database, DatabaseConfig)
        assert isinstance(config.scheduler, SchedulerConfig)

    def test_get_config_singleton(self):
        """Test that get_config returns the same instance."""
        config1 = get_config()
        config2 = get_config()
        assert config1 is config2

    def test_get_config_path(self):
        """Test get_config_path method."""
        config = Config(config_dir="test_config")
        path = config.get_config_path("test.yaml")
        assert path == Path("test_config/test.yaml")

    def test_get_data_path(self, tmp_path):
        """Test get_data_path method."""
        config = Config(data_dir=str(tmp_path))
        path = config.get_data_path("subdir/test.db")
        assert path == tmp_path / "subdir" / "test.db"
        assert path.parent.exists()

    def test_env_prefix(self, monkeypatch):
        """Test environment variable prefix."""
        monkeypatch.setenv("MIND_DEBUG", "true")
        monkeypatch.setenv("MIND_APP_NAME", "Test App")
        config = Config()
        assert config.debug is True
        assert config.app_name == "Test App"


class TestYamlConfigLoading:
    """Tests for YAML configuration loading."""

    def test_load_config_from_yaml(self, tmp_path):
        """Test loading configuration from YAML file."""
        config_yaml = tmp_path / "config.yaml"
        test_config = {
            "app_name": "Test App",
            "debug": True,
            "database": {
                "path": "/tmp/test.db",
                "echo": True,
            },
            "scheduler": {
                "enabled": False,
                "default_interval_minutes": 120,
            },
        }

        with config_yaml.open("w") as f:
            yaml.dump(test_config, f)

        config = load_config_from_yaml(str(config_yaml))
        assert config.app_name == "Test App"
        assert config.debug is True
        assert config.database.path == "/tmp/test.db"
        assert config.database.echo is True
        assert config.scheduler.enabled is False
        assert config.scheduler.default_interval_minutes == 120

    def test_load_config_from_nonexistent_file(self):
        """Test loading from nonexistent file raises error."""
        with pytest.raises(FileNotFoundError):
            load_config_from_yaml("nonexistent.yaml")

    def test_reload_config(self, tmp_path, monkeypatch):
        """Test reload_config function."""
        # Create config directory structure
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        config_yaml = config_dir / "config.yaml"

        # Write initial config
        test_config = {"app_name": "Initial App"}
        with config_yaml.open("w") as f:
            yaml.dump(test_config, f)

        # Change to tmp_path so reload_config finds config/config.yaml
        monkeypatch.chdir(tmp_path)
        config = reload_config()
        assert config.app_name == "Initial App"

        # Modify config
        test_config["app_name"] = "Updated App"
        with config_yaml.open("w") as f:
            yaml.dump(test_config, f)

        # Reload and verify
        config = reload_config()
        assert config.app_name == "Updated App"

    def test_yaml_with_env_override(self, tmp_path, monkeypatch):
        """Test that YAML values override environment variables for main config."""
        config_yaml = tmp_path / "config.yaml"
        test_config = {"debug": False}
        with config_yaml.open("w") as f:
            yaml.dump(test_config, f)

        monkeypatch.setenv("MIND_DEBUG", "true")

        config = load_config_from_yaml(str(config_yaml))
        # YAML values override environment variables for main config
        assert config.debug is False

    def test_nested_config_env_override(self, monkeypatch):
        """Test that environment variables work for nested configs."""
        monkeypatch.setenv("DB_PATH", "/tmp/env_test.db")
        monkeypatch.setenv("SCHEDULER_ENABLED", "false")

        config = Config()
        assert config.database.path == "/tmp/env_test.db"
        assert config.scheduler.enabled is False


class TestConfigIntegration:
    """Integration tests for configuration."""

    def test_full_config_loading(self, tmp_path):
        """Test loading a complete configuration file."""
        config_yaml = tmp_path / "full_config.yaml"
        full_config = {
            "app_name": "MindWeaver Test",
            "debug": True,
            "verbose": True,
            "database": {
                "path": "data/test.db",
                "echo": True,
                "pool_size": 10,
            },
            "scheduler": {
                "enabled": True,
                "timezone": "UTC",
                "default_interval_minutes": 30,
            },
            "fetcher": {
                "timeout_seconds": 60,
                "max_retries": 5,
            },
            "deduplicator": {
                "enabled": True,
                "title_similarity_threshold": 0.9,
            },
            "logging": {
                "level": "DEBUG",
                "file_enabled": True,
                "console_enabled": True,
            },
            "feed": {
                "validate_url": True,
                "max_consecutive_errors": 5,
            },
            "web": {
                "enabled": True,
                "host": "0.0.0.0",
                "port": 9000,
            },
        }

        with config_yaml.open("w") as f:
            yaml.dump(full_config, f)

        config = load_config_from_yaml(str(config_yaml))

        # Verify all sections
        assert config.app_name == "MindWeaver Test"
        assert config.debug is True
        assert config.database.path == "data/test.db"
        assert config.database.pool_size == 10
        assert config.scheduler.timezone == "UTC"
        assert config.fetcher.timeout_seconds == 60
        assert config.deduplicator.title_similarity_threshold == 0.9
        assert config.logging.level == "DEBUG"
        assert config.web.port == 9000
