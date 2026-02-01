# Mind-Aggregation 项目任务拆解方案

## 项目概述

这是一个**个人知识或研究动态监测工具**，目标构建一个持续自动化监测指定领域动态的系统。

### 当前状态（约 5% 完成度）

**已有资源：**
- ✅ README.md - 完整的 4 阶段技术方案文档
- ✅ main.py - 基础 RSS 解析示例代码（使用 feedparser）
- ✅ Python 3.14 + UV 包管理器环境
- ✅ Git 仓库已初始化

**缺失组件：**
- ❌ 模块化目录结构
- ❌ 依赖声明（pyproject.toml 的 dependencies 为空）
- ❌ 数据持久化层
- ❌ 配置管理系统
- ❌ 日志系统
- ❌ 定时任务调度器
- ❌ 去重机制
- ❌ 测试框架
- ❌ 命令行界面

---

## 推荐的目录结构

```
mind-weaver/
├── README.md                          # 项目说明（已有）
├── pyproject.toml                     # 项目配置（需更新）
├── uv.lock                            # 依赖锁定（已有）
├── .gitignore                         # Git忽略（需扩展）
├── .python-version                    # Python版本（已有）
│
├── docs/                              # 📁 文档目录
│   ├── architecture.md                # 架构设计文档
│   ├── api-reference.md               # API参考文档
│   ├── development-guide.md           # 开发指南
│   └── deployment-guide.md            # 部署指南
│
├── plans/                             # 📁 任务拆解方案
│   ├── mvp-implementation.md          # MVP阶段实施计划
│   ├── phase2-enhancement.md          # 阶段2增强计划
│   ├── phase3-personalization.md      # 阶段3个性化计划
│   └── phase4-advanced.md             # 阶段4高级功能计划
│
├── src/                               # 📁 源代码目录
│   └── spider_aggregation/            # 主包
│       ├── __init__.py
│       ├── cli.py                     # 命令行入口
│       ├── config.py                  # 配置管理
│       ├── logger.py                  # 日志配置
│       │
│       ├── core/                      # 核心业务逻辑
│       │   ├── __init__.py
│       │   ├── fetcher.py             # RSS/Atom 抓取器
│       │   ├── parser.py              # 内容解析器
│       │   ├── deduplicator.py        # 去重逻辑
│       │   └── scheduler.py           # 任务调度器
│       │
│       ├── models/                    # 数据模型
│       │   ├── __init__.py
│       │   ├── feed.py                # 订阅源模型
│       │   ├── entry.py               # 条目模型
│       │   └── filter_rule.py         # 过滤规则模型
│       │
│       ├── storage/                   # 存储层
│       │   ├── __init__.py
│       │   ├── database.py            # 数据库连接
│       │   └── repositories/          # 仓储模式
│       │       ├── __init__.py
│       │       ├── feed_repo.py       # 订阅源仓储
│       │       └── entry_repo.py      # 条目仓储
│       │
│       └── utils/                     # 工具函数
│           ├── __init__.py
│           ├── hash_utils.py          # 哈希工具
│           ├── date_utils.py          # 日期工具
│           └── http_utils.py          # HTTP工具
│
├── config/                            # 📁 配置文件目录
│   ├── config.yaml                    # 主配置文件
│   ├── feeds.example.yaml             # 订阅源配置示例
│   └── filters.example.yaml           # 过滤规则示例
│
├── tests/                             # 📁 测试目录
│   ├── conftest.py                    # pytest配置
│   ├── unit/                          # 单元测试
│   └── fixtures/                      # 测试数据
│
├── scripts/                           # 📁 脚本目录
│   ├── init_db.py                     # 数据库初始化
│   └── seed_feeds.py                  # 种子数据
│
└── data/                              # 📁 数据目录
    ├── spider_aggregation.db          # SQLite数据库
    └── logs/                          # 日志文件
```

---

## 依赖更新（pyproject.toml）

```toml
[project]
name = "mind-weaver"
version = "0.1.0"
description = "Personal knowledge/research dynamic monitoring tool"
readme = "README.md"
requires-python = ">=3.14"
dependencies = [
    "feedparser>=6.0.10",      # RSS/Atom 解析
    "httpx>=0.27.0",           # HTTP 客户端
    "apscheduler>=3.10.4",     # 定时任务
    "sqlalchemy>=2.0.0",       # 数据库 ORM
    "pydantic>=2.6.0",         # 数据验证
    "pydantic-settings>=2.1.0",
    "pyyaml>=6.0.1",           # YAML 配置
    "loguru>=0.7.2",           # 日志
    "click>=8.1.7",            # CLI 框架
    "rich>=13.7.0",            # 终端美化
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
    "black>=24.0.0",
    "ruff>=0.2.0",
]

[project.scripts]
mind-weaver = "spider_aggregation.cli:main"
```

---

## MVP 阶段任务拆解（10 个子阶段）

### PHASE 1.0: 项目基础搭建 (2-3h)

| ID | 任务 | 验收标准 |
|----|------|----------|
| 1.0.1 | 创建完整目录结构 | 所有目录和 `__init__.py` 创建完成 |
| 1.0.2 | 更新 pyproject.toml 依赖 | `uv sync` 可成功安装所有依赖 |
| 1.0.3 | 更新 .gitignore | 排除 `data/`, `__pycache__`, `.venv/` 等 |
| 1.0.4 | 配置 black/ruff | 代码格式化工具可用 |

### PHASE 1.1: 配置管理系统 (2-3h)

| ID | 任务 | 验收标准 |
|----|------|----------|
| 1.1.1 | 实现 Pydantic 配置模型 | DatabaseConfig, SchedulerConfig, FeedConfig 等 |
| 1.1.2 | 实现配置加载器 | 支持 YAML 配置文件和环境变量 |
| 1.1.3 | 创建默认配置文件 | `config/config.yaml` 和示例文件 |
| 1.1.4 | 编写配置加载单元测试 | 测试覆盖率 ≥ 80% |

### PHASE 1.2: 日志系统 (1-2h)

| ID | 任务 | 验收标准 |
|----|------|----------|
| 1.2.1 | 配置 loguru 日志器 | 输出到文件和终端 |
| 1.2.2 | 实现日志轮转 | 文件大小轮转正常 |
| 1.2.3 | 添加结构化日志 | 包含时间、级别、模块名 |

### PHASE 1.3: 数据模型与数据库层 (3-4h)

| ID | 任务 | 验收标准 |
|----|------|----------|
| 1.3.1 | 设计 SQLAlchemy 模型 | Feed 和 Entry 模型（含去重字段） |
| 1.3.2 | 实现数据库连接管理 | 单例连接池 |
| 1.3.3 | 创建数据库初始化脚本 | `scripts/init_db.py` 可创建所有表 |
| 1.3.4 | 实现 Feed 仓储类 | CRUD 操作正常 |
| 1.3.5 | 实现 Entry 仓储类 | CRUD 操作正常 |
| 1.3.6 | 编写数据库集成测试 | 使用 SQLite 内存数据库 |

**数据模型设计：**
```python
# Feed 模型
- id, url (unique), name, description
- enabled, created_at, updated_at, last_fetched_at
- fetch_error_count

# Entry 模型
- id, feed_id (FK), title, link
- summary, content, author, published_at, fetched_at
- title_hash, link_hash (unique), content_hash (去重用)
```

### PHASE 1.4: RSS/Atom 抓取器 (3-4h)

| ID | 任务 | 验收标准 |
|----|------|----------|
| 1.4.1 | 重构 main.py 为 fetcher 模块 | 代码模块化 |
| 1.4.2 | 实现 FeedParser 封装类 | 统一解析 RSS 和 Atom |
| 1.4.3 | 添加错误处理和重试机制 | 网络错误自动重试 3 次 |
| 1.4.4 | 实现超时处理 | 超时可配置 |
| 1.4.5 | 添加抓取统计 | 记录成功/失败次数 |
| 1.4.6 | 编写 fetcher 单元测试 | Mock 网络请求 |

### PHASE 1.5: 内容解析器 (2-3h)

| ID | 任务 | 验收标准 |
|----|------|----------|
| 1.5.1 | 实现字段标准化 | 统一不同订阅源格式 |
| 1.5.2 | 实现日期解析器 | 支持多种日期格式 |
| 1.5.3 | 实现 HTML 清理 | 去除标签，保留纯文本 |
| 1.5.4 | 添加内容长度限制 | 过长内容可截断 |
| 1.5.5 | 编写 parser 单元测试 | 覆盖边界情况 |

### PHASE 1.6: 去重系统 (2-3h)

| ID | 任务 | 验收标准 |
|----|------|----------|
| 1.6.1 | 实现哈希工具函数 | 支持 MD5/SHA256 |
| 1.6.2 | 实现基于链接的去重 | 相同链接不重复存储 |
| 1.6.3 | 实现基于标题的去重 | 相似标题可检测 |
| 1.6.4 | 实现基于内容的去重 | 内容指纹比对 |
| 1.6.5 | 实现去重策略配置 | 可配置严格度 |
| 1.6.6 | 编写去重单元测试 | 测试各种重复场景 |

### PHASE 1.7: 任务调度器 (2-3h)

| ID | 任务 | 验收标准 |
|----|------|----------|
| 1.7.1 | 实现 APScheduler 集成 | 调度器可启动和停止 |
| 1.7.2 | 实现定时抓取任务 | 按配置间隔执行 |
| 1.7.3 | 添加任务状态监控 | 可查看执行状态 |
| 1.7.4 | 实现任务失败重试 | 失败自动重试 |
| 1.7.5 | 编写调度器集成测试 | 验证调度逻辑 |

### PHASE 1.8: 命令行界面 (2-3h)

| ID | 任务 | 验收标准 |
|----|------|----------|
| 1.8.1 | 设计 CLI 命令结构 | 使用 Click 框架 |
| 1.8.2 | `mind-weaver init` | 初始化数据库 |
| 1.8.3 | `mind-weaver add-feed <url>` | 添加订阅源 |
| 1.8.4 | `mind-weaver list-feeds` | 列出订阅源 |
| 1.8.5 | `mind-weaver fetch` | 手动触发抓取 |
| 1.8.6 | `mind-weaver start` | 启动定时任务 |
| 1.8.7 | `mind-weaver list-entries` | 列出条目，支持过滤 |
| 1.8.8 | 添加 Rich 终端美化 | 表格、进度条 |

### PHASE 1.9: 集成与端到端测试 (2-3h)

| ID | 任务 | 验收标准 |
|----|------|----------|
| 1.9.1 | 集成所有模块 | 端到端流程可运行 |
| 1.9.2 | 编写 E2E 测试场景 | 完整流程自动化 |
| 1.9.3 | 添加 5 个真实订阅源测试 | 验证兼容性 |
| 1.9.4 | 性能测试 | 抓取延迟 < 5秒/源 |
| 1.9.5 | 修复发现的 Bug | 所有测试通过 |

### PHASE 1.10: 文档与部署准备 (2-3h)

| ID | 任务 | 验收标准 |
|----|------|----------|
| 1.10.1 | 编写架构设计文档 | `docs/architecture.md` |
| 1.10.2 | 编写 API 参考文档 | `docs/api-reference.md` |
| 1.10.3 | 编写开发指南 | `docs/development-guide.md` |
| 1.10.4 | 更新 README.md | 包含安装和使用说明 |
| 1.10.5 | 创建部署脚本 | `scripts/deploy.sh` |

---

## MVP 验收标准

### 功能性
- ✅ 稳定从至少 5 个订阅源抓取数据
- ✅ 无重复存储（条目唯一判定）
- ✅ 能输出文本格式的抓取结果清单
- ✅ 带简单错误日志记录

### 性能
- ✅ 抓取延迟不超过 5 秒/条目
- ✅ 支持至少 10 个订阅源并发抓取
- ✅ 系统在抓取失败时具备重试机制

### 代码质量
- ✅ 单元测试覆盖率 ≥ 70%
- ✅ 所有模块有类型注解
- ✅ 代码通过 black 和 ruff 检查

---

## 时间估算

| 阶段 | 预计时间 | 实际时间 |
|------|----------|----------|
| 1.0 基础搭建 | 2-3h | |
| 1.1 配置管理 | 2-3h | |
| 1.2 日志系统 | 1-2h | |
| 1.3 数据库层 | 3-4h | |
| 1.4 抓取器 | 3-4h | |
| 1.5 解析器 | 2-3h | |
| 1.6 去重系统 | 2-3h | |
| 1.7 调度器 | 2-3h | |
| 1.8 CLI | 2-3h | |
| 1.9 集成测试 | 2-3h | |
| 1.10 文档部署 | 2-3h | |
| **总计** | **25-37h** | |

**建议开发周期**: 按每天 2-3 小时开发，预计 **10-15 天** 完成 MVP

---

## 关键文件路径

### 需要创建/修改的核心文件
- `pyproject.toml` - 更新依赖声明
- `src/spider_aggregation/config.py` - 配置管理
- `src/spider_aggregation/core/fetcher.py` - RSS 抓取（从 main.py 重构）
- `src/spider_aggregation/storage/database.py` - 数据库层
- `src/spider_aggregation/cli.py` - 命令行入口
- `config/config.yaml` - 主配置文件

### 方案文档存放位置
- `plans/mvp-implementation.md` - MVP 详细实施计划
- `plans/phase2-enhancement.md` - 阶段 2 计划
- `plans/phase3-personalization.md` - 阶段 3 计划
- `plans/phase4-advanced.md` - 阶段 4 计划

---

## 后续阶段概览

| 阶段 | 主要功能 | 预估周期 |
|------|----------|----------|
| 阶段 1 (MVP) | RSS 抓取、去重、存储、CLI | 10-15 天 |
| 阶段 2 | 摘要生成、关键词过滤、Web UI | 4-6 周 |
| 阶段 3 | 用户行为、兴趣模型、智能推荐 | 6-8 周 |
| 阶段 4 | 多源采集、事件聚类、趋势分析 | 8-10 周 |
