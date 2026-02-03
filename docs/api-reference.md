# MindWeaver - API 参考文档

## 目录

- [REST API](#rest-api)
  - [通用响应格式](#通用响应格式)
  - [订阅源管理](#订阅源管理)
  - [分类管理](#分类管理)
  - [条目管理](#条目管理)
  - [过滤规则管理](#过滤规则管理)
  - [调度器管理](#调度器管理)
  - [系统接口](#系统接口)
- [核心模块 API](#核心模块-api)
- [存储层 API](#存储层-api)
- [数据模型](#数据模型)

---

## REST API

MindWeaver 提供完整的 REST API 用于管理 RSS/Atom 订阅源、条目、分类和过滤规则。

**基础 URL**: `http://localhost:8000/api`

**Content-Type**: `application/json`

---

### 通用响应格式

所有 API 响应遵循统一的格式：

```json
{
  "success": true|false,
  "data": { ... },           // 响应数据（成功时）
  "message": "操作成功",      // 提示信息
  "error": "错误信息"         // 错误信息（失败时）
}
```

**HTTP 状态码**：
- `200` - 成功
- `400` - 请求参数错误
- `404` - 资源不存在
- `500` - 服务器内部错误

---

### 订阅源管理

**基础路径**: `/api/feeds`

#### 获取订阅源列表

```http
GET /api/feeds?page=1&page_size=20
```

**查询参数**：

| 参数 | 类型 | 描述 | 默认值 |
|------|------|------|--------|
| `page` | int | 页码 | 1 |
| `page_size` | int | 每页数量 | 20 |

**响应示例**：

```json
{
  "success": true,
  "data": {
    "feeds": [
      {
        "id": 1,
        "url": "https://blog.cloudflare.com/zh-cn/rss",
        "name": "Cloudflare Blog",
        "description": "Cloudflare 官方博客",
        "enabled": true,
        "fetch_interval_minutes": 60,
        "max_entries_per_fetch": 100,
        "fetch_only_recent": false,
        "created_at": "2026-02-01T08:30:00",
        "updated_at": "2026-02-01T08:30:00",
        "last_fetched_at": "2026-02-01T09:00:00",
        "fetch_error_count": 0,
        "categories": []
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 20
  }
}
```

---

#### 创建订阅源

```http
POST /api/feeds
```

**请求体**：

```json
{
  "url": "https://example.com/feed.xml",
  "name": "My Feed",
  "description": "Description",
  "enabled": true,
  "fetch_interval_minutes": 60,
  "max_entries_per_fetch": 100,
  "fetch_only_recent": false
}
```

**必填字段**：`url`

---

#### 获取订阅源详情

```http
GET /api/feeds/{feed_id}
```

---

#### 更新订阅源

```http
PUT /api/feeds/{feed_id}
```

**请求体**：

```json
{
  "name": "Updated Name",
  "description": "Updated description",
  "enabled": true,
  "fetch_interval_minutes": 120,
  "max_entries_per_fetch": 50,
  "fetch_only_recent": true
}
```

---

#### 删除订阅源

```http
DELETE /api/feeds/{feed_id}
```

---

#### 手动抓取订阅源

```http
POST /api/feeds/{feed_id}/fetch
```

**响应示例**：

```json
{
  "success": true,
  "data": {
    "entries_created": 5,
    "feed": { ... }
  },
  "message": "成功获取 5 条新内容"
}
```

---

#### 获取订阅源的分类

```http
GET /api/feeds/{feed_id}/categories
```

---

#### 设置订阅源的分类

```http
PUT /api/feeds/{feed_id}/categories
```

**请求体**：

```json
{
  "category_ids": [1, 2, 3]
}
```

---

#### 添加单个分类到订阅源

```http
POST /api/feeds/{feed_id}/categories/{category_id}
```

---

#### 从订阅源移除分类

```http
DELETE /api/feeds/{feed_id}/categories/{category_id}
```

---

### 分类管理

**基础路径**: `/api/categories`

#### 获取分类列表

```http
GET /api/categories?enabled_only=true
```

**查询参数**：

| 参数 | 类型 | 描述 | 默认值 |
|------|------|------|--------|
| `enabled_only` | bool | 仅返回启用的分类 | false |

---

#### 创建分类

```http
POST /api/categories
```

**请求体**：

```json
{
  "name": "Technology",
  "description": "Technology news and articles",
  "color": "#3B82F6",
  "icon": "cpu",
  "enabled": true
}
```

**必填字段**：`name`

---

#### 获取分类详情

```http
GET /api/categories/{category_id}
```

---

#### 更新分类

```http
PUT /api/categories/{category_id}
```

**请求体**：

```json
{
  "name": "Tech",
  "description": "Updated description",
  "color": "#10B981",
  "icon": "chip",
  "enabled": true
}
```

---

#### 删除分类

```http
DELETE /api/categories/{category_id}
```

---

#### 获取分类下的订阅源

```http
GET /api/categories/{category_id}/feeds
```

**响应示例**：

```json
{
  "success": true,
  "data": {
    "feeds": [...],
    "total": 10
  }
}
```

---

#### 获取分类统计

```http
GET /api/categories/stats
```

**响应示例**：

```json
{
  "success": true,
  "data": {
    "total": 5,
    "enabled": 4
  }
}
```

---

#### 获取分类条目统计

```http
GET /api/categories/{category_id}/entries/stats
```

---

### 条目管理

**基础路径**: `/api/entries`

#### 获取条目列表

```http
GET /api/entries?page=1&page_size=20&feed_id=1
```

**查询参数**：

| 参数 | 类型 | 描述 |
|------|------|------|
| `page` | int | 页码 |
| `page_size` | int | 每页数量 |
| `feed_id` | int | 按订阅源过滤 |
| `search` | string | 搜索关键词 |

---

#### 获取条目详情

```http
GET /api/entries/{entry_id}
```

**响应示例**：

```json
{
  "success": true,
  "data": {
    "id": 1,
    "feed_id": 1,
    "title": "Article Title",
    "link": "https://example.com/article",
    "author": "Author Name",
    "summary": "Article summary...",
    "content": "Full article content...",
    "published_at": "2026-02-01T08:00:00",
    "fetched_at": "2026-02-01T09:00:00",
    "tags": ["technology", "ai"],
    "language": "en",
    "reading_time_seconds": 300
  }
}
```

---

#### 删除条目

```http
DELETE /api/entries/{entry_id}
```

---

#### 批量删除条目

```http
POST /api/entries/batch/delete
```

**请求体**：

```json
{
  "entry_ids": [1, 2, 3]
}
```

---

#### 批量提取内容

```http
POST /api/entries/batch/fetch-content
```

**请求体**：

```json
{
  "entry_ids": [1, 2, 3]
}
```

**响应示例**：

```json
{
  "success": true,
  "data": {
    "success": 3,
    "failed": 0
  },
  "message": "成功获取 3 条条目的完整内容"
}
```

---

#### 批量提取关键词

```http
POST /api/entries/batch/extract-keywords
```

**请求体**：

```json
{
  "entry_ids": [1, 2, 3]
}
```

---

#### 批量生成摘要

```http
POST /api/entries/batch/summarize
```

**请求体**：

```json
{
  "entry_ids": [1, 2, 3]
}
```

---

#### 按分类获取条目

```http
GET /api/entries/by-category/{category_id}?page=1&page_size=20
```

---

#### 按分类名称获取条目

```http
GET /api/entries/by-category-name/{category_name}?page=1&page_size=20
```

---

#### 在分类内搜索

```http
GET /api/entries/search-by-category/{category_id}?q=keyword&page=1
```

**查询参数**：

| 参数 | 类型 | 描述 | 必填 |
|------|------|------|------|
| `q` | string | 搜索关键词 | 是 |
| `page` | int | 页码 | 否 |
| `page_size` | int | 每页数量 | 否 |

---

#### 获取分类条目统计

```http
GET /api/entries/by-category/{category_id}/stats
```

---

### 过滤规则管理

**基础路径**: `/api/filter-rules`

#### 获取过滤规则列表

```http
GET /api/filter-rules
```

---

#### 创建过滤规则

```http
POST /api/filter-rules
```

**请求体**：

```json
{
  "name": "Python Articles",
  "enabled": true,
  "rule_type": "keyword",
  "match_type": "include",
  "pattern": "python",
  "priority": 10
}
```

**规则类型**：`keyword`, `regex`, `tag`, `language`

**匹配类型**：`include`, `exclude`

---

#### 获取过滤规则详情

```http
GET /api/filter-rules/{rule_id}
```

---

#### 更新过滤规则

```http
PUT /api/filter-rules/{rule_id}
```

---

#### 删除过滤规则

```http
DELETE /api/filter-rules/{rule_id}
```

---

#### 启用/禁用过滤规则

```http
POST /api/filter-rules/{rule_id}/toggle
```

---

### 调度器管理

**基础路径**: `/api/scheduler`

#### 获取调度器状态

```http
GET /api/scheduler/status
```

**响应示例**：

```json
{
  "success": true,
  "data": {
    "is_running": true,
    "total_feeds_count": 10,
    "enabled_feeds_count": 8,
    "jobs": [
      {
        "id": "feed_1",
        "name": "feed_1",
        "next_run_time": "2026-02-01T10:00:00+00:00"
      }
    ]
  }
}
```

---

#### 启动调度器

```http
POST /api/scheduler/start
```

---

#### 停止调度器

```http
POST /api/scheduler/stop
```

---

#### 立即抓取所有订阅源

```http
POST /api/scheduler/fetch-all
```

**响应示例**：

```json
{
  "success": true,
  "data": {
    "feeds_fetched": 10,
    "total_entries_created": 25,
    "results": [
      {
        "feed_id": 1,
        "feed_name": "Cloudflare Blog",
        "success": true,
        "entries_created": 5,
        "http_status": 200
      }
    ]
  },
  "message": "成功获取 10 个订阅源，共创建 25 条新内容"
}
```

---

### 系统接口

**基础路径**: `/api`

#### 获取系统统计

```http
GET /api/stats
```

**响应示例**：

```json
{
  "total_entries": 1000,
  "total_feeds": 10,
  "enabled_feeds": 8,
  "total_rules": 5,
  "total_categories": 3,
  "language_counts": {
    "zh": 500,
    "en": 450,
    "ja": 50
  },
  "most_recent": "2026-02-01T09:00:00"
}
```

---

#### 获取最近活动

```http
GET /api/dashboard/activity?limit=10
```

---

#### 获取订阅源健康状态

```http
GET /api/dashboard/feed-health
```

**响应示例**：

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Cloudflare Blog",
      "url": "https://blog.cloudflare.com/zh-cn/rss",
      "enabled": true,
      "error_count": 0,
      "last_fetched": "2026-02-01T09:00:00",
      "has_error": false
    }
  ]
}
```

---

#### 清理旧条目

```http
POST /api/system/cleanup
```

**请求体**：

```json
{
  "days": 90
}
```

---

#### 导出条目

```http
GET /api/system/export/entries?feed_id=1&limit=1000
```

**响应**：JSON 文件下载

---

#### 导出订阅源

```http
GET /api/system/export/feeds
```

**响应**：JSON 文件下载

---

## 核心模块 API

### Service Layer (Facade)

Web 层必须通过 Service Layer 访问核心模块。

```python
from spider_aggregation.core.services import (
    FetcherService,
    ParserService,
    DeduplicatorService,
    SchedulerService,
    FilterService,
    ContentService,
    KeywordService,
    SummarizerService,
)
```

---

### FetcherService

```python
from spider_aggregation.core.services import FetcherService

# 创建服务
fetcher = FetcherService(session=session)

# 抓取订阅源
result = fetcher.fetch_feed(
    url="https://example.com/feed.xml",
    feed_id=1,
    etag=None,
    last_modified=None,
    max_entries=100,
    recent_only=False,
)
```

**FetchResult 属性**：

```python
@dataclass
class FetchResult:
    success: bool
    feed_id: int
    feed_url: str
    entries_count: int
    entries: list
    error: Optional[str]
    fetch_time_seconds: float
    http_status: Optional[int]
    etag: Optional[str]
    last_modified: Optional[str]
```

---

### ParserService

```python
from spider_aggregation.core.services import ParserService

parser = ParserService()

# 解析条目
parsed = parser.parse_entry(raw_entry, feed_id=1)
```

**返回字典结构**：

```python
{
    "title": str,
    "link": str,
    "author": Optional[str],
    "summary": Optional[str],
    "content": Optional[str],
    "published_at": Optional[datetime],
    "updated_at": Optional[datetime],
    "tags": Optional[list[str]],
    "language": Optional[str],
    "reading_time_seconds": Optional[int],
    "title_hash": str,
    "link_hash": str,
    "content_hash": Optional[str],
}
```

---

### DeduplicatorService

```python
from spider_aggregation.core.services import DeduplicatorService

# 创建服务（需要 session）
deduplicator = DeduplicatorService(session=session)

# 检查重复
result = deduplicator.check_duplicate(
    parsed_entry,
    entry_repo,
    feed_id=1
)

if result.is_duplicate:
    print(f"重复: {result.reason}")
```

**DedupResult 属性**：

```python
@dataclass
class DedupResult:
    is_duplicate: bool
    reason: Optional[str]
    matched_by: Optional[str]  # link/title/content
    existing_entry: Optional[EntryModel]
```

---

### FilterService

```python
from spider_aggregation.core.services import FilterService

filter_service = FilterService()

# 应用过滤规则
result = filter_service.apply(parsed_entry, filter_rule_repo)

if not result.allowed:
    print(f"被规则过滤: {result.excluded_by}")
```

**FilterResult 属性**：

```python
@dataclass
class FilterResult:
    passed: bool       # 是否通过
    allowed: bool      # 别名
    matched_rules: list[str]
    excluded_by: Optional[str]
```

---

### ContentService

```python
from spider_aggregation.core.services import ContentService

content_service = ContentService()

# 提取完整内容
result = content_service.fetch_content("https://example.com/article")

if result.success:
    print(result.content)
```

---

### KeywordService

```python
from spider_aggregation.core.services import KeywordService

keyword_service = KeywordService()

# 提取关键词
keywords = keyword_service.extract(
    text="Article content here...",
    max_keywords=10
)
# Returns: ["keyword1", "keyword2", ...]
```

---

### SummarizerService

```python
from spider_aggregation.core.services import SummarizerService

summarizer = SummarizerService()

# 生成摘要
summary = summarizer.summarize(
    text="Long article content...",
    max_length=500
)
```

---

### SchedulerService

```python
from spider_aggregation.core.services import SchedulerService

scheduler = SchedulerService(db_manager=db_manager)

# 启动调度器
scheduler.start()

# 停止调度器
scheduler.stop(wait=True)

# 获取统计
stats = scheduler.get_stats()
```

---

## 存储层 API

### DatabaseManager

```python
from spider_aggregation.storage.database import DatabaseManager

# SQLite
manager = DatabaseManager("data/spider_aggregation.db")

# PostgreSQL
manager = DatabaseManager(
    host="localhost",
    port=5432,
    database="mindweaver",
    username="user",
    password="password",
    dialect="postgresql"
)

# 初始化数据库
manager.init_db()

# 获取会话
with manager.session() as session:
    # 使用 session
    pass

# 关闭
manager.close()
```

---

### FeedRepository

```python
from spider_aggregation.storage.repositories.feed_repo import FeedRepository
from spider_aggregation.models import FeedCreate

repo = FeedRepository(session)

# 创建
feed = repo.create(FeedCreate(url="...", name="..."))

# 查询
feed = repo.get_by_id(1)
feed = repo.get_by_url("https://...")
feeds = repo.list(enabled_only=True, limit=100)

# 更新
feed.name = "New Name"
repo.update(feed)

# 删除
repo.delete(feed)

# 分类管理
repo.add_category(feed, category)
repo.remove_category(feed, category)
repo.set_categories(feed, [1, 2, 3])
categories = repo.get_categories(feed)

# 获取待抓取订阅源
feeds = repo.get_feeds_to_fetch(max_feeds=50)

# 更新抓取信息
repo.update_fetch_info(
    feed,
    last_fetched_at=datetime.utcnow(),
    reset_errors=True,
    etag="...",
    last_modified="..."
)
```

---

### EntryRepository

```python
from spider_aggregation.storage.repositories.entry_repo import EntryRepository
from spider_aggregation.models import EntryCreate

repo = EntryRepository(session)

# 创建
entry = repo.create(EntryCreate(...))

# 查询
entry = repo.get_by_id(1)
entry = repo.get_by_link_hash("...")
entries = repo.list(feed_id=1, limit=100)

# 搜索
entries = repo.search("keyword", feed_id=1)

# 按分类查询
entries = repo.list_by_category(1, limit=20)

# 统计
stats = repo.get_stats()
count = repo.count(feed_id=1)

# 清理旧条目
deleted = repo.cleanup_old_entries(days=90)

# 批量删除
deleted = repo.delete_by_ids([1, 2, 3])
```

---

### CategoryRepository

```python
from spider_aggregation.storage.repositories.category_repo import CategoryRepository

repo = CategoryRepository(session)

# 创建（自定义参数）
category = repo.create(
    name="Technology",
    description="...",
    color="#3B82F6",
    icon="cpu",
    enabled=True
)

# 查询
category = repo.get_by_id(1)
category = repo.get_by_name("Technology")

# 更新（自定义参数）
repo.update(category, name="Tech", color="#10B981")

# 获取分类下的订阅源
feeds = repo.get_feeds_by_category(1)
count = repo.get_feed_count_by_category(1)

# 统计
total = repo.count()
enabled = repo.count(enabled_only=True)
```

---

### FilterRuleRepository

```python
from spider_aggregation.storage.repositories.filter_rule_repo import FilterRuleRepository
from spider_aggregation.models import FilterRuleCreate

repo = FilterRuleRepository(session)

# 创建
rule = repo.create(FilterRuleCreate(...))

# 查询
rule = repo.get_by_id(1)
rule = repo.get_by_name("Rule Name")
rules = repo.list(enabled_only=True)

# 获取启用的规则（按优先级排序）
rules = repo.get_enabled_rules()

# 统计
count = repo.count()
```

---

## 数据模型

### FeedModel (ORM)

```python
class FeedModel(Base):
    id: int                          # 主键
    url: str                         # URL（唯一）
    name: Optional[str]              # 名称
    description: Optional[str]       # 描述
    enabled: bool                    # 是否启用
    fetch_interval_minutes: int       # 抓取间隔（分钟）
    max_entries_per_fetch: int        # 每次最大条目数
    fetch_only_recent: bool          # 仅获取最近30天
    etag: Optional[str]              # ETag
    last_modified: Optional[str]      # Last-Modified
    last_fetched_at: Optional[datetime]  # 最后抓取时间
    last_error: Optional[str]         # 最后错误
    last_error_at: Optional[datetime]    # 最后错误时间
    fetch_error_count: int            # 错误次数
    created_at: datetime              # 创建时间
    updated_at: datetime              # 更新时间

    # 关系
    entries: list[EntryModel]
    categories: list[CategoryModel]
```

---

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

    # 关系
    feed: FeedModel
```

---

### CategoryModel (ORM)

```python
class CategoryModel(Base):
    id: int                          # 主键
    name: str                        # 名称（唯一）
    description: Optional[str]       # 描述
    color: Optional[str]             # 颜色（Hex）
    icon: Optional[str]              # 图标
    enabled: bool                    # 是否启用
    created_at: datetime             # 创建时间
    updated_at: datetime             # 更新时间

    # 关系
    feeds: list[FeedModel]
```

---

### FilterRuleModel (ORM)

```python
class FilterRuleModel(Base):
    id: int                          # 主键
    name: str                        # 规则名称
    enabled: bool                    # 是否启用
    rule_type: str                   # 规则类型: keyword/regex/tag/language
    match_type: str                  # 匹配类型: include/exclude
    pattern: str                     # 匹配模式
    priority: int                    # 优先级
    created_at: datetime             # 创建时间
    updated_at: datetime             # 更新时间
```

---

### Pydantic Schemas

```python
from spider_aggregation.models import (
    FeedCreate, FeedUpdate, FeedResponse,
    EntryCreate, EntryUpdate, EntryResponse,
    CategoryCreate, CategoryUpdate, CategoryResponse,
    FilterRuleCreate, FilterRuleUpdate, FilterRuleResponse,
)
```

**FeedCreate**：

```python
class FeedCreate(BaseModel):
    url: str
    name: Optional[str] = None
    description: Optional[str] = None
    enabled: bool = True
    fetch_interval_minutes: int = 60
    max_entries_per_fetch: int = 100
    fetch_only_recent: bool = False
```

**CategoryCreate**：

```python
class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    color: Optional[str] = None  # Hex color
    icon: Optional[str] = None
    enabled: bool = True
```

**FilterRuleCreate**：

```python
class FilterRuleCreate(BaseModel):
    name: str
    enabled: bool = True
    rule_type: str  # keyword, regex, tag, language
    match_type: str  # include, exclude
    pattern: str
    priority: int = 0
```
