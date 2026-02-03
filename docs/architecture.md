# MindWeaver - 架构设计文档

## 项目概述

MindWeaver 是一个个人知识/研究动态监测工具，用于自动化抓取、解析、去重、过滤和存储 RSS/Atom 订阅源内容。

### 核心目标

- 自动化监测指定领域的信息动态
- 智能去重避免重复内容
- 内容增强（提取、关键词、摘要）
- 规则过滤自定义信息流
- 分类组织管理订阅源
- Web 界面可视化操作

## 系统架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Web UI Layer                                │
│  (Flask + Jinja2)                                                  │
│  - Dashboard, Feeds, Entries, Categories, Filter Rules, Settings   │
│  - REST API endpoints                                              │
└─────────────────────────┬───────────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────────┐
│                      Service Layer (Facade)                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌──────────────┐  │
│  │FetcherSvc   │ │ParserSvc    │ │Deduplicator │ │SchedulerSvc  │  │
│  │Service      │ │Service      │ │Service      │ │Service       │  │
│  └─────────────┘ └─────────────┘ └─────────────┘ └──────────────┘  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                   │
│  │ContentSvc   │ │FilterSvc    │ │KeywordSvc   │ │SummarizerSvc │  │
│  └─────────────┘ └─────────────┘ └─────────────┘ └──────────────┘  │
└─────────────────────────┬───────────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────────┐
│                      Core Logic Layer                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────────┐  │
│  │ Fetcher  │ │  Parser  │ │Deduplicator│ │Scheduler (APScheduler)│  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────────┘  │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────────┐   │
│  │ContentFetcher│ │ FilterEngine │ │KeywordExtractor          │   │
│  └──────────────┘ └──────────────┘ └──────────────────────────┘   │
│  ┌──────────────────────────┐                                      │
│  │Summarizer (Extractive/AI)│                                      │
│  └──────────────────────────┘                                      │
└─────────────────────────┬───────────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────────┐
│                     Repository Layer                                │
│  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐    │
│  │BaseRepository    │ │FeedRepository    │ │EntryRepository   │    │
│  │(abstract base)   │ │                  │ │                  │    │
│  └──────────────────┘ └──────────────────┘ └──────────────────┘    │
│  ┌──────────────────┐ ┌──────────────────┐                          │
│  │CategoryRepository│ │FilterRuleRepo    │                          │
│  │                  │ │                  │                          │
│  └──────────────────┘ └──────────────────┘                          │
└─────────────────────────┬───────────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────────┐
│                    Storage Layer (Multi-DB)                         │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────┐                  │
│  │  SQLite     │ │ PostgreSQL   │ │    MySQL     │                  │
│  │  (default)  │ │  (optional)  │ │  (optional)  │                  │
│  └─────────────┘ └──────────────┘ └──────────────┘                  │
└─────────────────────────────────────────────────────────────────────┘
```

## 核心模块设计

### 1. Web UI Layer (`web/`)

**职责**：提供 Web 界面和 REST API

**主要组件**：

| 组件 | 功能 |
|------|------|
| `app.py` | Flask 应用工厂，注册 Blueprints |
| `blueprints/feeds.py` | 订阅源 API (`/api/feeds`) |
| `blueprints/categories.py` | 分类 API (`/api/categories`) |
| `blueprints/entries.py` | 条目 API (`/api/entries`) |
| `blueprints/filter_rules.py` | 过滤规则 API (`/api/filter-rules`) |
| `blueprints/scheduler.py` | 调度器 API (`/api/scheduler`) |
| `blueprints/system.py` | 系统 API (`/api/system`, `/api/stats`) |
| `templates/` | Jinja2 HTML 模板 |
| `static/` | CSS/JS 静态资源 |

**设计模式**：Blueprint 模块化架构，每个功能模块独立 Blueprint

---

### 2. Service Layer (`core/services/`)

**职责**：提供统一的服务入口（Facade 模式），Web 层只能通过 Service Layer 访问核心模块

**核心服务**：

```python
from spider_aggregation.core.services import (
    FetcherService,      # 抓取服务
    ParserService,       # 解析服务
    DeduplicatorService, # 去重服务
    SchedulerService,    # 调度服务
    FilterService,       # 过滤服务
    ContentService,      # 内容提取服务
    KeywordService,      # 关键词服务
    SummarizerService,   # 摘要服务
)
```

**使用示例**：

```python
# Correct - 使用 Service Facade
from spider_aggregation.core.services import FetcherService

fetcher = FetcherService(db_manager)
result = fetcher.fetch_feed(feed_id)

# Wrong - 直接导入核心模块（禁止）
from spider_aggregation.core.fetcher import FeedFetcher  # VIOLATION
```

**设计模式**：Facade 模式，封装复杂子系统，提供简化接口

---

### 3. 抓取器模块 (`core/fetcher.py`)

**职责**：从 RSS/Atom 订阅源抓取内容

**核心类**：`FeedFetcher`

**主要功能**：
```python
class FeedFetcher:
    def fetch_feed(feed: FeedModel) -> FetchResult
    # - HTTP 请求处理
    # - ETag/Last-Modified 支持（304 Not Modified）
    # - 自动重试（最多 3 次）
    # - 超时处理（30 秒）
    # - 错误计数和自动禁用
```

**重试策略**：
- 4xx 错误：不重试
- 5xx/网络错误：重试最多 3 次
- 超时：重试最多 3 次
- 连续 10 次失败后自动禁用订阅源

---

### 4. 解析器模块 (`core/parser.py`)

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

---

### 5. 去重模块 (`core/deduplicator.py`)

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

---

### 6. 调度器模块 (`core/scheduler.py`)

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
- 线程池执行（可配置并发数，默认 3 个）
- 事件监听（任务执行/错误）
- 统计追踪（执行次数、成功率）
- 每个任务独立数据库会话

---

### 7. 内容提取模块 (`core/content_fetcher.py`)

**职责**：提取完整文章内容（从 URL 抓取原文）

**核心类**：`ContentFetcher`

**主要功能**：
```python
class ContentFetcher:
    def fetch_content(url: str) -> ContentResult
    # - 使用 Trafilatura 提取正文
    # - 清理导航/广告等噪声
    # - 返回结构化内容（标题、正文、作者、日期）
```

**配置**：
- 超时：30 秒
- 最大内容长度：500,000 字符（可配置）

---

### 8. 过滤引擎模块 (`core/filter_engine.py`)

**职责**：基于规则过滤条目

**核心类**：`FilterEngine`

**规则类型**：

| 类型 | 描述 | 示例 |
|------|------|------|
| `keyword` | 关键词匹配 | "Python", "AI" |
| `regex` | 正则表达式匹配 | `r"\d{4}-\d{2}-\d{2}"` |
| `tag` | 标签匹配 | "technology", "news" |
| `language` | 语言代码匹配 | "zh", "en" |

**匹配类型**：
- `include` - 包含匹配（条目必须匹配规则）
- `exclude` - 排除匹配（条目匹配则被过滤）

**优先级**：高优先级规则优先执行

---

### 9. 关键词提取模块 (`core/keyword_extractor.py`)

**职责**：自动提取文章关键词

**核心类**：`KeywordExtractor`

**主要功能**：
```python
class KeywordExtractor:
    def extract(text: str, max_keywords: int = 10) -> list[str]
    # - 中文：使用 jieba 分词 + TF-IDF
    # - 英文：使用 NLTK 分词 + 词频统计
    # - 过滤停用词
    # - 返回关键词列表
```

---

### 10. 摘要生成模块 (`core/summarizer.py`)

**职责**：生成文章摘要

**核心类**：`Summarizer`

**摘要方法**：

| 方法 | 描述 |
|------|------|
| `extractive` | 抽取式摘要（基于句子重要性） |
| `ai` | AI 生成摘要（Claude/OpenAI API，可选） |

**配置**：
- 最大摘要长度：10,000 字符（可配置）

---

### 11. 存储层 (`storage/`)

**数据库设计**：

```sql
-- Feeds 表
CREATE TABLE feeds (
    id INTEGER PRIMARY KEY,
    url TEXT UNIQUE NOT NULL,
    name TEXT,
    description TEXT,
    enabled BOOLEAN DEFAULT TRUE,
    fetch_interval_minutes INTEGER DEFAULT 60,
    max_entries_per_fetch INTEGER DEFAULT 100,
    fetch_only_recent BOOLEAN DEFAULT FALSE,
    etag TEXT,
    last_modified TEXT,
    last_fetched_at TIMESTAMP,
    last_error TEXT,
    last_error_at TIMESTAMP,
    fetch_error_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Categories 表
CREATE TABLE categories (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    color TEXT(7),  -- Hex color code
    icon TEXT(50),  -- Icon name/class
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Feed-Categories 关联表（多对多）
CREATE TABLE feed_categories (
    feed_id INTEGER REFERENCES feeds(id) ON DELETE CASCADE,
    category_id INTEGER REFERENCES categories(id) ON DELETE CASCADE,
    PRIMARY KEY (feed_id, category_id)
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

-- Filter Rules 表
CREATE TABLE filter_rules (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    rule_type TEXT NOT NULL,  -- keyword, regex, tag, language
    match_type TEXT NOT NULL, -- include, exclude
    pattern TEXT NOT NULL,
    priority INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_entries_feed_id ON entries(feed_id);
CREATE INDEX idx_entries_published_at ON entries(published_at DESC);
CREATE INDEX idx_entries_title_hash ON entries(title_hash);
CREATE INDEX idx_entries_content_hash ON entries(content_hash);
CREATE INDEX idx_feed_categories_feed_id ON feed_categories(feed_id);
CREATE INDEX idx_feed_categories_category_id ON feed_categories(category_id);
CREATE INDEX idx_filter_rules_enabled_priority ON filter_rules(enabled, priority);
```

**仓储模式**：

| Repository | 功能 |
|------------|------|
| `BaseRepository` | 通用 CRUD 基类 |
| `FeedRepository` | 订阅源 CRUD，分类关联 |
| `EntryRepository` | 条目 CRUD，搜索、过滤、分页 |
| `CategoryRepository` | 分类 CRUD，订阅源管理 |
| `FilterRuleRepository` | 过滤规则 CRUD，优先级查询 |

**多数据库支持**：

| 数据库 | 驱动 | 环境变量 |
|--------|------|----------|
| SQLite | 内置 | `MIND_DB_TYPE=sqlite` |
| PostgreSQL | psycopg2-binary | `MIND_DB_TYPE=postgresql` |
| MySQL | pymysql | `MIND_DB_TYPE=mysql` |

---

## 数据流

### 抓取流程

```
1. Scheduler 触发任务 (APScheduler)
   ↓
2. SchedulerService 调用 FetcherService
   ↓
3. FetcherService.fetch_feed()
   ├── HTTP GET with ETag/Last-Modified
   ├── 304 Not Modified → 跳过
   └── 200 OK → 继续
   ↓
4. ParserService.parse_entry()
   ├── 标准化字段
   ├── 清理 HTML
   ├── 解析日期
   ├── 检测语言
   └── 计算阅读时间
   ↓
5. DeduplicatorService.check_duplicate()
   ├── 计算哈希
   ├── 查询数据库
   └── 返回是否重复
   ↓
6. FilterService.apply_filter() (如果启用)
   ├── 加载过滤规则
   ├── 应用 include/exclude 规则
   └── 返回 FilterResult
   ↓
7. EntryRepository.create() (如果不重复且通过过滤)
   └── 存储到数据库
   ↓
8. 可选：ContentService.fetch_content()
   └── 提取完整文章内容
   ↓
9. 可选：KeywordService.extract_keywords()
   └── 自动提取关键词
   ↓
10. 可选：SummarizerService.generate_summary()
    └── 生成摘要
```

---

## 设计模式

| 模式 | 应用场景 | 实现位置 |
|------|----------|----------|
| **Facade 模式** | Service Layer 提供统一入口 | `core/services/` |
| **Repository 模式** | 数据访问层抽象 | `storage/repositories/` |
| **Factory 模式** | 组件创建 | `core/factories.py` |
| **Strategy 模式** | 去重策略 (strict/medium/relaxed) | `core/deduplicator.py` |
| **Blueprint 模式** | Flask 路由模块化 | `web/blueprints/` |
| **Mixin 模式** | 代码复用 | `storage/repositories/mixins.py` |

---

## 配置管理

### 配置结构 (`config.py`)

```python
class DatabaseConfig:
    type: str = "sqlite"  # sqlite, postgresql, mysql
    path: str = "data/spider_aggregation.db"
    host: Optional[str] = None
    port: Optional[int] = None
    name: Optional[str] = None
    user: Optional[str] = None
    password: Optional[str] = None

class FetcherConfig:
    timeout_seconds: int = 30
    max_retries: int = 3
    retry_delay_seconds: int = 5
    max_content_length: int = 100000
    user_agent: str = "MindWeaver/0.4.0"

class SchedulerConfig:
    min_interval_minutes: int = 15
    timezone: str = "Asia/Shanghai"
    max_workers: int = 3

class DeduplicatorConfig:
    strategy: DedupStrategy = DedupStrategy.MEDIUM
    similarity_threshold: float = 0.85

class ContentFetcherConfig:
    enabled: bool = True
    timeout_seconds: int = 30
    max_content_length: int = 500000

class KeywordExtractorConfig:
    enabled: bool = True
    max_keywords: int = 10

class SummarizerConfig:
    enabled: bool = True
    method: str = "extractive"  # extractive or ai
    max_length: int = 10000
    ai_provider: Optional[str] = None  # anthropic, openai
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
```

### 配置优先级

1. 环境变量 (`MIND_***`)
2. 配置文件 (`config/config.yaml`)
3. 默认值

---

## 日志系统

### 日志配置

```python
# logger.py
from spider_aggregation.logger import get_logger

logger = get_logger(__name__)

logger.add(
    "logs/mind-weaver.log",
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

---

## 性能考虑

### 数据库优化

1. **索引**：
   - `link_hash` 唯一索引，快速去重查询
   - `ix_feeds_enabled_last_fetched` 复合索引
   - `ix_filter_rules_enabled_priority` 复合索引

2. **CASCADE 删除**：删除订阅源自动删除关联条目

3. **连接池**：SQLAlchemy 连接池管理

### 并发控制

- 调度器使用线程池（默认 3 个工作线程，可配置）
- 每个任务独立数据库会话
- 避免会话冲突

### 内存管理

- 内容长度限制（默认 100,000 字符）
- 按需加载（分页查询）
- 及时关闭会话

---

## 扩展性设计

### 添加新的订阅源类型

```python
# 1. 继承 FeedFetcher
class CustomFetcher(FeedFetcher):
    def fetch_feed(self, feed):
        # 自定义抓取逻辑
        pass

# 2. 创建对应的 Service
class CustomFetcherService:
    def __init__(self, db_manager):
        self.fetcher = CustomFetcher()

# 3. 在 Web Blueprint 中使用
@bp.route("/api/custom-fetch", methods=["POST"])
def custom_fetch():
    service = CustomFetcherService(db_manager)
    return service.fetch(...)
```

### 自定义解析器

```python
# 1. 继承 ContentParser
class CustomParser(ContentParser):
    def parse_entry(self, raw_entry):
        # 自定义解析逻辑
        pass

# 2. 创建对应的 Service
class CustomParserService(ParserService):
    def __init__(self):
        self.parser = CustomParser(strip_html=False)

# 3. 使用
parser = CustomParserService()
parsed = parser.parse_entry(raw_entry)
```

### 自定义去重策略

```python
class CustomDeduplicator(Deduplicator):
    def check_duplicate(self, entry, feed_id):
        # 自定义去重逻辑
        pass

# 创建对应的 Service
class CustomDeduplicatorService(DeduplicatorService):
    def __init__(self, db_manager):
        self.deduplicator = CustomDeduplicator()
```

---

## 安全考虑

1. **SQL 注入防护**：使用 SQLAlchemy ORM
2. **XSS 防护**：HTML 清理（BeautifulSoup）
3. **资源限制**：超时、重试次数、内容长度
4. **敏感信息**：不记录 API 密钥、密码
5. **CSRF 防护**：Flask-WTF CSRF 保护

---

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

- 自动重试（最多 3 次）
- 错误计数 → 达到阈值（10次）自动禁用
- 手动启用 → 重置错误计数

---

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

1. **定期清理**：Settings 页面手动清理旧条目
2. **错误检查**：Dashboard 查看高错误率订阅源
3. **性能监控**：查看抓取延迟统计
4. **存储管理**：日志轮转、数据库备份

---

## 路线图

### ✅ Phase 1 - MVP（已完成）

- RSS/Atom 抓取
- 内容解析和标准化
- 多层次去重
- 定时任务调度

### ✅ Phase 2 - 内容增强（已完成）

- 完整文章内容提取 (ContentFetcher)
- 关键词提取 (KeywordExtractor)
- 过滤规则引擎 (FilterEngine)
- AI 摘要（可选）

### ✅ Phase 3 - 组织管理（已完成）

- 订阅源分类管理 (Category)
- 分类 CRUD 操作
- 颜色和图标自定义
- 个性化订阅源设置（条目限制、仅获取最新）

### ✅ Phase 4 - 架构优化（已完成）

- Service Layer (Facade 模式)
- 多数据库支持（SQLite/PostgreSQL/MySQL）
- Repository 模式强化（BaseRepository）
- Blueprint 模块化架构
- Web-only 界面
- 数据库迁移工具（Alembic）

### 📋 Phase 5 - 智能推荐（计划中）

- 用户行为追踪
- 兴趣模型构建
- 智能推荐引擎
- 个性化信息流

### 🚀 Phase 6 - 高级功能（长期）

- 全文搜索（Elasticsearch/Whoosh）
- 多源采集（社交媒体、API、网页监控）
- 事件聚类与热点发现
- 趋势分析与预测
- 知识图谱
- 自动化报告生成
- API 认证与多用户支持
- 移动端适配
