"""
Unit tests for CategoryModel.
"""

import pytest
from datetime import datetime

from spider_aggregation.models import CategoryModel, CategoryCreate, CategoryUpdate, FeedModel, FeedCreate
from spider_aggregation.storage.database import DatabaseManager
from spider_aggregation.models.feed import Base, feed_categories
from sqlalchemy.exc import IntegrityError


class TestCategoryModel:
    """Test CategoryModel basic functionality."""

    def test_category_creation(self):
        """Test creating a category with all fields."""
        category = CategoryModel(
            name="测试分类",
            description="这是一个测试分类",
            color="#ff5733",
            icon="test",
            enabled=True,
        )

        assert category.name == "测试分类"
        assert category.description == "这是一个测试分类"
        assert category.color == "#ff5733"
        assert category.icon == "test"
        assert category.enabled is True
        # Note: created_at and updated_at are set by database defaults, not by ORM instantiation
        # They will be populated after being saved to the database

    def test_category_defaults(self):
        """Test category default values."""
        category = CategoryModel(name="默认分类")

        assert category.name == "默认分类"
        assert category.description is None
        assert category.color is None
        assert category.icon is None
        # Note: enabled is set by database default, not by ORM instantiation
        # It will be populated after being saved to the database

    def test_category_repr(self):
        """Test category __repr__ method."""
        category = CategoryModel(id=1, name="测试")
        assert repr(category) == "<CategoryModel(id=1, name='测试')>"

    def test_category_name_unique_constraint(self):
        """Test that category names must be unique."""
        # This would be tested at the database level
        # We just verify the model has unique constraint in metadata
        assert CategoryModel.__table__.columns['name'].unique


class TestCategoryPydanticModels:
    """Test Pydantic schemas for Category."""

    def test_category_create_valid(self):
        """Test CategoryCreate schema with valid data."""
        data = {
            "name": "测试分类",
            "description": "描述",
            "color": "#ff5733",
            "icon": "test",
            "enabled": True,
        }

        schema = CategoryCreate(**data)
        assert schema.name == "测试分类"
        assert schema.description == "描述"
        assert schema.color == "#ff5733"
        assert schema.icon == "test"
        assert schema.enabled is True

    def test_category_create_minimal(self):
        """Test CategoryCreate with only required field."""
        schema = CategoryCreate(name="最小分类")
        assert schema.name == "最小分类"
        assert schema.description is None
        assert schema.color is None
        assert schema.icon is None
        assert schema.enabled is True

    def test_category_create_invalid_color(self):
        """Test CategoryCreate with invalid color format."""
        with pytest.raises(ValueError):
            CategoryCreate(name="测试", color="invalid")  # Not a valid hex color

    def test_category_update(self):
        """Test CategoryUpdate schema."""
        schema = CategoryUpdate(
            name="新名称",
            color="#10b981",
        )
        assert schema.name == "新名称"
        assert schema.color == "#10b981"
        assert schema.description is None
        assert schema.icon is None


class TestCategoryDatabaseOperations:
    """Test Category database operations using CategoryRepository."""

    def test_create_and_retrieve_category(self, db_session):
        """Test creating and retrieving a category through repository."""
        from spider_aggregation.storage.repositories.category_repo import CategoryRepository

        repo = CategoryRepository(db_session)

        # Create category
        category = repo.create(
            name="技术博客",
            description="技术文章",
            color="#3b82f6",
            icon="blog",
        )

        assert category.id is not None
        assert category.name == "技术博客"

        # Retrieve by ID
        retrieved = repo.get_by_id(category.id)
        assert retrieved is not None
        assert retrieved.id == category.id
        assert retrieved.name == "技术博客"
        assert retrieved.color == "#3b82f6"

    def test_get_category_by_name(self, db_session):
        """Test retrieving category by name."""
        from spider_aggregation.storage.repositories.category_repo import CategoryRepository

        repo = CategoryRepository(db_session)

        # Create category
        category = repo.create(name="Python")

        # Retrieve by name
        retrieved = repo.get_by_name("Python")
        assert retrieved is not None
        assert retrieved.id == category.id

        # Non-existent name
        assert repo.get_by_name("不存在") is None

    def test_list_categories(self, db_session):
        """Test listing all categories."""
        from spider_aggregation.storage.repositories.category_repo import CategoryRepository

        repo = CategoryRepository(db_session)

        # Create multiple categories
        repo.create(name="分类1")
        repo.create(name="分类2")
        repo.create(name="分类3", enabled=False)

        # List all
        all_categories = repo.list()
        assert len(all_categories) == 3

        # List only enabled
        enabled_only = repo.list(enabled_only=True)
        assert len(enabled_only) == 2

    def test_update_category(self, db_session):
        """Test updating a category."""
        from spider_aggregation.storage.repositories.category_repo import CategoryRepository

        repo = CategoryRepository(db_session)

        category = repo.create(name="原始名称")
        original_id = category.id

        # Update
        updated = repo.update(category, name="新名称", color="#ff0000")

        assert updated.id == original_id
        assert updated.name == "新名称"
        assert updated.color == "#ff0000"

    def test_delete_category(self, db_session):
        """Test deleting a category."""
        from spider_aggregation.storage.repositories.category_repo import CategoryRepository

        repo = CategoryRepository(db_session)

        category = repo.create(name="待删除")
        category_id = category.id

        # Delete
        repo.delete(category)

        # Verify deleted
        assert repo.get_by_id(category_id) is None

    def test_category_feed_relationship(self, db_session):
        """Test many-to-many relationship between categories and feeds."""
        from spider_aggregation.storage.repositories.category_repo import CategoryRepository
        from spider_aggregation.storage.repositories.feed_repo import FeedRepository

        cat_repo = CategoryRepository(db_session)
        feed_repo = FeedRepository(db_session)

        # Create categories
        cat1 = cat_repo.create(name="技术博客")
        cat2 = cat_repo.create(name="新闻")

        # Create feed
        from spider_aggregation.models import FeedCreate
        feed_data = FeedCreate(
            url="https://example.com/feed",
            name="测试订阅源",
        )
        feed = feed_repo.create(feed_data)

        # Add feed to categories
        cat_repo.add_feed_to_category(feed, cat1)
        cat_repo.add_feed_to_category(feed, cat2)

        # Verify relationship
        assert len(feed.categories) == 2
        assert set(c.id for c in feed.categories) == {cat1.id, cat2.id}

        # Get feeds by category
        cat1_feeds = cat_repo.get_feeds_by_category(cat1.id)
        assert len(cat1_feeds) == 1
        assert cat1_feeds[0].id == feed.id

    def test_add_duplicate_feed_to_category(self, db_session):
        """Test that adding same feed to category twice is idempotent."""
        from spider_aggregation.storage.repositories.category_repo import CategoryRepository
        from spider_aggregation.storage.repositories.feed_repo import FeedRepository

        cat_repo = CategoryRepository(db_session)
        feed_repo = FeedRepository(db_session)

        cat = cat_repo.create(name="测试")
        feed_data = FeedCreate(url="https://example.com/feed")
        feed = feed_repo.create(feed_data)

        # Add twice
        cat_repo.add_feed_to_category(feed, cat)
        cat_repo.add_feed_to_category(feed, cat)

        # Should only appear once
        cat_feeds = cat_repo.get_feeds_by_category(cat.id)
        assert len(cat_feeds) == 1
        assert cat_feeds[0].id == feed.id

    def test_remove_feed_from_category(self, db_session):
        """Test removing a feed from a category."""
        from spider_aggregation.storage.repositories.category_repo import CategoryRepository
        from spider_aggregation.storage.repositories.feed_repo import FeedRepository

        cat_repo = CategoryRepository(db_session)
        feed_repo = FeedRepository(db_session)

        cat = cat_repo.create(name="测试")
        feed_data = FeedCreate(url="https://example.com/feed")
        feed = feed_repo.create(feed_data)

        # Add then remove
        cat_repo.add_feed_to_category(feed, cat)
        assert len(feed.categories) == 1

        cat_repo.remove_feed_from_category(feed, cat)
        assert len(feed.categories) == 0

    def test_cascade_delete_category_removes_associations(self, db_session):
        """Test that deleting a category removes feed associations but not feeds."""
        from spider_aggregation.storage.repositories.category_repo import CategoryRepository
        from spider_aggregation.storage.repositories.feed_repo import FeedRepository
        from spider_aggregation.models import FeedCreate

        cat_repo = CategoryRepository(db_session)
        feed_repo = FeedRepository(db_session)

        cat1 = cat_repo.create(name="分类1")
        cat2 = cat_repo.create(name="分类2")
        feed_data = FeedCreate(url="https://example.com/feed")
        feed = feed_repo.create(feed_data)

        # Add feed to both categories
        cat_repo.add_feed_to_category(feed, cat1)
        cat_repo.add_feed_to_category(feed, cat2)

        # Delete one category
        cat1_id = cat1.id
        cat_repo.delete(cat1)

        # Feed should still exist
        assert feed_repo.get_by_id(feed.id) is not None

        # Feed should only be in cat2 now
        feed = feed_repo.get_by_id(feed.id)
        # Refresh to get latest relationships
        db_session.refresh(feed)
        assert len(feed.categories) == 1
        assert feed.categories[0].id == cat2.id


class TestCategoryConstraints:
    """Test database constraints for CategoryModel."""

    def test_name_unique_constraint(self, db_session):
        """Test that category names must be unique."""
        from spider_aggregation.storage.repositories.category_repo import CategoryRepository

        repo = CategoryRepository(db_session)

        # Create first category
        repo.create(name="唯一名称")

        # Try to create duplicate - should fail at database level
        with pytest.raises(IntegrityError):
            repo.create(name="唯一名称")

    def test_color_format_validation(self):
        """Test that color field stores valid hex colors."""
        # This is validated at Pydantic level
        from spider_aggregation.models.category import CategoryCreate

        # Valid colors
        CategoryCreate(name="测试", color="#ff0000")
        CategoryCreate(name="测试", color="#ABCDEF")
        CategoryCreate(name="测试", color="#123456")

        # Invalid color format
        with pytest.raises(ValueError):
            CategoryCreate(name="测试", color="ff0000")  # Missing #
        with pytest.raises(ValueError):
            CategoryCreate(name="测试", color="#GGGGGG")  # Invalid hex
        with pytest.raises(ValueError):
            CategoryCreate(name="测试", color="#ZZZZZZ")  # Invalid hex
