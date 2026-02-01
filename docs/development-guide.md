# MindWeaver - 开发指南

## 目录

- [开发环境设置](#开发环境设置)
- [项目结构](#项目结构)
- [开发工作流](#开发工作流)
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
   uv run mind-weaver --version
   ```

### 开发依赖

```bash
# 安装开发依赖
uv sync --dev

# 或直接安装
uv pip install pytest pytest-cov black ruff
```

---

## 项目结构

```
mind-weaver/
├── src/spider_aggregation/      # 源代码
│   ├── __init__.py
│   ├── cli.py                   # CLI 入口
│   ├── config.py                # 配置管理
│   ├── logger.py                # 日志配置
│   │
│   ├── core/                    # 核心业务逻辑
│   │   ├── __init__.py
│   │   ├── fetcher.py           # RSS 抓取器
│   │   ├── parser.py            # 内容解析器
│   │   ├── deduplicator.py      # 去重逻辑
│   │   └── scheduler.py         # 任务调度器
│   │
│   ├── models/                  # 数据模型
│   │   ├── __init__.py
│   │   ├── feed.py              # 订阅源模型
│   │   └── entry.py             # 条目模型
│   │
│   ├── storage/                 # 存储层
│   │   ├── __init__.py
│   │   ├── database.py          # 数据库连接
│   │   └── repositories/        # 仓储模式
│   │       ├── __init__.py
│   │       ├── feed_repo.py
│   │       └── entry_repo.py
│   │
│   └── utils/                   # 工具函数
│       ├── __init__.py
│       └── hash_utils.py        # 哈希工具
│
├── tests/                       # 测试目录
│   ├── conftest.py              # pytest 配置
│   ├── unit/                    # 单元测试
│   │   ├── test_fetcher.py
│   │   ├── test_parser.py
│   │   ├── test_deduplicator.py
│   │   ├── test_scheduler.py
│   │   └── test_database.py
│   └── integration/             # 集成测试
│       └── test_real_feeds.py
│
├── scripts/                     # 脚本目录
│   └── test_real_feed.py        # 真实 RSS 测试
│
├── docs/                        # 文档
│   ├── architecture.md          # 架构设计
│   ├── api-reference.md         # API 参考
│   └── development-guide.md     # 开发指南（本文件）
│
├── config/                      # 配置文件
│   └── config.yaml              # 主配置
│
├── data/                        # 数据目录
│   ├── spider_aggregation.db    # SQLite 数据库
│   └── logs/                    # 日志文件
│
├── pyproject.toml               # 项目配置
├── .python-version              # Python 版本
└── README.md                    # 项目说明
```

---

## 开发工作流

### 分支策略

```bash
main          # 主分支，稳定版本
├── develop   # 开发分支
└── feature/* # 功能分支
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
git commit -m "feat(fetcher): add ETag support for conditional requests

Implement ETag and Last-Modified header support to avoid
fetching unchanged feeds.

Closes #123"
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

    # Test length limit
    long_title = "A" * 1000
    title = parser._normalize_title(long_title)
    assert len(title) == 500  # Limited to 500 chars
    assert title.endswith("...")
```

#### 集成测试

测试多个模块协作。

```python
# tests/integration/test_real_feeds.py
@pytest.mark.integration
def test_cloudflare_blog_rss_full_pipeline(db_session, feed_repo, entry_repo):
    """Test complete pipeline with real RSS feed."""
    # 1. Create feed
    feed = feed_repo.create(FeedCreate(
        url="https://blog.cloudflare.com/zh-cn/rss",
        name="Cloudflare Blog"
    ))

    # 2. Fetch
    fetcher = create_fetcher(session=db_session)
    result = fetcher.fetch_feed(feed)
    assert result.success is True

    # 3. Parse
    parser = create_parser()
    dedup = create_deduplicator(session=db_session)

    for raw_entry in result.entries:
        parsed = parser.parse_entry(raw_entry)

        # 4. Check duplicate
        dup_result = dedup.check_duplicate(parsed, feed_id=feed.id)
        if not dup_result.is_duplicate:
            # 5. Store
            entry_repo.create(EntryCreate(...))
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
def feed(db_session: Session) -> FeedModel:
    """Create test feed."""
    repo = FeedRepository(db_session)
    return repo.create(FeedCreate(
        url="https://example.com/feed.xml",
        name="Test Feed"
    ))
```

### Mock 和 Patch

使用 unittest.mock 进行模拟：

```python
from unittest.mock import MagicMock, patch

def test_fetch_with_mocked_response(feed):
    """Test fetching with mocked HTTP response."""
    with patch("spider_aggregation.core.fetcher.httpx.Client") as mock_client:
        # Setup mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"<rss>...</rss>"
        mock_response.headers = {}

        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        # Test
        fetcher = FeedFetcher()
        result = fetcher.fetch_feed(feed)

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
            "name": "Python: Current File",
            "type": "debugpy",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "env": {
                "PYTHONPATH": "${workspaceFolder}/src"
            }
        },
        {
            "name": "Python: CLI",
            "type": "debugpy",
            "request": "launch",
            "module": "spider_aggregation.cli",
            "args": ["fetch", "--all"],
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

# 退出
.quit
```

或使用 VS Code SQLite 扩展。

---

## 常见问题

### 如何添加新的订阅源类型？

```python
# 1. 创建自定义 Fetcher
class CustomFetcher(FeedFetcher):
    def fetch_feed(self, feed: FeedModel) -> FetchResult:
        # 自定义抓取逻辑
        pass

# 2. 注册到 CLI
@click.command()
def add-custom-feed(url):
    fetcher = CustomFetcher()
    result = fetcher.fetch_feed(feed)
```

### 如何自定义去重策略？

```python
class CustomDeduplicator(Deduplicator):
    def check_duplicate(self, entry, feed_id):
        # 自定义去重逻辑
        pass

# 使用
dedup = CustomDeduplicator(session=session)
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

3. 创建数据库迁移：
```python
# 使用 SQLAlchemy 手动迁移
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text("ALTER TABLE entries ADD COLUMN new_field VARCHAR(500)"))
```

### 如何处理大型订阅源？

```python
# 配置更长的超时和更大的内容限制
fetcher = FeedFetcher(
    timeout_seconds=60,
    max_content_length=50000
)

# 使用更宽松的去重策略
dedup = Deduplicator(
    strategy=DedupStrategy.RELAXED
)
```

### 如何优化数据库性能？

```python
# 1. 添加索引
CREATE INDEX idx_entries_published_at ON entries(published_at DESC);

# 2. 使用批量操作
entries = [EntryModel(**data) for data in entry_list]
session.bulk_save_objects(entries)

# 3. 定期清理
entry_repo.cleanup_old_entries(days=90)
```

### 调试时如何避免真实 HTTP 请求？

```python
from unittest.mock import patch

with patch("spider_aggregation.core.fetcher.httpx.Client"):
    # 使用 mock 的 HTTP 客户端
    fetcher = FeedFetcher()
    result = fetcher.fetch_feed(feed)
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

---

## 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。
