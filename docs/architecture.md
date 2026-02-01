# MindWeaver - 架构设计文档

## 项目概述

MindWeaver 是一个个人知识/研究动态监测工具，用于自动化抓取、解析、去重和存储 RSS/Atom 订阅源内容。

### 核心目标

- 自动化监测指定领域的信息动态
- 智能去重避免重复内容
- 结构化存储便于检索
- 可扩展的调度系统

## 系统架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLI Layer                               │
│  (Click + Rich)                                                │
│  - init, add-feed, list-feeds, fetch, start                    │
└────────────────────────┬───────────────────────────────────────┘
                         │
┌────────────────────────▼───────────────────────────────────────┐
│                      Scheduler Layer                            │
│  (APScheduler)                                                 │
│  - 定时任务调度                                                 │
│  - 并发抓取控制                                                 │
└────────────────────────┬───────────────────────────────────────┘
                         │
┌────────────────────────▼───────────────────────────────────────┐
│                      Core Logic Layer                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐     │
│  │ Fetcher  │ │  Parser  │ │Deduplicator│ │ FeedMetadata │     │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────┘     │
└────────────────────────┬───────────────────────────────────────┘
                         │
┌────────────────────────▼───────────────────────────────────────┐
│                    Storage Layer                               │
│  ┌──────────┐ ┌──────────┐                                     │
│  │   DB     │ │Repositories│                                   │
│  │(SQLite)  │ │(ORM/CRUD) │                                    │
│  └──────────┘ └──────────┘                                     │
└─────────────────────────────────────────────────────────────────┘
```

## 核心模块设计

### 1. CLI 模块 (`cli.py`)

**职责**：提供命令行界面

**主要命令**：
- `init` - 初始化数据库
- `add-feed` - 添加订阅源
- `list-feeds` - 列出订阅源
- `fetch` - 手动抓取
- `start` - 启动调度器
- `list-entries` - 列出条目
- `enable-feed` - 启用/禁用订阅源
- `delete-feed` - 删除订阅源
- `cleanup` - 清理旧条目

### 2. 抓取器模块 (`fetcher.py`)

**职责**：从 RSS/Atom 订阅源抓取内容

**核心类**：`FeedFetcher`

**主要功能**：
```python
class FeedFetcher:
    def fetch_feed(feed: FeedModel) -> FetchResult
    # - HTTP 请求处理
    # - ETag/Last-Modified 支持（304 Not Modified）
    # - 自动重试（最多 4 次）
    # - 超时处理（30 秒）
    # - 错误计数和自动禁用
```

**重试策略**：
- 4xx 错误：不重试
- 5xx/网络错误：重试最多 4 次
- 超时：重试最多 4 次
- 连续 10 次失败后自动禁用订阅源

### 3. 解析器模块 (`parser.py`)

**职责**：标准化和清洗订阅源内容

**核心类**：
- `ContentParser` - 条目内容解析
- `FeedMetadataParser` - 订阅源元数据解析

**ContentParser 处理流程**：
```
Raw Entry → 字段标准化 → HTML 清理 → 日期解析 → 标签提取 → 语言检测 → 阅读时间计算
```

**支持的日期格式**：
- ISO 8601 (带/不带时区)
- RFC 2822
- 常见格式 (YYYY-MM-DD, DD/MM/YYYY, etc.)
- 带月份名称的格式

**语言检测**：
- 中文（CJK 统一汉字）
- 日文（平假名/片假名）
- 英文（拉丁字母）
- 其他欧洲语言

### 4. 去重模块 (`deduplicator.py`)

**职责**：检测和过滤重复内容

**去重策略**：

| 策略 | 描述 | 检测方式 |
|------|------|----------|
| STRICT | 严格模式 | link_hash 或 title_hash + content_hash |
| MEDIUM | 中等模式（默认） | link_hash 或 title_hash |
| RELAXED | 宽松模式 | title_hash 或 content_hash (相似度>85%) |

**哈希算法**：
- `link_hash` - MD5(link小写)
- `title_hash` - MD5(title小写并标准化)
- `content_hash` - SHA256(content前500字符，标准化)
- `similarity_hash` - MinHash 算法用于内容相似度检测

### 5. 调度器模块 (`scheduler.py`)

**职责**：管理定时抓取任务

**核心类**：`FeedScheduler`

**主要功能**：
```python
class FeedScheduler:
    def start() -> None
    def stop(wait: bool) -> None
    def add_feed_job(feed_id, interval_minutes) -> str
    def add_multiple_feeds_job(feed_ids) -> str
    def pause_job(job_id) -> bool
    def resume_job(job_id) -> bool
    def remove_job(job_id) -> bool
    def get_job_status(job_id) -> JobStatus
    def get_stats() -> SchedulerStats
```

**调度特性**：
- 基于 APScheduler
- 线程池执行（可配置并发数）
- 事件监听（任务执行/错误）
- 统计追踪（执行次数、成功率）
- 每个任务独立数据库会话

### 6. 存储层 (`storage/`)

**数据库设计**：

```sql
-- Feeds 表
CREATE TABLE feeds (
    id INTEGER PRIMARY KEY,
    url TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    enabled BOOLEAN DEFAULT TRUE,
    fetch_interval_minutes INTEGER DEFAULT 60,
    etag TEXT,
    last_modified TEXT,
    last_fetched_at TIMESTAMP,
    last_error TEXT,
    last_error_at TIMESTAMP,
    fetch_error_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Entries 表
CREATE TABLE entries (
    id INTEGER PRIMARY KEY,
    feed_id INTEGER NOT NULL REFERENCES feeds(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    link TEXT NOT NULL,
    author TEXT,
    summary TEXT,
    content TEXT,
    published_at TIMESTAMP,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    title_hash TEXT NOT NULL,
    link_hash TEXT UNIQUE NOT NULL,
    content_hash TEXT,
    tags TEXT,  -- JSON string
    language TEXT(10),
    reading_time_seconds INTEGER
);

CREATE INDEX idx_entries_feed_id ON entries(feed_id);
CREATE INDEX idx_entries_published_at ON entries(published_at DESC);
CREATE INDEX idx_entries_title_hash ON entries(title_hash);
CREATE INDEX idx_entries_content_hash ON entries(content_hash);
```

**仓储模式**：
- `FeedRepository` - 订阅源 CRUD
- `EntryRepository` - 条目 CRUD

## 数据流

### 抓取流程

```
1. Scheduler 触发任务
   ↓
2. FeedFetcher.fetch_feed()
   ├── HTTP GET with ETag/Last-Modified
   ├── 304 Not Modified → 跳过
   └── 200 OK → 继续
   ↓
3. FeedParser.parse()
   ├── 提取 entries
   └── 提取 feed metadata
   ↓
4. For each entry:
   ├── ContentParser.parse_entry()
   │   ├── 标准化字段
   │   ├── 清理 HTML
   │   ├── 解析日期
   │   ├── 检测语言
   │   └── 计算阅读时间
   ↓
   ├── Deduplicator.check_duplicate()
   │   ├── 计算哈希
   │   ├── 查询数据库
   │   └── 返回是否重复
   ↓
   └── EntryRepository.create() (如果不重复)
       └── 存储到数据库
```

## 配置管理

### 配置结构 (`config.py`)

```python
class DatabaseConfig:
    path: str = "data/spider_aggregation.db"

class FetcherConfig:
    timeout_seconds: int = 30
    max_retries: int = 3
    retry_delay_seconds: int = 5
    max_content_length: int = 10000
    user_agent: str = "Mind-Aggregation/0.1.0"

class SchedulerConfig:
    min_interval_minutes: int = 15
    timezone: str = "UTC"

class DeduplicatorConfig:
    strategy: DedupStrategy = DedupStrategy.MEDIUM
    similarity_threshold: float = 0.85
```

### 配置优先级

1. 环境变量 (`MIND_***`)
2. 配置文件 (`config/config.yaml`)
3. 默认值

## 日志系统

### 日志配置

```python
# logger.py
from loguru import logger

logger.add(
    "logs/spider_{time}.log",
    rotation="10 MB",
    retention="30 days",
    level="INFO"
)
```

### 日志级别

- `DEBUG` - 详细调试信息
- `INFO` - 常规操作（抓取、解析、存储）
- `WARNING` - 可恢复的错误（重试、跳过）
- `ERROR` - 严重错误（失败、禁用）

## 性能考虑

### 数据库优化

1. **索引**：link_hash 唯一索引，快速去重查询
2. **CASCADE 删除**：删除订阅源自动删除关联条目
3. **连接池**：SQLite 使用会话管理

### 并发控制

- 调度器使用线程池（默认 3 个工作线程）
- 每个任务独立数据库会话
- 避免会话冲突

### 内存管理

- 内容长度限制（默认 10000 字符）
- 按需加载（分页查询）
- 及时关闭会话

## 扩展性设计

### 添加新的订阅源类型

```python
# 1. 继承 FeedFetcher
class CustomFetcher(FeedFetcher):
    def fetch_feed(self, feed):
        # 自定义抓取逻辑
        pass

# 2. 注册到 CLI
@click.command()
def add-custom-feed(url):
    # 使用 CustomFetcher
    pass
```

### 自定义解析器

```python
# 1. 继承 ContentParser
class CustomParser(ContentParser):
    def parse_entry(self, raw_entry):
        # 自定义解析逻辑
        pass

# 2. 使用
parser = CustomParser(strip_html=False)
```

### 自定义去重策略

```python
class CustomDeduplicator(Deduplicator):
    def check_duplicate(self, entry, feed_id):
        # 自定义去重逻辑
        pass
```

## 安全考虑

1. **SQL 注入防护**：使用 SQLAlchemy ORM
2. **XSS 防护**：HTML 清理（BeautifulSoup）
3. **资源限制**：超时、重试次数、内容长度
4. **敏感信息**：不记录 API 密钥、密码

## 错误处理策略

### 可恢复错误
- 网络超时 → 重试
- 临时性 HTTP 错误 → 重试
- 解析失败 → 跳过条目，记录警告

### 不可恢复错误
- 404 Not Found → 不重试，记录错误
- 订阅源格式错误 → 禁用订阅源
- 数据库错误 → 终止程序

### 错误恢复
- 自动重试（最多 4 次）
- 错误计数 → 达到阈值自动禁用
- 手动启用 → 重置错误计数

## 监控与维护

### 统计指标

```python
class SchedulerStats:
    total_jobs: int
    active_jobs: int
    total_executions: int
    successful_executions: int
    failed_executions: int
    uptime_seconds: float
```

### 健康检查

- 数据库连接状态
- 调度器运行状态
- 最近抓取成功率
- 订阅源错误率

### 维护任务

1. **定期清理**：`cleanup --days 90`
2. **错误检查**：查看高错误率订阅源
3. **性能监控**：查看抓取延迟统计
4. **存储管理**：日志轮转、数据库备份

## 未来扩展

### Phase 2 - 增强功能
- AI 摘要生成
- 关键词过滤
- Web UI

### Phase 3 - 个性化
- 用户行为追踪
- 兴趣模型
- 智能推荐

### Phase 4 - 高级功能
- 多源采集（网页、API、社交媒体）
- 事件聚类
- 趋势分析
