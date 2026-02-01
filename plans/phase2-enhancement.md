# 阶段 2 - 基础增强与内容加工

## 阶段目标

在 MVP 基础上加入结构化解析、NLP 内容加工和可配置过滤能力，打造一个智能化的内容聚合系统。

---

## 核心功能

### 1. 全文抓取与摘要生成
- 从订阅源提取的链接抓取完整正文
- 使用 NLP 模型生成智能摘要
- 提取关键词和主题标签

### 2. 可配置过滤系统
- 用户自定义关键词规则
- 标签过滤与分类
- 正则表达式匹配
- 排除规则配置

### 3. 字段标准化增强
- 统一不同来源的日期格式
- 来源网站规范化
- 内容长度标准化
- 作者信息清洗

### 4. Web 界面
- 订阅源管理界面
- 条目浏览与搜索
- 过滤规则配置
- 统计仪表板

---

## 技术选型

| 功能 | 技术方案 |
|------|----------|
| 全文抓取 | httpx + BeautifulSoup4 / trafilatura |
| 摘要生成 | transformers (bart-large-cnn) 或 spaCy |
| 关键词提取 | spaCy / RAKE / YAKE |
| Web 框架 | FastAPI + Vue 3 / React |
| 向量数据库 | sqlite-vec / Chroma (轻量级) |

---

## 任务拆解

### PHASE 2.1: 全文抓取模块 (4-5h)

| ID | 任务 | 验收标准 |
|----|------|----------|
| 2.1.1 | 设计内容提取器接口 | 抽象基类定义 |
| 2.1.2 | 实现 trafilatura 封装 | 支持主流新闻网站 |
| 2.1.3 | 实现备用提取器 (BeautifulSoup) | trafilatura 失败时降级 |
| 2.1.4 | 添加缓存机制 | 避免重复抓取同一URL |
| 2.1.5 | 处理反爬策略 | User-Agent 轮换、延迟控制 |
| 2.1.6 | 编写内容提取测试 | 覆盖 10 个常见网站 |

### PHASE 2.2: NLP 内容分析 (5-6h)

| ID | 任务 | 验收标准 |
|----|------|----------|
| 2.2.1 | 选择并配置 NLP 模型 | spaCy 或 transformers |
| 2.2.2 | 实现摘要生成器 | 生成 50-200 字摘要 |
| 2.2.3 | 实现关键词提取器 | 提取 Top 5-10 关键词 |
| 2.2.4 | 实现语言检测 | 支持中英文混合内容 |
| 2.2.5 | 添加批处理优化 | 提高处理速度 |
| 2.2.6 | 编写 NLP 单元测试 | 验证输出质量 |

**数据模型扩展：**
```python
# Entry 模型新增字段
- full_content: Text          # 完整正文
- summary: Text(500)          # AI 生成摘要
- keywords: JSON             # 关键词列表
- language: String(10)       # 语言代码
- reading_time: Integer      # 预估阅读时间(秒)
```

### PHASE 2.3: 过滤规则系统 (4-5h)

| ID | 任务 | 验收标准 |
|----|------|----------|
| 2.3.1 | 设计过滤规则数据模型 | 支持多种规则类型 |
| 2.3.2 | 实现关键词匹配引擎 | OR/AND 逻辑 |
| 2.3.3 | 实现正则表达式过滤 | 支持复杂模式 |
| 2.3.4 | 实现标签过滤 | 包含/排除逻辑 |
| 2.3.5 | 实现规则优先级 | 多规则协同 |
| 2.3.6 | 规则性能优化 | 高效匹配算法 |

**过滤规则模型：**
```python
class FilterRule:
    - id, name, enabled
    - rule_type: keyword | regex | tag | language
    - match_type: include | exclude
    - pattern: String       # 关键词/正则/标签
    - priority: Integer     # 优先级
    - created_at, updated_at
```

### PHASE 2.4: 去重系统增强 (2-3h)

| ID | 任务 | 验收标准 |
|----|------|----------|
| 2.4.1 | 实现标题相似度检测 | 使用 Levenshtein/序列匹配 |
| 2.4.2 | 实现摘要指纹比对 | MinHash/LSH 算法 |
| 2.4.3 | 添加近似去重配置 | 可配置相似度阈值 |
| 2.4.4 | 去重历史记录 | 保留去重决策日志 |

### PHASE 2.5: Web API 后端 (5-6h)

| ID | 任务 | 验收标准 |
|----|------|----------|
| 2.5.1 | 设计 RESTful API | 遵循 OpenAPI 规范 |
| 2.5.2 | 实现 Feed CRUD API | 完整的订阅源管理 |
| 2.5.3 | 实现 Entry 查询 API | 支持分页、过滤、排序 |
| 2.5.4 | 实现过滤规则 API | 规则的增删改查 |
| 2.5.5 | 添加统计 API | 抓取统计、趋势数据 |
| 2.5.6 | API 认证与限流 | 简单 Token 机制 |

**API 端点设计：**
```
GET    /api/feeds              # 列出订阅源
POST   /api/feeds              # 添加订阅源
PUT    /api/feeds/{id}         # 更新订阅源
DELETE /api/feeds/{id}         # 删除订阅源

GET    /api/entries            # 列出条目（支持过滤）
GET    /api/entries/{id}       # 获取条目详情

POST   /api/filters            # 创建过滤规则
GET    /api/filters            # 列出过滤规则
DELETE /api/filters/{id}       # 删除规则

GET    /api/stats/overview     # 概览统计
GET    /api/stats/trends       # 趋势数据
```

### PHASE 2.6: Web 前端 (8-10h)

| ID | 任务 | 验收标准 |
|----|------|----------|
| 2.6.1 | 搭建 Vue 3 项目 | Vite + TypeScript |
| 2.6.2 | 设计 UI 组件库 | 统一风格 |
| 2.6.3 | 实现订阅源管理页面 | 添加、编辑、删除 |
| 2.6.4 | 实现条目列表页面 | 无限滚动、快速过滤 |
| 2.6.5 | 实现条目详情页面 | 展开、收藏、标记 |
| 2.6.6 | 实现过滤规则配置 | 可视化规则编辑器 |
| 2.6.7 | 实现统计仪表板 | 图表展示 |
| 2.6.8 | 响应式设计 | 移动端适配 |

### PHASE 2.7: 配置系统增强 (2-3h)

| ID | 任务 | 验收标准 |
|----|------|----------|
| 2.7.1 | 添加 NLP 配置项 | 模型选择、参数调整 |
| 2.7.2 | 添加抓取配置 | 全文抓取开关、缓存策略 |
| 2.7.3 | 添加过滤配置 | 默认规则、严格度 |
| 2.7.4 | 配置热更新 | 无需重启 |

### PHASE 2.8: 测试与优化 (3-4h)

| ID | 任务 | 验收标准 |
|----|------|----------|
| 2.8.1 | 端到端测试 | 完整流程验证 |
| 2.8.2 | 性能测试 | 全文抓取 < 10秒/页面 |
| 2.8.3 | NLP 性能优化 | 摘要生成 < 2秒/条目 |
| 2.8.4 | 并发测试 | 支持 20 并发抓取 |

### PHASE 2.9: 文档与部署 (2-3h)

| ID | 任务 | 验收标准 |
|----|------|----------|
| 2.9.1 | API 文档 | Swagger/OpenAPI |
| 2.9.2 | 用户手册 | 功能使用说明 |
| 2.9.3 | 部署脚本 | Docker 化 |
| 2.9.4 | 环境配置文档 | 依赖安装指南 |

---

## 验收标准

### 功能性
- ✅ 能自动抓取并提取完整正文
- ✅ 生成的摘要准确、可读
- ✅ 关键词提取相关度 ≥ 70%
- ✅ 支持至少 5 种过滤规则类型
- ✅ Web 界面完整可用

### 性能
- ✅ 全文抓取延迟 ≤ 10 秒/页面
- ✅ 摘要生成延迟 ≤ 2 秒/条目
- ✅ Web 页面加载 ≤ 2 秒
- ✅ 支持至少 100 条目/页显示

### 代码质量
- ✅ 单元测试覆盖率 ≥ 75%
- ✅ API 文档完整
- ✅ 前端组件测试覆盖 ≥ 60%

---

## 时间估算

| 阶段 | 预计时间 |
|------|----------|
| 2.1 全文抓取 | 4-5h |
| 2.2 NLP 分析 | 5-6h |
| 2.3 过滤系统 | 4-5h |
| 2.4 去重增强 | 2-3h |
| 2.5 Web API | 5-6h |
| 2.6 Web 前端 | 8-10h |
| 2.7 配置增强 | 2-3h |
| 2.8 测试优化 | 3-4h |
| 2.9 文档部署 | 2-3h |
| **总计** | **35-45h** |

**建议开发周期**: 按每天 2-3 小时开发，预计 **3-4 周** 完成

---

## 关键依赖

```toml
[project.dependencies]
"trafilatura>=1.6.0",       # 全文提取
"beautifulsoup4>=4.12.0",   # HTML 解析备用
"spacy>=3.7.0",             # NLP 基础
"transformers>=4.35.0",     # 摘要生成（可选）
"fastapi>=0.109.0",         # Web API
"uvicorn>=0.27.0",          # ASGI 服务器
"jinja2>=3.1.0",            # 模板引擎
"aiofiles>=23.0.0",         # 异步文件操作
```

---

## 目录结构扩展

```
spider-aggregation/
├── src/spider_aggregation/
│   ├── nlp/                    # 🆕 NLP 模块
│   │   ├── __init__.py
│   │   ├── summarizer.py       # 摘要生成
│   │   ├── keyword_extractor.py # 关键词提取
│   │   └── language_detector.py # 语言检测
│   │
│   ├── extractors/             # 🆕 内容提取
│   │   ├── __init__.py
│   │   ├── base.py            # 抽象基类
│   │   ├── trafilatura_extractor.py
│   │   └── bs4_extractor.py
│   │
│   ├── filters/                # 🆕 过滤系统
│   │   ├── __init__.py
│   │   ├── engine.py          # 过滤引擎
│   │   ├── keyword_filter.py
│   │   ├── regex_filter.py
│   │   └── tag_filter.py
│   │
│   └── api/                    # 🆕 Web API
│       ├── __init__.py
│       ├── main.py            # FastAPI 应用
│       ├── routes/            # 路由模块
│       │   ├── feeds.py
│       │   ├── entries.py
│       │   ├── filters.py
│       │   └── stats.py
│       └── schemas/           # Pydantic 模型
│           ├── feed.py
│           ├── entry.py
│           └── filter.py
│
├── web/                        # 🆕 前端项目
│   ├── package.json
│   ├── vite.config.ts
│   ├── src/
│   │   ├── components/        # Vue 组件
│   │   ├── views/             # 页面
│   │   ├── stores/            # 状态管理
│   │   └── styles/            # 样式
│   └── dist/                  # 构建输出
│
└── docker/                     # 🆕 Docker 配置
    ├── Dockerfile
    └── docker-compose.yml
```
