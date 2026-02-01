# 阶段 4 - 高级功能与生态整合

## 阶段目标

打造完整的情报分析平台，包括多源采集、事件聚类、趋势分析和智能洞察。

---

## 核心功能

### 1. 多源采集扩展
- 社交媒体 API 集成（Twitter/X, Reddit, Hacker News）
- 网页监控与变更检测
- 邮件列表订阅
- 播客/视频订阅源
- 学术论文跟踪（arXiv, Google Scholar）

### 2. 事件检测与聚类
- 相似文章聚合
- 事件演化追踪
- 热点事件发现
- 事件摘要生成

### 3. 趋势分析
- 关键词趋势（时间序列）
- 主题热度变化
- 突发事件检测
- 预测性分析

### 4. 智能洞察
- 自动化报告生成
- 关联分析
- 异常检测
- 知识图谱

---

## 技术选型

| 功能 | 技术方案 |
|------|----------|
| 多源采集 | 各平台 API + 通用爬虫 |
| 事件聚类 | HDBSCAN / DBSCAN |
| 趋势分析 | Prophet / statsmodels |
| 时间序列 | pandas + matplotlib/plotly |
| 知识图谱 | NetworkX / Neo4j |
| 报告生成 | Jinja2 + WeasyPrint |
| 数据存储 | PostgreSQL / TimescaleDB |

---

## 任务拆解

### PHASE 4.1: 多源采集架构 (6-8h)

| ID | 任务 | 验收标准 |
|----|------|----------|
| 4.1.1 | 设计统一采集接口 | 抽象数据源 |
| 4.1.2 | 实现 Twitter/X 采集 | API 集成 |
| 4.1.3 | 实现 Reddit 采集 | API + RSS |
| 4.1.4 | 实现 Hacker News 采集 | API |
| 4.1.5 | 实现网页监控 | 变更检测 |
| 4.1.6 | 实现 arXiv 采集 | 学术论文 |
| 4.1.7 | 实现邮件列表解析 | mbox/IMAP |
| 4.1.8 | 采集器插件系统 | 可扩展架构 |

**统一数据源接口：**
```python
class DataSource(ABC):
    @abstractmethod
    async def fetch(self) -> List[RawItem]:
        pass

    @abstractmethod
    def get_metadata(self) -> SourceMetadata:
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        pass
```

### PHASE 4.2: 事件检测与聚类 (6-7h)

| ID | 任务 | 验收标准 |
|----|------|----------|
| 4.2.1 | 实现文章相似度计算 | 语义相似度 |
| 4.2.2 | 实现 HDBSCAN 聚类 | 事件聚类 |
| 4.2.3 | 实现事件演化追踪 | 时间窗口聚合 |
| 4.2.4 | 实现热点发现算法 | 突发检测 |
| 4.2.5 | 事件摘要生成 | 多文档摘要 |
| 4.2.6 | 事件生命周期管理 | 创建、更新、归档 |

**事件模型：**
```python
class Event:
    - id, title, summary
    - cluster_id: String       # 聚类标识
    - entry_ids: JSON          # 包含的条目
    - first_seen_at, last_seen_at
    - article_count: Integer   # 文章数量
    - trend_score: Float       # 热度分数
    - keywords: JSON
    - entities: JSON           # 命名实体
    - status: emerging | active | fading | archived
```

### PHASE 4.3: 趋势分析系统 (5-6h)

| ID | 任务 | 验收标准 |
|----|------|----------|
| 4.3.1 | 实现关键词趋势分析 | 时间序列聚合 |
| 4.3.2 | 实现主题热度追踪 | 滑动窗口统计 |
| 4.3.3 | 实现突发事件检测 | 异常检测算法 |
| 4.3.4 | 实现趋势预测 | Prophet/ARIMA |
| 4.3.5 | 可视化 API | 图表数据 |
| 4.3.6 | 趋势报告生成 | 定期报告 |

**趋势数据模型：**
```python
class KeywordTrend:
    - keyword: String
    - counts: JSON            # 时间序列计数
    - scores: JSON            # 热度分数
    - velocity: Float         # 增长速度
    - acceleration: Float     # 加速度
    - predicted: JSON         # 预测值

class TopicTrend:
    - topic_id: Integer
    - topic_name: String
    - entry_volume: JSON      # 文章量趋势
    - engagement_score: JSON  # 参与度趋势
    - sentiment_score: JSON   # 情感趋势
```

### PHASE 4.4: 知识图谱构建 (4-5h)

| ID | 任务 | 验收标准 |
|----|------|----------|
| 4.4.1 | 实体识别与抽取 | NER 模型 |
| 4.4.2 | 实现关系抽取 | 共现分析 |
| 4.4.3 | 构建图数据库 | NetworkX/Neo4j |
| 4.4.4 | 实现图查询 API | 路径查找、社区发现 |
| 4.4.5 | 知识图谱可视化 | 交互式展示 |

**知识图谱模型：**
```python
class Entity:
    - id, name, type          # 人物/组织/地点/概念
    - aliases: JSON
    - description: Text
    - metadata: JSON

class Relation:
    - id, source_id, target_id
    - relation_type: mentions | associated_with | employs | ...
    - weight: Float           # 关系强度
    - context: Text
```

### PHASE 4.5: 自动化报告系统 (4-5h)

| ID | 任务 | 验收标准 |
|----|------|----------|
| 4.5.1 | 设计报告模板系统 | 可自定义 |
| 4.5.2 | 实现日报生成器 | 每日摘要 |
| 4.5.3 | 实现周报生成器 | 趋势分析 |
| 4.5.4 | 实现 PDF 导出 | WeasyPrint |
| 4.5.5 | 实现邮件推送 | SMTP |
| 4.5.6 | 报告调度系统 | 定时生成 |

**报告模板：**
```markdown
# 情报日报 - {date}

## 热点事件
{top_events}

## 关键词趋势
{keyword_trends}

## 新增订阅源
{new_feeds}

## 统计概览
- 新增条目: {entry_count}
- 活跃事件: {active_events}
```

### PHASE 4.6: 高级搜索与过滤 (3-4h)

| ID | 任务 | 验收标准 |
|----|------|----------|
| 4.6.1 | 实现全文搜索 | 向量搜索 |
| 4.6.2 | 实现语义搜索 | 语义相似度 |
| 4.6.3 | 实现组合过滤器 | 复杂查询 |
| 4.6.4 | 搜索结果排序 | 相关性排序 |
| 4.6.5 | 保存搜索查询 | 快速访问 |

### PHASE 4.7: 实时通知系统 (3-4h)

| ID | 任务 | 验收标准 |
|----|------|----------|
| 4.7.1 | 实现通知规则引擎 | 可配置触发条件 |
| 4.7.2 | 支持多渠道通知 | 邮件/Webhook/Telegram |
| 4.7.3 | 实现通知去重 | 避免轰炸 |
| 4.7.4 | 通知历史记录 | 查看和追溯 |

### PHASE 4.8: 数据可视化仪表板 (5-6h)

| ID | 任务 | 验收标准 |
|----|------|----------|
| 4.8.1 | 设计仪表板布局 | 多模块展示 |
| 4.8.2 | 实现趋势图表 | 折线图、面积图 |
| 4.8.3 | 实现事件时间线 | 可视化事件流 |
| 4.8.4 | 实现网络图谱 | 关系可视化 |
| 4.8.5 | 实现词云展示 | 关键词可视化 |
| 4.8.6 | 实时数据更新 | WebSocket |

### PHASE 4.9: API 与集成 (3-4h)

| ID | 任务 | 验收标准 |
|----|------|----------|
| 4.9.1 | Webhook 系统 | 外部集成 |
| 4.9.2 | GraphQL API | 灵活查询 |
| 4.9.3 | 导入/导出功能 | 数据迁移 |
| 4.9.4 | API 密钥管理 | 安全访问 |

### PHASE 4.10: 测试与优化 (4-5h)

| ID | 任务 | 验收标准 |
|----|------|----------|
| 4.10.1 | 多源采集测试 | 验证各数据源 |
| 4.10.2 | 事件聚类评估 | 质量指标 |
| 4.10.3 | 趋势分析验证 | 准确性测试 |
| 4.10.4 | 性能压力测试 | 并发处理 |
| 4.10.5 | 数据安全审计 | 敏感信息保护 |

---

## 验收标准

### 功能性
- ✅ 支持至少 5 种数据源
- ✅ 事件聚类准确率 ≥ 70%
- ✅ 趋势预测误差 ≤ 30%
- ✅ 报告自动生成

### 性能
- ✅ 多源采集延迟 ≤ 30 秒
- ✅ 事件聚类时间 ≤ 5 分钟
- ✅ 仪表板加载 ≤ 3 秒
- ✅ 支持 10000+ 条目处理

### 效果
- ✅ 热点发现准确率 ≥ 75%
- ✅ 用户留存率提升

### 代码质量
- ✅ 单元测试覆盖率 ≥ 70%
- ✅ 文档完整
- ✅ 可扩展架构

---

## 时间估算

| 阶段 | 预计时间 |
|------|----------|
| 4.1 多源采集 | 6-8h |
| 4.2 事件聚类 | 6-7h |
| 4.3 趋势分析 | 5-6h |
| 4.4 知识图谱 | 4-5h |
| 4.5 报告系统 | 4-5h |
| 4.6 高级搜索 | 3-4h |
| 4.7 通知系统 | 3-4h |
| 4.8 数据可视化 | 5-6h |
| 4.9 API 集成 | 3-4h |
| 4.10 测试优化 | 4-5h |
| **总计** | **43-58h** |

**建议开发周期**: 按每天 2-3 小时开发，预计 **4-6 周** 完成

---

## 关键依赖

```toml
[project.dependencies]
"tweepy>=4.14.0",            # Twitter API
"praw>=7.7.0",               # Reddit API
"requests>=2.31.0",          # HTTP 请求
"beautifulsoup4>=4.12.0",    # HTML 解析
"hdbscan>=0.8.33",           # 聚类算法
"scikit-learn>=1.3.0",       # 机器学习
"prophet>=1.1.4",            # 时间序列预测
"networkx>=3.2.0",           # 图计算
"plotly>=5.18.0",            # 交互式图表
"weasyprint>=60.0",          # PDF 生成
"spacy>=3.7.0",              # NLP + NER
"graphql-core>=3.2.5",       # GraphQL
"arrow>=1.3.0",              # 时区处理
```

---

## 事件检测算法

### 相似度计算
```python
# 使用文本嵌入计算相似度
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def compute_similarity(entry1, entry2):
    emb1 = model.encode(entry1.title + " " + entry1.summary)
    emb2 = model.encode(entry2.title + " " + entry2.summary)
    return cosine_similarity(emb1, emb2)
```

### 聚类算法
```python
import hdbscan
import numpy as np

# 获取所有条目的嵌入
embeddings = [model.encode(e.title) for e in entries]

# HDBSCAN 聚类
clusterer = hdbscan.HDBSCAN(
    min_cluster_size=3,
    min_samples=1,
    metric='cosine'
)
labels = clusterer.fit_predict(embeddings)

# 创建事件组
events = {}
for entry, label in zip(entries, labels):
    if label not in events:
        events[label] = []
    events[label].append(entry)
```

### 热点发现
```python
def detect_hot_events(events, window=24h):
    hot_events = []
    for event in events:
        # 计算时间窗口内的文章增长率
        velocity = calculate_growth_rate(event, window)
        # 计算参与度
        engagement = calculate_engagement(event)
        # 热度分数
        hot_score = 0.7 * velocity + 0.3 * engagement
        if hot_score > threshold:
            hot_events.append(event)
    return sort_by_score(hot_events)
```

---

## 趋势分析示例

### 关键词趋势
```python
# 时间窗口聚合
def analyze_keyword_trend(keyword, days=30):
    daily_counts = []
    for day in range(days):
        count = count_keyword_occurrences(keyword, day)
        daily_counts.append(count)

    # 计算增长速度
    velocity = calculate_velocity(daily_counts)

    # 预测未来趋势
    predicted = predict_trend(daily_counts)

    return {
        'historical': daily_counts,
        'velocity': velocity,
        'predicted': predicted
    }
```

### 突发检测
```python
def detect_bursts(keyword_series):
    # 使用 z-score 检测异常
    mean = np.mean(keyword_series)
    std = np.std(keyword_series)

    bursts = []
    for i, value in enumerate(keyword_series):
        z_score = (value - mean) / std
        if z_score > 3:  # 3-sigma 规则
            bursts.append({
                'timestamp': i,
                'value': value,
                'z_score': z_score
            })
    return bursts
```

---

## 报告生成流程

```python
class ReportGenerator:
    def generate_daily_report(self, date):
        # 收集数据
        top_events = get_top_events(date, n=5)
        trending_keywords = get_trending_keywords(date, n=10)
        new_entries = get_new_entries(date)

        # 渲染模板
        html = render_template('daily_report.html', {
            'date': date,
            'events': top_events,
            'keywords': trending_keywords,
            'stats': {
                'entry_count': len(new_entries),
                'feed_count': count_active_feeds()
            }
        })

        # 导出 PDF
        pdf = convert_html_to_pdf(html)

        return pdf
```

---

## 目录结构扩展

```
spider-aggregation/
├── src/spider_aggregation/
│   ├── sources/                # 🆕 多源采集
│   │   ├── __init__.py
│   │   ├── base.py            # 数据源基类
│   │   ├── twitter_source.py
│   │   ├── reddit_source.py
│   │   ├── hn_source.py
│   │   ├── webpage_monitor.py
│   │   ├── arxiv_source.py
│   │   └── email_source.py
│   │
│   ├── clustering/             # 🆕 事件聚类
│   │   ├── __init__.py
│   │   ├── event_detector.py  # 事件检测
│   │   ├── clusterer.py       # 聚类算法
│   │   ├── event_tracker.py   # 事件追踪
│   │   └── event_summarizer.py # 事件摘要
│   │
│   ├── trends/                 # 🆕 趋势分析
│   │   ├── __init__.py
│   │   ├── analyzer.py        # 趋势分析
│   │   ├── forecaster.py      # 预测
│   │   ├── burst_detector.py  # 突发检测
│   │   └ visualizer.py        # 可视化
│   │
│   ├── knowledge/              # 🆕 知识图谱
│   │   ├── __init__.py
│   │   ├── entity_extractor.py # 实体抽取
│   │   ├── relation_extractor.py # 关系抽取
│   │   ├── graph_builder.py   # 图构建
│   │   └── graph_query.py     # 图查询
│   │
│   ├── reports/                # 🆕 报告系统
│   │   ├── __init__.py
│   │   ├── generator.py       # 报告生成
│   │   ├── templates/         # 报告模板
│   │   │   ├── daily.html
│   │   │   ├── weekly.html
│   │   │   └── monthly.html
│   │   └── scheduler.py       # 报告调度
│   │
│   ├── notifications/          # 🆕 通知系统
│   │   ├── __init__.py
│   │   ├── engine.py          # 通知引擎
│   │   ├── channels/          # 通知渠道
│   │   │   ├── email.py
│   │   │   ├── webhook.py
│   │   │   └── telegram.py
│   │   └── rules.py           # 通知规则
│   │
│   └── search/                 # 🆕 高级搜索
│       ├── __init__.py
│       ├── vector_search.py   # 向量搜索
│       ├── semantic_search.py # 语义搜索
│       └── query_builder.py   # 查询构建
│
├── web/src/views/
│   ├── Dashboard.vue          # 🆕 仪表板
│   ├── Events.vue             # 🆕 事件视图
│   ├── Trends.vue             # 🆕 趋势视图
│   ├── KnowledgeGraph.vue     # 🆕 知识图谱
│   └── Reports.vue            # 🆕 报告列表
│
├── models/                     # 训练模型
│   ├── hdbscan_model.pkl
│   ├── sentence_transformer/
│   └── ner_model/
│
└── exports/                    # 导出文件
    └── reports/
```

---

## 数据可视化示例

### 趋势图表
```python
import plotly.graph_objects as go

def create_trend_chart(keyword_data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=keyword_data['dates'],
        y=keyword_data['counts'],
        mode='lines',
        name='实际值'
    ))
    fig.add_trace(go.Scatter(
        x=keyword_data['dates'],
        y=keyword_data['predicted'],
        mode='lines',
        name='预测值',
        line=dict(dash='dash')
    ))
    return fig.to_html()
```

### 事件时间线
```python
def create_event_timeline(events):
    fig = go.Figure()
    for event in events:
        fig.add_trace(go.Scatter(
            x=[event.start, event.end],
            y=[event.id, event.id],
            mode='lines+markers',
            name=event.title
        ))
    return fig.to_html()
```

---

## API 扩展示例

```python
# 事件相关
GET  /api/events                 # 列出事件
GET  /api/events/{id}           # 事件详情
GET  /api/events/{id}/timeline  # 事件时间线
GET  /api/events/trending       # 热点事件

# 趋势相关
GET  /api/trends/keywords       # 关键词趋势
GET  /api/trends/topics         # 主题趋势
GET  /api/trends/bursts         # 突发事件

# 知识图谱
GET  /api/knowledge/entities    # 实体列表
GET  /api/knowledge/graph       # 图数据
GET  /api/knowledge/paths       # 实体关系路径

# 报告
GET  /api/reports               # 报告列表
POST /api/reports/generate      # 生成报告
GET  /api/reports/{id}/download # 下载报告
```
