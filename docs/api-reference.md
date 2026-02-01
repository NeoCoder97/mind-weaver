# Spider Aggregation - API 参考文档

## 目录

- [CLI API](#cli-api)
- [核心模块 API](#核心模块-api)
- [存储层 API](#存储层-api)
- [数据模型](#数据模型)

---

## CLI API

### 命令行工具入口点

```bash
spider-aggregation [OPTIONS] COMMAND [ARGS]...
```

### 全局选项

| 选项 | 简写 | 描述 |
|------|------|------|
| `--db-path TEXT` | | 数据库文件路径（默认: `data/spider_aggregation.db`）|
| `--verbose` | `-v` | 启用详细输出 |
| `--version` | | 显示版本并退出 |
| `--help` | `-h` | 显示帮助信息 |

### 命令列表

#### `init`

初始化数据库。

```bash
spider-aggregation init
```

**示例**：
```bash
$ spider-aggregation init
Initializing Spider Aggregation database...
✅ Database initialized at: data/spider_aggregation.db
```

---

#### `add-feed`

添加新的 RSS/Atom 订阅源。

```bash
spider-aggregation add-feed URL [OPTIONS]
```

| 参数/选项 | 描述 |
|-----------|------|
| `URL` | RSS/Atom 订阅源地址（必需）|
| `--name TEXT`, `-n TEXT` | 订阅源名称（默认：自动检测）|
| `--description TEXT`, `-d TEXT` | 订阅源描述 |
| `--enabled/--disabled` | 启用/禁用（默认：启用）|
| `--interval INTEGER`, `-i INTEGER` | 抓取间隔（分钟）|

**示例**：
```bash
# 自动检测元数据
spider-aggregation add-feed https://blog.cloudflare.com/zh-cn/rss

# 指定名称和间隔
spider-aggregation add-feed https://example.com/feed.xml --name "My Feed" --interval 120
```

---

#### `list-feeds`

列出所有订阅源。

```bash
spider-aggregation list-feeds [OPTIONS]
```

| 选项 | 描述 |
|------|------|
| `--enabled-only/--all` | 仅显示启用的订阅源 |
| `--verbose`, `-v` | 显示详细信息（包括条目数量和最后抓取时间）|

**示例**：
```bash
$ spider-aggregation list-feeds --verbose
```

输出：
```
┏━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ ID     ┃ Name                ┃ URL          ┃ Enabled  ┃ Interval ┃ Last Fetched     ┃ Entry Count ┃
┡━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 1      │ The Cloudflare Blog │ https://...   │    ✓     │      60m │ 2026-02-01 08:54 │         20 │
└────────┴─────────────────────┴──────────────┴──────────┴──────────┴──────────────────┴────────────┘
```

---

#### `fetch`

手动触发订阅源抓取。

```bash
spider-aggregation fetch [FEED_ID] [OPTIONS]
```

| 参数/选项 | 描述 |
|-----------|------|
| `FEED_ID` | 指定订阅源 ID |
| `--all`, `-a` | 抓取所有启用的订阅源 |
| `--force`, `-f` | 强制抓取（即使未到抓取时间）|

**示例**：
```bash
# 抓取所有启用的订阅源
spider-aggregation fetch --all

# 抓取指定订阅源
spider-aggregation fetch 1
```

---

#### `start`

启动调度器进行自动抓取。

```bash
spider-aggregation start [OPTIONS]
```

| 选项 | 描述 |
|------|------|
| `--workers INTEGER`, `-w INTEGER` | 工作线程数（默认：3）|

**示例**：
```bash
$ spider-aggregation start --workers 5
```

按 `Ctrl+C` 停止调度器。

---

#### `list-entries`

列出数据库中的条目。

```bash
spider-aggregation list-entries [OPTIONS]
```

| 选项 | 描述 |
|------|------|
| `--feed-id INTEGER`, `-f INTEGER` | 按订阅源 ID 过滤 |
| `--limit INTEGER`, `-l INTEGER` | 显示数量（默认：20）|
| `--offset INTEGER` | 分页偏移量 |
| `--language TEXT` | 按语言代码过滤（如：en, zh）|
| `--search TEXT`, `-s TEXT` | 在标题和内容中搜索 |

**示例**：
```bash
# 显示最近 10 条中文条目
spider-aggregation list-entries --limit 10 --language zh

# 搜索包含 "Python" 的条目
spider-aggregation list-entries --search Python
```

---

#### `enable-feed`

启用或禁用订阅源。

```bash
spider-aggregation enable-feed FEED_ID [OPTIONS]
```

| 参数/选项 | 描述 |
|-----------|------|
| `FEED_ID` | 订阅源 ID |
| `--enable/--disable` | 启用或禁用（默认：启用）|

**示例**：
```bash
# 禁用订阅源
spider-aggregation enable-feed 1 --disable

# 启用订阅源
spider-aggregation enable-feed 1 --enable
```

---

#### `delete-feed`

删除订阅源及其所有条目。

```bash
spider-aggregation delete-feed FEED_ID
```

| 参数 | 描述 |
|------|------|
| `FEED_ID` | 订阅源 ID |

**示例**：
```bash
$ spider-aggregation delete-feed 1
Deleting feed 'The Cloudflare Blog' and 20 entries...
✅ Feed deleted
```

---

#### `cleanup`

清理旧条目。

```bash
spider-aggregation cleanup [OPTIONS]
```

| 选项 | 描述 |
|------|------|
| `--days INTEGER` | 删除 N 天前的条目（默认：30）|

**示例**：
```bash
# 清理 90 天前的条目
spider-aggregation cleanup --days 90
```

---

## 核心模块 API

### FeedFetcher

RSS/Atom 订阅源抓取器。

```python
from spider_aggregation.core import FeedFetcher, FetchResult, create_fetcher

# 创建抓取器
fetcher = create_fetcher(session=None)

# 或
from sqlalchemy.orm import Session
fetcher = FeedFetcher(session=session)
```

#### 方法

##### `fetch_feed(feed: FeedModel) -> FetchResult`

抓取订阅源内容。

**参数**：
- `feed` - FeedModel 实例

**返回**：`FetchResult` 对象

**示例**：
```python
from spider_aggregation.models import FeedModel

feed = FeedModel(
    id=1,
    url="https://blog.cloudflare.com/zh-cn/rss",
    name="Cloudflare Blog",
    enabled=True,
    fetch_interval_minutes=60
)

result = fetcher.fetch_feed(feed)

if result.success:
    print(f"抓取了 {result.entries_count} 个条目")
    for entry in result.entries:
        print(f"  - {entry.get('title')}")
else:
    print(f"抓取失败: {result.error}")
```

**FetchResult 属性**：
```python
@dataclass
class FetchResult:
    success: bool                          # 是否成功
    feed_id: int                           # 订阅源 ID
    feed_url: str                          # 订阅源 URL
    entries_count: int                     # 条目数量
    entries: list                          # 条目列表（feedparser 格式）
    error: Optional[str]                   # 错误信息
    fetch_time_seconds: float              # 抓取耗时
    http_status: Optional[int]             # HTTP 状态码
    etag: Optional[str]                    # ETag
    last_modified: Optional[str]           # Last-Modified
    feed_data: Optional[dict]              # 原始 feedparser 数据
    feed_info: Optional[dict]              # 订阅源元数据
```

---

### ContentParser

内容解析器，用于标准化和清洗订阅源条目。

```python
from spider_aggregation.core import ContentParser, create_parser

# 创建解析器
parser = create_parser()

# 或自定义
parser = ContentParser(
    max_content_length=5000,
    strip_html=True,
    preserve_paragraphs=True
)
```

#### 方法

##### `parse_entry(raw_entry: dict) -> dict`

解析单个条目。

**参数**：
- `raw_entry` - feedparser 返回的原始条目

**返回**：标准化的条目字典

**示例**：
```python
import feedparser

parsed = feedparser.parse("https://example.com/feed.xml")
for raw_entry in parsed.entries:
    entry = parser.parse_entry(raw_entry)

    print(f"标题: {entry['title']}")
    print(f"链接: {entry['link']}")
    print(f"作者: {entry.get('author')}")
    print(f"语言: {entry.get('language')}")
    print(f"阅读时间: {entry.get('reading_time_seconds')}秒")
```

**返回字典结构**：
```python
{
    "title": str,                    # 标题
    "link": str,                     # 链接
    "author": Optional[str],         # 作者
    "summary": Optional[str],        # 摘要
    "content": Optional[str],        # 内容
    "published_at": Optional[datetime],  # 发布时间
    "updated_at": Optional[datetime],    # 更新时间
    "tags": Optional[list[str]],     # 标签
    "language": Optional[str],       # 语言代码
    "reading_time_seconds": Optional[int]  # 阅读时间（秒）
}
```

---

### Deduplicator

去重器，用于检测重复内容。

```python
from spider_aggregation.core import (
    Deduplicator,
    DedupStrategy,
    create_deduplicator
)

# 创建去重器
dedup = create_deduplicator(session=session, strategy="medium")

# 或
dedup = Deduplicator(
    session=session,
    strategy=DedupStrategy.MEDIUM
)
```

#### 去重策略

```python
class DedupStrategy(Enum):
    STRICT = "strict"    # link_hash OR (title_hash AND content_hash)
    MEDIUM = "medium"    # link_hash OR title_hash
    RELAXED = "relaxed"  # title_hash OR content_hash (similarity > 85%)
```

#### 方法

##### `check_duplicate(entry: dict, feed_id: int) -> DedupResult`

检查条目是否重复。

**参数**：
- `entry` - 解析后的条目字典
- `feed_id` - 订阅源 ID

**返回**：`DedupResult` 对象

**示例**：
```python
result = dedup.check_duplicate(
    {"title": "Example", "link": "https://example.com/article"},
    feed_id=1
)

if result.is_duplicate:
    print(f"重复: {result.reason}")
else:
    print("新条目")
```

**DedupResult 属性**：
```python
@dataclass
class DedupResult:
    is_duplicate: bool           # 是否重复
    reason: Optional[str]        # 原因
    matched_by: Optional[str]    # 匹配方式 (link/title/content)
    existing_entry: Optional[EntryModel]  # 已存在的条目
```

##### `compute_hashes(entry: dict) -> dict`

计算条目的哈希值。

**参数**：
- `entry` - 解析后的条目字典

**返回**：哈希值字典

**示例**：
```python
hashes = dedup.compute_hashes(entry)
# {
#     "title_hash": "...",
#     "link_hash": "...",
#     "content_hash": "..."
# }
```

---

### FeedScheduler

任务调度器，用于管理定时抓取。

```python
from spider_aggregation.core import FeedScheduler, create_scheduler

# 创建调度器
scheduler = create_scheduler(
    session=None,
    max_workers=3,
    db_manager=db_manager
)
```

#### 方法

##### `start() -> None`

启动调度器。

**示例**：
```python
scheduler.start()
```

##### `stop(wait: bool = True) -> None`

停止调度器。

**参数**：
- `wait` - 是否等待正在运行的任务完成

**示例**：
```python
scheduler.stop(wait=True)
```

##### `add_feed_job(feed_id: int, interval_minutes: int = 60, job_id: Optional[str] = None) -> str`

添加单个订阅源的定时任务。

**参数**：
- `feed_id` - 订阅源 ID
- `interval_minutes` - 抓取间隔（分钟）
- `job_id` - 自定义任务 ID（可选）

**返回**：任务 ID

**示例**：
```python
job_id = scheduler.add_feed_job(feed_id=1, interval_minutes=30)
# 返回: "feed_1"
```

##### `remove_job(job_id: str) -> bool`

移除任务。

**参数**：
- `job_id` - 任务 ID

**返回**：是否成功移除

**示例**：
```python
success = scheduler.remove_job("feed_1")
```

##### `pause_job(job_id: str) -> bool`

暂停任务。

**示例**：
```python
success = scheduler.pause_job("feed_1")
```

##### `resume_job(job_id: str) -> bool`

恢复任务。

**示例**：
```python
success = scheduler.resume_job("feed_1")
```

##### `get_job_status(job_id: str) -> Optional[JobStatus]`

获取任务状态。

**返回**：`JobStatus` 对象或 None

**示例**：
```python
status = scheduler.get_job_status("feed_1")
if status:
    print(f"下次运行: {status.next_run_time}")
    print(f"是否活跃: {status.is_active}")
```

##### `get_stats() -> SchedulerStats`

获取调度器统计信息。

**返回**：`SchedulerStats` 对象

**示例**：
```python
stats = scheduler.get_stats()
print(f"总任务数: {stats.total_jobs}")
print(f"活跃任务: {stats.active_jobs}")
print(f"运行时间: {stats.uptime_seconds}秒")
```

---

## 存储层 API

### DatabaseManager

数据库管理器。

```python
from spider_aggregation.storage.database import DatabaseManager

# 创建管理器
manager = DatabaseManager(":memory:")  # 内存数据库
manager = DatabaseManager("data/spider_aggregation.db")  # 文件数据库

# 初始化数据库
manager.init_db()

# 获取会话
with manager.session() as session:
    # 使用 session
    pass

# 关闭
manager.close()
```

### FeedRepository

订阅源仓储。

```python
from spider_aggregation.storage.repositories.feed_repo import FeedRepository
from spider_aggregation.models.feed import FeedCreate

repo = FeedRepository(session)
```

#### 方法

| 方法 | 描述 |
|------|------|
| `create(data: FeedCreate) -> FeedModel` | 创建订阅源 |
| `get_by_id(feed_id: int) -> Optional[FeedModel]` | 按 ID 获取 |
| `get_by_url(url: str) -> Optional[FeedModel]` | 按 URL 获取 |
| `list(enabled_only: bool = False) -> list[FeedModel]` | 列出订阅源 |
| `update(feed: FeedModel) -> FeedModel` | 更新订阅源 |
| `delete(feed: FeedModel) -> None` | 删除订阅源 |
| `get_feeds_to_fetch(max_feeds: int = 50) -> list[FeedModel]` | 获取待抓取订阅源 |
| `enable_feed(feed: FeedModel) -> FeedModel` | 启用订阅源 |
| `disable_feed(feed: FeedModel, reason: Optional[str] = None) -> FeedModel` | 禁用订阅源 |
| `update_fetch_info(feed, ...) -> FeedModel` | 更新抓取信息 |

### EntryRepository

条目仓储。

```python
from spider_aggregation.storage.repositories.entry_repo import EntryRepository
from spider_aggregation.models.entry import EntryCreate

repo = EntryRepository(session)
```

#### 方法

| 方法 | 描述 |
|------|------|
| `create(data: EntryCreate) -> EntryModel` | 创建条目 |
| `get_by_id(entry_id: int) -> Optional[EntryModel]` | 按 ID 获取 |
| `get_by_link_hash(link_hash: str, feed_id: Optional[int] = None) -> Optional[EntryModel]` | 按 link_hash 获取 |
| `get_by_title_hash(title_hash: str, feed_id: Optional[int] = None) -> Optional[EntryModel]` | 按 title_hash 获取 |
| `list(feed_id: Optional[int] = None, limit: int = 100, offset: int = 0) -> list[EntryModel]` | 列出条目 |
| `search(query: str, feed_id: Optional[int] = None, limit: int = 100) -> list[EntryModel]` | 搜索条目 |
| `get_recent(days: int = 7, limit: int = 100) -> list[EntryModel]` | 获取最近条目 |
| `count(feed_id: Optional[int] = None) -> int` | 统计条目数量 |
| `cleanup_old_entries(days: int = 90) -> int` | 清理旧条目 |
| `get_stats(feed_id: Optional[int] = None) -> dict` | 获取统计信息 |

---

## 数据模型

### FeedModel (ORM)

```python
class FeedModel(Base):
    id: int                          # 主键
    url: str                         # URL（唯一）
    name: str                        # 名称
    description: Optional[str]        # 描述
    enabled: bool                    # 是否启用
    fetch_interval_minutes: int       # 抓取间隔（分钟）
    etag: Optional[str]              # ETag
    last_modified: Optional[str]      # Last-Modified
    last_fetched_at: Optional[datetime]  # 最后抓取时间
    last_error: Optional[str]         # 最后错误
    last_error_at: Optional[datetime]    # 最后错误时间
    fetch_error_count: int            # 错误次数
    created_at: datetime              # 创建时间
    updated_at: datetime              # 更新时间
```

### EntryModel (ORM)

```python
class EntryModel(Base):
    id: int                          # 主键
    feed_id: int                     # 订阅源 ID（外键）
    title: str                       # 标题
    link: str                        # 链接
    author: Optional[str]            # 作者
    summary: Optional[str]           # 摘要
    content: Optional[str]           # 内容
    published_at: Optional[datetime] # 发布时间
    fetched_at: datetime             # 抓取时间
    title_hash: str                  # 标题哈希
    link_hash: str                   # 链接哈希（唯一）
    content_hash: Optional[str]      # 内容哈希
    tags: Optional[str]              # 标签（JSON 字符串）
    language: Optional[str]          # 语言代码
    reading_time_seconds: Optional[int]  # 阅读时间（秒）
```

### FeedCreate (Pydantic)

```python
class FeedCreate(BaseModel):
    url: str
    name: Optional[str] = None
    description: Optional[str] = None
    enabled: bool = True
    fetch_interval_minutes: int = 60
```

### EntryCreate (Pydantic)

```python
class EntryCreate(BaseModel):
    feed_id: int
    title: str
    link: str
    author: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    published_at: Optional[datetime] = None
    tags: Optional[list[str]] = None
    language: Optional[str] = None
    reading_time_seconds: Optional[int] = None
    title_hash: str
    link_hash: str
    content_hash: Optional[str] = None
```
