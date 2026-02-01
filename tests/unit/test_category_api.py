"""
Unit tests for Category API endpoints.
"""

import pytest
import json


class TestCategoryAPI:
    """Test category management API endpoints."""

    def test_api_categories_list(self, client):
        """Test GET /api/categories - list all categories."""
        # Create some categories first
        from spider_aggregation.storage.database import DatabaseManager
        from spider_aggregation.storage.repositories.category_repo import CategoryRepository

        with client.application.app_context():
            db_manager = DatabaseManager(client.application.config["DB_PATH"])
            with db_manager.session() as session:
                cat_repo = CategoryRepository(session)
                cat_repo.create(name="技术博客", color="#3b82f6")
                cat_repo.create(name="新闻", color="#ef4444")

        response = client.get("/api/categories")
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data["success"] is True
        assert len(data["data"]) == 2

    def test_api_categories_list_enabled_only(self, client):
        """Test GET /api/categories?enabled_only=true - list enabled categories."""
        from spider_aggregation.storage.database import DatabaseManager
        from spider_aggregation.storage.repositories.category_repo import CategoryRepository

        with client.application.app_context():
            db_manager = DatabaseManager(client.application.config["DB_PATH"])
            with db_manager.session() as session:
                cat_repo = CategoryRepository(session)
                cat_repo.create(name="Enabled", enabled=True)
                cat_repo.create(name="Disabled", enabled=False)

        response = client.get("/api/categories?enabled_only=true")
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data["success"] is True
        assert len(data["data"]) == 1
        assert data["data"][0]["name"] == "Enabled"

    def test_api_category_detail(self, client):
        """Test GET /api/categories/<id> - get category details."""
        from spider_aggregation.storage.database import DatabaseManager
        from spider_aggregation.storage.repositories.category_repo import CategoryRepository

        with client.application.app_context():
            db_manager = DatabaseManager(client.application.config["DB_PATH"])
            with db_manager.session() as session:
                cat_repo = CategoryRepository(session)
                category = cat_repo.create(name="测试分类", description="测试描述", color="#ff0000")
                category_id = category.id

        response = client.get(f"/api/categories/{category_id}")
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data["success"] is True
        assert data["data"]["name"] == "测试分类"
        assert data["data"]["description"] == "测试描述"
        assert data["data"]["color"] == "#ff0000"

    def test_api_category_detail_not_found(self, client):
        """Test GET /api/categories/<id> - category not found."""
        response = client.get("/api/categories/99999")
        data = json.loads(response.data)

        assert response.status_code == 404
        assert data["success"] is False

    def test_api_category_create(self, client):
        """Test POST /api/categories - create category."""
        payload = {
            "name": "新分类",
            "description": "新分类描述",
            "color": "#10b981",
            "icon": "test",
        }

        response = client.post(
            "/api/categories",
            data=json.dumps(payload),
            content_type="application/json",
        )
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data["success"] is True
        assert data["data"]["name"] == "新分类"
        assert data["data"]["description"] == "新分类描述"
        assert data["data"]["color"] == "#10b981"
        assert data["data"]["icon"] == "test"

    def test_api_category_create_duplicate_name(self, client):
        """Test POST /api/categories - duplicate name should fail."""
        from spider_aggregation.storage.database import DatabaseManager
        from spider_aggregation.storage.repositories.category_repo import CategoryRepository

        with client.application.app_context():
            db_manager = DatabaseManager(client.application.config["DB_PATH"])
            with db_manager.session() as session:
                cat_repo = CategoryRepository(session)
                cat_repo.create(name="重复名称")

        payload = {"name": "重复名称"}

        response = client.post(
            "/api/categories",
            data=json.dumps(payload),
            content_type="application/json",
        )
        data = json.loads(response.data)

        assert response.status_code == 400
        assert data["success"] is False

    def test_api_category_create_missing_name(self, client):
        """Test POST /api/categories - missing name should fail."""
        payload = {"description": "描述"}

        response = client.post(
            "/api/categories",
            data=json.dumps(payload),
            content_type="application/json",
        )
        data = json.loads(response.data)

        assert response.status_code == 400
        assert data["success"] is False

    def test_api_category_update(self, client):
        """Test PUT /api/categories/<id> - update category."""
        from spider_aggregation.storage.database import DatabaseManager
        from spider_aggregation.storage.repositories.category_repo import CategoryRepository

        with client.application.app_context():
            db_manager = DatabaseManager(client.application.config["DB_PATH"])
            with db_manager.session() as session:
                cat_repo = CategoryRepository(session)
                category = cat_repo.create(name="原始名称")
                category_id = category.id

        payload = {"name": "更新后名称", "color": "#ff0000"}

        response = client.put(
            f"/api/categories/{category_id}",
            data=json.dumps(payload),
            content_type="application/json",
        )
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data["success"] is True
        assert data["data"]["name"] == "更新后名称"
        assert data["data"]["color"] == "#ff0000"

    def test_api_category_delete(self, client):
        """Test DELETE /api/categories/<id> - delete category."""
        from spider_aggregation.storage.database import DatabaseManager
        from spider_aggregation.storage.repositories.category_repo import CategoryRepository

        with client.application.app_context():
            db_manager = DatabaseManager(client.application.config["DB_PATH"])
            with db_manager.session() as session:
                cat_repo = CategoryRepository(session)
                category = cat_repo.create(name="待删除")
                category_id = category.id

        response = client.delete(f"/api/categories/{category_id}")
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data["success"] is True

    def test_api_category_toggle(self, client):
        """Test PATCH /api/categories/<id>/toggle - toggle category enabled status."""
        from spider_aggregation.storage.database import DatabaseManager
        from spider_aggregation.storage.repositories.category_repo import CategoryRepository

        with client.application.app_context():
            db_manager = DatabaseManager(client.application.config["DB_PATH"])
            with db_manager.session() as session:
                cat_repo = CategoryRepository(session)
                category = cat_repo.create(name="测试", enabled=True)
                category_id = category.id

        # Toggle to disable
        response = client.post(f"/api/categories/{category_id}/toggle")
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data["success"] is True
        assert data["data"]["enabled"] is False

        # Toggle to enable
        response = client.post(f"/api/categories/{category_id}/toggle")
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data["success"] is True
        assert data["data"]["enabled"] is True

    def test_api_category_feeds(self, client):
        """Test GET /api/categories/<id>/feeds - get feeds in category."""
        from spider_aggregation.storage.database import DatabaseManager
        from spider_aggregation.storage.repositories.category_repo import CategoryRepository
        from spider_aggregation.storage.repositories.feed_repo import FeedRepository
        from spider_aggregation.models import FeedCreate

        with client.application.app_context():
            db_manager = DatabaseManager(client.application.config["DB_PATH"])
            with db_manager.session() as session:
                cat_repo = CategoryRepository(session)
                feed_repo = FeedRepository(session)

                category = cat_repo.create(name="测试分类")
                feed1 = feed_repo.create(FeedCreate(url="https://example.com/feed1"))
                feed2 = feed_repo.create(FeedCreate(url="https://example.com/feed2"))

                cat_repo.add_feed_to_category(feed1, category)
                cat_repo.add_feed_to_category(feed2, category)

                category_id = category.id

        response = client.get(f"/api/categories/{category_id}/feeds")
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data["success"] is True
        assert data["data"]["total"] == 2
        assert len(data["data"]["feeds"]) == 2

    def test_api_categories_stats(self, client):
        """Test GET /api/categories/stats - get category statistics."""
        from spider_aggregation.storage.database import DatabaseManager
        from spider_aggregation.storage.repositories.category_repo import CategoryRepository

        with client.application.app_context():
            db_manager = DatabaseManager(client.application.config["DB_PATH"])
            with db_manager.session() as session:
                cat_repo = CategoryRepository(session)
                cat_repo.create(name="Enabled1", enabled=True)
                cat_repo.create(name="Enabled2", enabled=True)
                cat_repo.create(name="Disabled", enabled=False)

        response = client.get("/api/categories/stats")
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data["success"] is True
        assert data["data"]["total"] == 3
        assert data["data"]["enabled"] == 2


class TestFeedCategoryAPI:
    """Test feed-category relationship API endpoints."""

    def test_api_feed_categories_get(self, client):
        """Test GET /api/feeds/<id>/categories - get feed categories."""
        from spider_aggregation.storage.database import DatabaseManager
        from spider_aggregation.storage.repositories.category_repo import CategoryRepository
        from spider_aggregation.storage.repositories.feed_repo import FeedRepository
        from spider_aggregation.models import FeedCreate

        with client.application.app_context():
            db_manager = DatabaseManager(client.application.config["DB_PATH"])
            with db_manager.session() as session:
                cat_repo = CategoryRepository(session)
                feed_repo = FeedRepository(session)

                cat1 = cat_repo.create(name="分类1")
                cat2 = cat_repo.create(name="分类2")
                feed = feed_repo.create(FeedCreate(url="https://example.com/feed"))

                cat_repo.add_feed_to_category(feed, cat1)
                cat_repo.add_feed_to_category(feed, cat2)

                feed_id = feed.id

        response = client.get(f"/api/feeds/{feed_id}/categories")
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data["success"] is True
        assert len(data["data"]) == 2

    def test_api_feed_set_categories(self, client):
        """Test PUT /api/feeds/<id>/categories - set feed categories."""
        from spider_aggregation.storage.database import DatabaseManager
        from spider_aggregation.storage.repositories.category_repo import CategoryRepository
        from spider_aggregation.storage.repositories.feed_repo import FeedRepository
        from spider_aggregation.models import FeedCreate

        with client.application.app_context():
            db_manager = DatabaseManager(client.application.config["DB_PATH"])
            with db_manager.session() as session:
                cat_repo = CategoryRepository(session)
                feed_repo = FeedRepository(session)

                cat1 = cat_repo.create(name="分类1")
                cat2 = cat_repo.create(name="分类2")
                cat3 = cat_repo.create(name="分类3")
                feed = feed_repo.create(FeedCreate(url="https://example.com/feed"))

                feed_id = feed.id
                cat1_id = cat1.id
                cat2_id = cat2.id
                cat3_id = cat3.id

        payload = {"category_ids": [cat1_id, cat2_id, cat3_id]}

        response = client.put(
            f"/api/feeds/{feed_id}/categories",
            data=json.dumps(payload),
            content_type="application/json",
        )
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data["success"] is True
        assert len(data["data"]) == 3

    def test_api_feed_add_category(self, client):
        """Test PUT /api/feeds/<id>/categories/<cat_id> - add category to feed."""
        from spider_aggregation.storage.database import DatabaseManager
        from spider_aggregation.storage.repositories.category_repo import CategoryRepository
        from spider_aggregation.storage.repositories.feed_repo import FeedRepository
        from spider_aggregation.models import FeedCreate

        with client.application.app_context():
            db_manager = DatabaseManager(client.application.config["DB_PATH"])
            with db_manager.session() as session:
                cat_repo = CategoryRepository(session)
                feed_repo = FeedRepository(session)

                category = cat_repo.create(name="测试分类")
                feed = feed_repo.create(FeedCreate(url="https://example.com/feed"))

                feed_id = feed.id
                category_id = category.id

        response = client.put(f"/api/feeds/{feed_id}/categories/{category_id}")
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data["success"] is True
        assert len(data["data"]) == 1

    def test_api_feed_remove_category(self, client):
        """Test DELETE /api/feeds/<id>/categories/<cat_id> - remove category from feed."""
        from spider_aggregation.storage.database import DatabaseManager
        from spider_aggregation.storage.repositories.category_repo import CategoryRepository
        from spider_aggregation.storage.repositories.feed_repo import FeedRepository
        from spider_aggregation.models import FeedCreate

        with client.application.app_context():
            db_manager = DatabaseManager(client.application.config["DB_PATH"])
            with db_manager.session() as session:
                cat_repo = CategoryRepository(session)
                feed_repo = FeedRepository(session)

                cat1 = cat_repo.create(name="分类1")
                cat2 = cat_repo.create(name="分类2")
                feed = feed_repo.create(FeedCreate(url="https://example.com/feed"))

                cat_repo.add_feed_to_category(feed, cat1)
                cat_repo.add_feed_to_category(feed, cat2)

                feed_id = feed.id
                category_id = cat1.id

        response = client.delete(f"/api/feeds/{feed_id}/categories/{category_id}")
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data["success"] is True
        assert len(data["data"]) == 1


class TestEntryCategoryAPI:
    """Test entry-category filtering API endpoints."""

    def test_api_entries_by_category(self, client):
        """Test GET /api/entries/by-category/<id> - get entries by category."""
        from spider_aggregation.storage.database import DatabaseManager
        from spider_aggregation.storage.repositories.category_repo import CategoryRepository
        from spider_aggregation.storage.repositories.feed_repo import FeedRepository
        from spider_aggregation.storage.repositories.entry_repo import EntryRepository
        from spider_aggregation.models import FeedCreate, EntryCreate
        from spider_aggregation.utils.hash_utils import compute_title_hash, compute_link_hash
        from datetime import datetime

        with client.application.app_context():
            db_manager = DatabaseManager(client.application.config["DB_PATH"])
            with db_manager.session() as session:
                cat_repo = CategoryRepository(session)
                feed_repo = FeedRepository(session)
                entry_repo = EntryRepository(session)

                category = cat_repo.create(name="测试分类")
                feed = feed_repo.create(FeedCreate(url="https://example.com/feed"))
                cat_repo.add_feed_to_category(feed, category)

                # Create entries
                link1 = "https://example.com/entry1"
                entry1 = entry_repo.create(EntryCreate(
                    feed_id=feed.id,
                    title="Entry 1",
                    link=link1,
                    published_at=datetime.utcnow(),
                    title_hash=compute_title_hash("Entry 1"),
                    link_hash=compute_link_hash(link1),
                ))

                category_id = category.id

        response = client.get(f"/api/entries/by-category/{category_id}")
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data["success"] is True
        assert data["data"]["total"] == 1
        assert len(data["data"]["entries"]) == 1

    def test_api_entries_by_category_name(self, client):
        """Test GET /api/entries/by-category-name/<name> - get entries by category name."""
        from spider_aggregation.storage.database import DatabaseManager
        from spider_aggregation.storage.repositories.category_repo import CategoryRepository
        from spider_aggregation.storage.repositories.feed_repo import FeedRepository
        from spider_aggregation.storage.repositories.entry_repo import EntryRepository
        from spider_aggregation.models import FeedCreate, EntryCreate
        from spider_aggregation.utils.hash_utils import compute_title_hash, compute_link_hash
        from datetime import datetime

        with client.application.app_context():
            db_manager = DatabaseManager(client.application.config["DB_PATH"])
            with db_manager.session() as session:
                cat_repo = CategoryRepository(session)
                feed_repo = FeedRepository(session)
                entry_repo = EntryRepository(session)

                category = cat_repo.create(name="Python")
                feed = feed_repo.create(FeedCreate(url="https://example.com/feed"))
                cat_repo.add_feed_to_category(feed, category)

                link = "https://example.com/entry"
                entry_repo.create(EntryCreate(
                    feed_id=feed.id,
                    title="Python Tutorial",
                    link=link,
                    published_at=datetime.utcnow(),
                    title_hash=compute_title_hash("Python Tutorial"),
                    link_hash=compute_link_hash(link),
                ))

        response = client.get("/api/entries/by-category-name/Python")
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data["success"] is True
        assert len(data["data"]["entries"]) == 1

    def test_api_entries_search_by_category(self, client):
        """Test GET /api/entries/search-by-category/<id> - search entries within category."""
        from spider_aggregation.storage.database import DatabaseManager
        from spider_aggregation.storage.repositories.category_repo import CategoryRepository
        from spider_aggregation.storage.repositories.feed_repo import FeedRepository
        from spider_aggregation.storage.repositories.entry_repo import EntryRepository
        from spider_aggregation.models import FeedCreate, EntryCreate
        from spider_aggregation.utils.hash_utils import compute_title_hash, compute_link_hash
        from datetime import datetime

        with client.application.app_context():
            db_manager = DatabaseManager(client.application.config["DB_PATH"])
            with db_manager.session() as session:
                cat_repo = CategoryRepository(session)
                feed_repo = FeedRepository(session)
                entry_repo = EntryRepository(session)

                category = cat_repo.create(name="技术博客")
                feed = feed_repo.create(FeedCreate(url="https://example.com/feed"))
                cat_repo.add_feed_to_category(feed, category)

                # Create entries
                link1 = "https://example.com/python"
                entry_repo.create(EntryCreate(
                    feed_id=feed.id,
                    title="Python Tutorial",
                    link=link1,
                    content="Python is great",
                    published_at=datetime.utcnow(),
                    title_hash=compute_title_hash("Python Tutorial"),
                    link_hash=compute_link_hash(link1),
                ))

                link2 = "https://example.com/django"
                entry_repo.create(EntryCreate(
                    feed_id=feed.id,
                    title="Django Guide",
                    link=link2,
                    content="Django is awesome",
                    published_at=datetime.utcnow(),
                    title_hash=compute_title_hash("Django Guide"),
                    link_hash=compute_link_hash(link2),
                ))

                category_id = category.id

        response = client.get(f"/api/entries/search-by-category/{category_id}?q=Python")
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data["success"] is True
        assert len(data["data"]["entries"]) == 1
        entry_title = data["data"]["entries"][0]["title"]
        assert "Python" in entry_title

    def test_api_category_entries_stats(self, client):
        """Test GET /api/categories/<id>/entries/stats - get entry stats for category."""
        from spider_aggregation.storage.database import DatabaseManager
        from spider_aggregation.storage.repositories.category_repo import CategoryRepository
        from spider_aggregation.storage.repositories.feed_repo import FeedRepository
        from spider_aggregation.storage.repositories.entry_repo import EntryRepository
        from spider_aggregation.models import FeedCreate, EntryCreate
        from spider_aggregation.utils.hash_utils import compute_title_hash, compute_link_hash
        from datetime import datetime

        with client.application.app_context():
            db_manager = DatabaseManager(client.application.config["DB_PATH"])
            with db_manager.session() as session:
                cat_repo = CategoryRepository(session)
                feed_repo = FeedRepository(session)
                entry_repo = EntryRepository(session)

                category = cat_repo.create(name="测试分类")
                feed = feed_repo.create(FeedCreate(url="https://example.com/feed"))
                cat_repo.add_feed_to_category(feed, category)

                # Create entries
                link1 = "https://example.com/entry1"
                entry1 = entry_repo.create(EntryCreate(
                    feed_id=feed.id,
                    title="Entry 1",
                    link=link1,
                    published_at=datetime.utcnow(),
                    title_hash=compute_title_hash("Entry 1"),
                    link_hash=compute_link_hash(link1),
                ))
                entry1.language = "en"
                session.flush()

                link2 = "https://example.com/entry2"
                entry2 = entry_repo.create(EntryCreate(
                    feed_id=feed.id,
                    title="Entry 2",
                    link=link2,
                    published_at=datetime.utcnow(),
                    title_hash=compute_title_hash("Entry 2"),
                    link_hash=compute_link_hash(link2),
                ))
                entry2.language = "en"
                session.flush()

                link3 = "https://example.com/entry3"
                entry3 = entry_repo.create(EntryCreate(
                    feed_id=feed.id,
                    title="Entry 3",
                    link=link3,
                    published_at=datetime.utcnow(),
                    title_hash=compute_title_hash("Entry 3"),
                    link_hash=compute_link_hash(link3),
                ))
                entry3.language = "zh"
                session.flush()

                category_id = category.id

        response = client.get(f"/api/categories/{category_id}/entries/stats")
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data["success"] is True
        assert data["data"]["total"] == 3
        assert data["data"]["language_counts"]["en"] == 2
        assert data["data"]["language_counts"]["zh"] == 1
