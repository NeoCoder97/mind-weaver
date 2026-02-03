# MindWeaver - 开发指南

## 目录

- [开发环境设置](#开发环境设置)
- [项目结构](#项目结构)
- [开发工作流](#开发工作流)
- [架构设计原则](#架构设计原则)
- [测试指南](#测试指南)
- [代码规范](#代码规范)
- [调试技巧](#调试技巧)
- [常见问题](#常见问题)

---

## 开发环境设置

### 系统要求

- Python 3.14+
- uv (推荐的包管理器)
- Git

### 安装步骤

1. **克隆仓库**
   ```bash
   git clone <repository-url>
   cd mind-weaver
   ```

2. **安装 uv**（如果尚未安装）
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **安装依赖**
   ```bash
   uv sync
   ```

4. **激活虚拟环境**
   ```bash
   source .venv/bin/activate  # Linux/macOS
   # 或
   .venv\Scripts\activate     # Windows
   ```

5. **验证安装**
   ```bash
   uv run mind-weaver
   ```

### 开发依赖

```bash
# 安装开发依赖
uv sync --dev

# 或直接安装
uv pip install pytest pytest-cov black ruff mypy
```

---

## 项目结构

```
mind-weaver/
├── src/spider_aggregation/          # 源代码
│   ├── __init__.py
│   ├── __main__.py                  # 程序入口点
│   ├── config.py                    # 配置管理
│   ├── logger.py                    # 日志配置
│   │
│   ├── core/                        # 核心业务逻辑
│   │   ├── __init__.py
│   │   ├── fetcher.py               # RSS 抓取器
│   │   ├── parser.py                # 内容解析器
│   │   ├── deduplicator.py          # 去重逻辑
│   │   ├── scheduler.py             # 任务调度器
│   │   ├── filter_engine.py         # 过滤引擎
│   │   ├── content_fetcher.py       # 内容提取
│   │   ├── keyword_extractor.py     # 关键词提取
│   │   ├── summarizer.py            # 摘要生成
│   │   ├── factories.py             # 工厂函数
│   │   └── services/                # Service Layer (Facade)
│   │       ├── __init__.py
│   │       ├── fetcher_service.py
│   │       ├── parser_service.py
│   │       ├── deduplicator_service.py
│   │       ├── scheduler_service.py
│   │       ├── filter_service.py
│   │       ├── content_service.py
│   │       ├── keyword_service.py
│   │       └── summarizer_service.py
│   │
│   ├── models/                      # 数据模型
│   │   ├── __init__.py
│   │   ├── base.py                  # ORM 基类
│   │   ├── feed.py                  # 订阅源模型
│   │   ├── entry.py                 # 条目模型
│   │   ├── category.py              # 分类模型
│   │   └── filter_rule.py           # 过滤规则模型
│   │
│   ├── storage/                     # 存储层
│   │   ├── __init__.py
│   │   ├── database.py              # 数据库管理
│   │   ├── mixins.py                # 通用 Mixins
│   │   ├── dialects/                # 数据库方言
│   │   │   ├── __init__.py
│   │   │   ├── base.py              # 方言基类
│   │   │   ├── sqlite.py            # SQLite 实现
│   │   │   ├── postgresql.py        # PostgreSQL 实现
│   │   │   └── mysql.py             # MySQL 实现
│   │   └── repositories/            # Repository 模式
│   │       ├── __init__.py
│   │       ├── base.py              # Repository 基类
│   │       ├── mixins.py            # Repository Mixins
│   │       ├── feed_repo.py         # Feed Repository
│   │       ├── entry_repo.py        # Entry Repository
│   │       ├── category_repo.py     # Category Repository
│   │       └── filter_rule_repo.py  # FilterRule Repository
│   │
│   ├── web/                         # Web 层
│   │   ├── __init__.py
│   │   ├── app.py                   # Flask 应用工厂
│   │   ├── __main__.py              # Web 入口
│   │   ├── serializers.py           # 序列化工具
│   │   ├── scheduler_manager.py     # 调度器管理
│   │   ├── blueprints/              # Blueprint 模块
│   │   │   ├── __init__.py
│   │   │   ├── base.py              # CRUDBlueprint 基类
│   │   │   ├── feeds.py             # Feed API
│   │   │   ├── categories.py        # Category API
│   │   │   ├── entries.py           # Entry API
│   │   │   ├── filter_rules.py      # FilterRule API
│   │   │   ├── scheduler.py         # Scheduler API
│   │   │   └── system.py            # System API
│   │   ├── templates/               # Jinja2 模板
│   │   │   ├── base.html
│   │   │   ├── dashboard.html
│   │   │   ├── feeds.html
│   │   │   ├── entries.html
│   │   │   ├── categories.html
│   │   │   ├── filter_rules.html
│   │   │   └── settings.html
│   │   └── static/                  # 静态资源
│   │       ├── css/
│   │       └── js/
│   │
│   └── utils/                       # 工具函数
│       ├── __init__.py
│       └── hash_utils.py            # 哈希工具
│
├── tests/                           # 测试目录
│   ├── conftest.py                  # pytest 配置
│   ├── unit/                        # 单元测试
│   │   ├── test_fetcher.py
│   │   ├── test_parser.py
│   │   ├── test_deduplicator.py
│   │   ├── test_scheduler.py
│   │   ├── test_filter_engine.py
│   │   └── test_database.py
│   └── integration/                 # 集成测试
│       └── test_real_feeds.py
│
├── scripts/                         # 脚本目录
│   ├── init_db.py                   # 数据库初始化
│   ├── seed_feeds.py                # 种子订阅源
│   ├── seed_filter_rules.py         # 种子过滤规则
│   ├── test_real_feed.py            # 真实 RSS 测试
│   ├── migrate_phase2.py            # Phase 2 迁移
│   ├── migrate_categories.py        # 分类迁移
│   └── migrate_feed_settings.py     # 订阅源设置迁移
│
├── docs/                            # 文档
│   ├── architecture.md              # 架构设计
│   ├── api-reference.md             # API 参考
│   ├── development-guide.md         # 开发指南（本文件）
│   ├── alembic_guide.md             # Alembic 迁移指南
│   └── ALEMBIC_QUICKREF.md          # Alembic 快速参考
│
├── config/                          # 配置文件
│   ├── config.yaml                  # 主配置
│   ├── feeds.example.yaml           # 订阅源配置示例
│   └── filters.example.yaml         # 过滤规则配置示例
│
├── migrations/                      # Alembic 数据库迁移
│   ├── env.py
│   ├── script.py.mako
│   └── versions/                    # 迁移版本
│
├── data/                            # 数据目录
│   └── spider_aggregation.db        # SQLite 数据库
│
├── logs/                            # 日志目录
│   └── mind-weaver.log
│
├── pyproject.toml                   # 项目配置
├── alembic.ini                      # Alembic 配置
├── .python-version                  # Python 版本
└── README.md                        # 项目说明
```

---

## 开发工作流

### 分支策略

```
main          # 主分支，稳定版本
├── develop   # 开发分支
└── feature/* # 功能分支
```

### 启动开发服务器

```bash
# 启动 Web 应用
uv run mind-weaver

# 指定 host 和 port
export MIND_WEB_HOST=0.0.0.0
export MIND_WEB_PORT=8000
uv run mind-weaver

# 启用调试模式
export MIND_WEB_DEBUG=true
uv run mind-weaver
```

### 开发新功能

1. **创建功能分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **开发代码**
   - 遵循代码规范
   - 添加类型注解
   - 编写测试
   - 更新文档

3. **运行测试**
   ```bash
   # 运行所有测试
   uv run pytest

   # 运行特定测试文件
   uv run pytest tests/unit/test_fetcher.py

   # 查看覆盖率
   uv run pytest --cov=src/spider_aggregation --cov-report=html
   ```

4. **代码格式化**
   ```bash
   # 格式化代码
   uv run black src/ tests/

   # 检查代码规范
   uv run ruff check src/ tests/

   # 自动修复
   uv run ruff check --fix src/ tests/
   ```

5. **提交代码**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

6. **推送并创建 PR**
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit 规范

使用约定式提交（Conventional Commits）：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型**：
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具相关

**示例**：
```bash
git commit -m "feat(web): add category management API

Add CRUD endpoints for feed categories with color and icon support.

- POST /api/categories
- GET /api/categories/{id}
- PUT /api/categories/{id}
- DELETE /api/categories/{id}

Closes #123"
```

---

## 架构设计原则

### Service Layer (Facade 模式)

Web 层必须通过 Service Layer 访问核心模块。

```python
# Correct - 使用 Service Facade
from spider_aggregation.core.services import FetcherService

fetcher = FetcherService(session=session)
result = fetcher.fetch_feed(url=feed_url, feed_id=feed_id)

# Wrong - 直接导入核心模块（禁止）
from spider_aggregation.core.fetcher import FeedFetcher  # VIOLATION
```

**核心服务**：
- `FetcherService` - 抓取服务
- `ParserService` - 解析服务
- `DeduplicatorService` - 去重服务
- `SchedulerService` - 调度服务
- `FilterService` - 过滤服务
- `ContentService` - 内容提取服务
- `KeywordService` - 关键词服务
- `SummarizerService` - 摘要服务

### Repository 模式

数据访问通过 Repository 层：

```python
from spider_aggregation.storage.repositories.feed_repo import FeedRepository
from spider_aggregation.storage.repositories.category_repo import CategoryRepository
from spider_aggregation.storage.repositories.entry_repo import EntryRepository

# 使用 Repository
with db_manager.session() as session:
    feed_repo = FeedRepository(session)
    feed = feed_repo.get_by_id(1)

    category_repo = CategoryRepository(session)
    categories = category_repo.list()
```

### Blueprint 模式

Web API 使用 Flask Blueprint 模块化：

```python
from spider_aggregation.web.blueprints.base import CRUDBlueprint

class CustomBlueprint(CRUDBlueprint):
    """自定义 Blueprint."""

    def __init__(self, db_path: str):
        super().__init__(db_path, url_prefix="/api/custom")

    def get_repository_class(self):
        from spider_aggregation.storage.repositories.custom_repo import CustomRepository
        return CustomRepository

    def get_create_schema_class(self):
        from spider_aggregation.models import CustomCreate
        return CustomCreate
```

---

## 测试指南

### 测试类型

#### 单元测试

测试单个函数或类的行为。

```python
# tests/unit/test_parser.py
import pytest
from spider_aggregation.core.parser import ContentParser

def test_normalize_title():
    """Test title normalization."""
    parser = ContentParser()

    # Test basic normalization
    title = parser._normalize_title("  Hello  World  ")
    assert title == "Hello World"

    # Test HTML entities
    title = parser._normalize_title("Hello &amp; World")
    assert title == "Hello & World"
```

#### 集成测试

测试多个模块协作。

```python
# tests/integration/test_real_feeds.py
@pytest.mark.integration
@pytest.mark.slow
def test_cloudflare_blog_rss_full_pipeline(db_session, feed_repo, entry_repo):
    """Test complete pipeline with real RSS feed."""
    from spider_aggregation.core.services import (
        FetcherService, ParserService, DeduplicatorService
    )

    # 1. Create feed
    feed = feed_repo.create(FeedCreate(
        url="https://blog.cloudflare.com/zh-cn/rss",
        name="Cloudflare Blog"
    ))

    # 2. Use Service Layer
    fetcher = FetcherService(session=db_session)
    parser = ParserService()
    dedup = DeduplicatorService(session=db_session)

    # 3. Fetch
    result = fetcher.fetch_feed(url=feed.url, feed_id=feed.id)
    assert result.success is True

    # 4. Parse and store
    for entry_data in result.entries:
        parsed = parser.parse_entry(entry_data, feed_id=feed.id)
        duplicate = dedup.check_duplicate(parsed, entry_repo, feed_id=feed.id)
        if not duplicate.is_duplicate:
            entry_repo.create(EntryCreate(**parsed))
```

### Fixtures

常用 pytest fixtures：

```python
# tests/conftest.py
import pytest
from sqlalchemy.orm import Session
from spider_aggregation.storage.database import DatabaseManager

@pytest.fixture
def db_manager():
    """Create test database manager."""
    manager = DatabaseManager(":memory:")
    manager.init_db()
    yield manager
    manager.close()

@pytest.fixture
def db_session(db_manager: DatabaseManager) -> Session:
    """Create test database session."""
    with db_manager.session() as session:
        yield session

@pytest.fixture
def feed(db_session: Session):
    """Create test feed."""
    from spider_aggregation.storage.repositories.feed_repo import FeedRepository
    from spider_aggregation.models import FeedCreate

    repo = FeedRepository(db_session)
    return repo.create(FeedCreate(
        url="https://example.com/feed.xml",
        name="Test Feed"
    ))

@pytest.fixture
def category(db_session: Session):
    """Create test category."""
    from spider_aggregation.storage.repositories.category_repo import CategoryRepository

    repo = CategoryRepository(db_session)
    return repo.create(name="Test Category", color="#3B82F6")
```

### Mock 和 Patch

使用 unittest.mock 进行模拟：

```python
from unittest.mock import MagicMock, patch

def test_fetch_with_mocked_response():
    """Test fetching with mocked HTTP response."""
    with patch("spider_aggregation.core.fetcher.httpx.Client") as mock_client:
        # Setup mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"<rss>...</rss>"
        mock_response.headers = {}

        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        # Test using Service Layer
        from spider_aggregation.core.services import FetcherService
        fetcher = FetcherService(session=None)
        result = fetcher.fetch_feed(url="https://example.com/feed")

        assert result.success is True
```

### 测试标记

使用 pytest 标记组织测试：

```python
@pytest.mark.unit
def test_parser_normalize_title():
    """Unit test for parser."""
    pass

@pytest.mark.integration
@pytest.mark.slow
def test_real_feed_fetch():
    """Slow integration test."""
    pass
```

运行特定标记的测试：
```bash
# 只运行单元测试
uv run pytest -m unit

# 跳过慢速测试
uv run pytest -m "not slow"

# 运行集成测试
uv run pytest -m integration
```

---

## 代码规范

### Python 风格指南

遵循 PEP 8 和以下约定：

#### 命名约定

```python
# 模块和包：小写，下划线
spider_aggregation/
feed_repo.py

# 类：大驼峰
class FeedFetcher:
    pass

# 函数和变量：小写，下划线
def fetch_feed():
    pass

fetch_count = 0

# 常量：大写，下划线
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30

# 私有成员：前缀下划线
class MyClass:
    def __init__(self):
        self._private_var = None

    def _private_method(self):
        pass
```

#### 类型注解

所有公共 API 必须有类型注解：

```python
from typing import Optional, List
from spider_aggregation.models import FeedModel

def fetch_feed(feed: FeedModel) -> FetchResult:
    """Fetch a feed.

    Args:
        feed: Feed model to fetch

    Returns:
        Fetch result with entries
    """
    pass

def parse_entries(
    entries: List[dict],
    max_count: Optional[int] = None
) -> List[dict]:
    """Parse multiple entries.

    Args:
        entries: Raw entries to parse
        max_count: Maximum number of entries to parse

    Returns:
        Parsed entries
    """
    pass
```

#### 文档字符串

使用 Google 风格：

```python
def normalize_content(
    self,
    content: Optional[str],
    max_length: int = 10000
) -> Optional[str]:
    """Normalize and clean content.

    Removes HTML tags, normalizes whitespace, and limits length.

    Args:
        content: Raw content string
        max_length: Maximum length in characters

    Returns:
        Normalized content or None if input is None

    Raises:
        ValueError: If content is not a string

    Examples:
        >>> parser = ContentParser()
        >>> parser.normalize_content("<p>Hello</p>", 100)
        'Hello'
    """
    pass
```

#### 错误处理

```python
from spider_aggregation.logger import get_logger

logger = get_logger(__name__)

# 使用具体的异常
try:
    result = fetcher.fetch_feed(feed)
except httpx.TimeoutError as e:
    logger.warning(f"Timeout fetching {feed.url}: {e}")
    # Handle timeout
except httpx.HTTPStatusError as e:
    if e.response.status_code == 404:
        logger.error(f"Feed not found: {feed.url}")
        # Don't retry
    else:
        logger.warning(f"HTTP error: {e}")
        # Retry
except Exception as e:
    logger.exception(f"Unexpected error: {e}")
    # Handle or re-raise
```

### Black 配置

项目使用 Black 进行代码格式化：

```toml
[tool.black]
line-length = 100
target-version = ['py314']
```

运行：
```bash
uv run black src/ tests/
```

### Ruff 配置

项目使用 Ruff 进行代码检查：

```toml
[tool.ruff]
line-length = 100
target-version = "py314"
select = ["E", "F", "I", "N", "W", "UP"]
ignore = ["E501"]  # Line too long (handled by black)
```

运行：
```bash
# 检查
uv run ruff check src/ tests/

# 自动修复
uv run ruff check --fix src/ tests/
```

---

## 调试技巧

### 使用日志

```python
from spider_aggregation.logger import get_logger

logger = get_logger(__name__)

# Debug 级别
logger.debug(f"Fetching feed: {feed.url}")

# Info 级别
logger.info(f"Fetched {len(entries)} entries")

# Warning 级别
logger.warning(f"Feed returned 304 Not Modified")

# Error 级别
logger.error(f"Failed to fetch feed: {error}")

# Exception 级别（包含堆栈跟踪）
logger.exception(f"Unexpected error: {e}")
```

### 使用 pdb 断点

```python
import pdb

def some_function():
    # 设置断点
    pdb.set_trace()

    # 或使用 Python 3.7+ 的 breakpoint()
    breakpoint()

    result = complex_calculation()
    return result
```

### 使用 IDE 调试器

推荐使用 VS Code + Python 扩展：

**launch.json 配置**：
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Flask",
            "type": "debugpy",
            "request": "launch",
            "module": "spider_aggregation.web.__main__",
            "env": {
                "FLASK_APP": "spider_aggregation.web.app",
                "FLASK_DEBUG": "1",
                "PYTHONPATH": "${workspaceFolder}/src"
            },
            "args": [
                "run",
                "--no-debugger",
                "--no-reload"
            ],
            "jinja": true,
            "justMyCode": false
        },
        {
            "name": "Python: Current File",
            "type": "debugpy",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "env": {
                "PYTHONPATH": "${workspaceFolder}/src"
            }
        }
    ]
}
```

### 查看数据库

使用 SQLite 客户端：

```bash
# 命令行
sqlite3 data/spider_aggregation.db

# 查询
SELECT * FROM feeds;
SELECT * FROM entries ORDER BY fetched_at DESC LIMIT 10;
SELECT * FROM categories;
SELECT * FROM filter_rules;

# 退出
.quit
```

或使用 VS Code SQLite 扩展。

---

## 常见问题

### 如何添加新的订阅源类型？

```python
# 1. 创建自定义 Fetcher
from spider_aggregation.core.fetcher import FeedFetcher

class CustomFetcher(FeedFetcher):
    def fetch_feed(self, feed: FeedModel) -> FetchResult:
        # 自定义抓取逻辑
        pass

# 2. 创建对应的 Service
from spider_aggregation.core.services.fetcher_service import FetcherService

class CustomFetcherService(FetcherService):
    def __init__(self, session=None):
        self.fetcher = CustomFetcher()

# 3. 在 Blueprint 中使用
@bp.route("/api/custom-fetch", methods=["POST"])
def custom_fetch():
    service = CustomFetcherService()
    result = service.fetch_feed(url=request.json["url"])
    return api_response(success=result.success, data=result)
```

### 如何自定义去重策略？

```python
from spider_aggregation.core.deduplicator import Deduplicator

class CustomDeduplicator(Deduplicator):
    def check_duplicate(self, entry, feed_id):
        # 自定义去重逻辑
        pass

# 创建对应的 Service
from spider_aggregation.core.services.deduplicator_service import DeduplicatorService

class CustomDeduplicatorService(DeduplicatorService):
    def __init__(self, session=None):
        self.deduplicator = CustomDeduplicator()
```

### 如何添加新的字段到 Entry 模型？

1. 修改 `models/entry.py`：
```python
class EntryModel(Base):
    # ... existing fields
    new_field: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
```

2. 更新 Pydantic 模型：
```python
class EntryCreate(BaseModel):
    # ... existing fields
    new_field: Optional[str] = None
```

3. 使用 Alembic 创建迁移：
```bash
alembic revision --autogenerate -m "add new_field to entries"
alembic upgrade head
```

### 如何添加新的 Blueprint？

```python
# 1. 在 web/blueprints/ 下创建新文件
# web/blueprints/custom.py

from spider_aggregation.web.blueprints.base import CRUDBlueprint

class CustomBlueprint(CRUDBlueprint):
    def __init__(self, db_path: str):
        super().__init__(db_path, url_prefix="/api/custom")

    def get_repository_class(self):
        from spider_aggregation.storage.repositories.custom_repo import CustomRepository
        return CustomRepository

# 2. 在 app.py 中注册
from spider_aggregation.web.blueprints.custom import CustomBlueprint

custom_bp = CustomBlueprint(db_path)
app.register_blueprint(custom_bp.blueprint)
```

### 如何处理大型订阅源？

```python
# 使用 Service Layer 配置
from spider_aggregation.core.services import FetcherService

fetcher = FetcherService(session=session)
result = fetcher.fetch_feed(
    url=feed_url,
    feed_id=feed_id,
    max_entries=50,  # 限制条目数
)
```

### 如何优化数据库性能？

```python
# 1. 添加索引（通过 Alembic 迁移）
# migrations/versions/xxx_add_indexes.py

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_index('idx_entries_new_field', 'entries', ['new_field'])

# 2. 使用批量操作
with db_manager.session() as session:
    entries = [EntryModel(**data) for data in entry_list]
    session.bulk_save_objects(entries)

# 3. 定期清理
from spider_aggregation.storage.repositories.entry_repo import EntryRepository

entry_repo = EntryRepository(session)
entry_repo.cleanup_old_entries(days=90)
```

### 如何调试时避免真实 HTTP 请求？

```python
from unittest.mock import patch, MagicMock

def test_with_mock():
    with patch("spider_aggregation.core.fetcher.httpx.Client") as mock_client:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"<rss><item><title>Test</title></item></rss>"
        mock_response.headers = {}
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        # 使用 Service Layer
        from spider_aggregation.core.services import FetcherService
        fetcher = FetcherService(session=None)
        result = fetcher.fetch_feed(url="https://test.com/feed")

        assert result.success is True
```

### 如何切换数据库类型？

```bash
# SQLite (默认)
export MIND_DB_TYPE=sqlite
export MIND_DB_PATH=data/spider_aggregation.db

# PostgreSQL
export MIND_DB_TYPE=postgresql
export MIND_DB_HOST=localhost
export MIND_DB_PORT=5432
export MIND_DB_NAME=mindweaver
export MIND_DB_USER=postgres
export MIND_DB_PASSWORD=yourpassword

# MySQL
export MIND_DB_TYPE=mysql
export MIND_DB_HOST=localhost
export MIND_DB_PORT=3306
export MIND_DB_NAME=mindweaver
export MIND_DB_USER=root
export MIND_DB_PASSWORD=yourpassword
```

---

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### Pull Request 检查清单

- [ ] 代码通过所有测试
- [ ] 测试覆盖率不降低
- [ ] 代码通过 Black 和 Ruff 检查
- [ ] 添加了必要的文档
- [ ] 更新了 CHANGELOG（如需要）
- [ ] 所有提交信息遵循约定式提交规范
- [ ] Service Layer 遵循 Facade 模式
- [ ] Web 层不直接导入核心模块

---

## 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。
