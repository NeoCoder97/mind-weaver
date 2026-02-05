# MindWeaver API 与 Web 端对接情况检查报告

基于 `openapi.yaml` 与当前 Web 前端（templates + static/js）的对照结果。

---

## 一、Web 已使用的接口（与 OpenAPI 一致）


| 模块           | 方法     | 路径                             | 使用位置                               |
| ------------ | ------ | ------------------------------ | ---------------------------------- |
| Feeds        | GET    | `/api/feeds`                   | feeds.html DataTable, 首页 feed 筛选下拉 |
| Feeds        | GET    | `/api/feeds/{id}`              | feeds.html 编辑时加载                   |
| Feeds        | POST   | `/api/feeds`                   | feeds.html 新建                      |
| Feeds        | PUT    | `/api/feeds/{id}`              | feeds.html 编辑保存                    |
| Feeds        | DELETE | `/api/feeds/{id}`              | feeds.html 删除                      |
| Feeds        | PATCH  | `/api/feeds/{id}/toggle`       | feeds.html 启用/禁用                   |
| Feeds        | POST   | `/api/feeds/{id}/fetch`        | feeds.html 立即抓取                    |
| Categories   | GET    | `/api/categories`              | categories.html, feeds.html 表单分类下拉 |
| Categories   | GET    | `/api/categories/{id}`         | categories.html 编辑时加载              |
| Categories   | POST   | `/api/categories`              | categories.html 新建                 |
| Categories   | PUT    | `/api/categories/{id}`         | categories.html 编辑保存               |
| Categories   | DELETE | `/api/categories/{id}`         | categories.html 删除                 |
| Filter Rules | GET    | `/api/filter-rules`            | filter_rules.html                  |
| Filter Rules | GET    | `/api/filter-rules/{id}`       | filter_rules.html 编辑时加载            |
| Filter Rules | POST   | `/api/filter-rules`            | filter_rules.html 新建               |
| Filter Rules | PUT    | `/api/filter-rules/{id}`       | filter_rules.html 编辑、切换启用          |
| Filter Rules | DELETE | `/api/filter-rules/{id}`       | filter_rules.html 删除               |
| Entries      | GET    | `/api/entries`                 | index.html DataTable               |
| Entries      | GET    | `/api/entries/{id}`            | entry 详情、api.js entries.get        |
| Entries      | PUT    | `/api/entries/{id}`            | index/entry 已读、未读、批量标记已读           |
| Entries      | DELETE | `/api/entries/{id}`            | index.html 删除单条                    |
| Entries      | POST   | `/api/entries/batch/delete`    | index.html 批量删除                    |
| Entries      | POST   | `/api/entries/batch/mark-read` | index.html 批量标记已读                  |
| Scheduler    | GET    | `/api/scheduler/status`        | dashboard.html                     |
| Scheduler    | POST   | `/api/scheduler/start`         | dashboard.html                     |
| Scheduler    | POST   | `/api/scheduler/stop`          | dashboard.html                     |
| Scheduler    | POST   | `/api/scheduler/fetch-all`     | dashboard.html                     |
| System       | GET    | `/api/stats`                   | dashboard.html                     |
| System       | GET    | `/api/settings`                | settings.html 加载设置                 |
| System       | PUT    | `/api/settings`                | settings.html 保存设置                 |
| System       | GET    | `/api/settings/db-size`        | settings.html 数据库大小                |


说明：

- **Filter Rules 启用/禁用**：Web 通过 `PUT /api/filter-rules/{id}` 传 `{ enabled: true/false }` 实现，未使用 OpenAPI 中的 `PATCH /api/filter-rules/{id}/toggle`。
- **批量删除/批量已读**：后端同时接受 `ids` 与 `entry_ids`，前端使用 `ids`，对接正常。条目状态使用 `enabled` 字段（enabled=true 未读，false 已读）。
- **Settings**：OpenAPI 未收录 `/api/settings`、`/api/settings/db-size`，但后端已实现且 Web 在用，建议在 OpenAPI 中补充。

---

## 二、OpenAPI 有、Web 未使用的接口

### 2.1 建议保留（预留或给其他客户端用）


| 方法     | 路径                                              | 说明                               |
| ------ | ----------------------------------------------- | -------------------------------- |
| GET    | `/api/feeds/{feed_id}/categories`               | 获取某订阅源关联分类，当前表单用 GET feed 即含分类信息 |
| PUT    | `/api/feeds/{feed_id}/categories`               | 设置订阅源分类（多分类），当前表单为单分类 + PUT feed |
| PUT    | `/api/feeds/{feed_id}/categories/{category_id}` | 添加分类到订阅源                         |
| DELETE | `/api/feeds/{feed_id}/categories/{category_id}` | 从订阅源移除分类                         |
| PATCH  | `/api/categories/{id}/toggle`                   | 分类启用/禁用，后端已实现                    |
| GET    | `/api/categories/{category_id}/feeds`           | 某分类下订阅源列表                        |
| GET    | `/api/categories/stats`                         | 分类整体统计                           |
| GET    | `/api/categories/{category_id}/entries/stats`   | 某分类条目统计                          |
| GET    | `/api/entries/by-category/{category_id}`        | 按分类分页查条目                         |
| GET    | `/api/entries/by-category-name/{category_name}` | 按分类名称查条目                         |
| GET    | `/api/entries/search-by-category/{category_id}` | 在分类内搜索                           |
| GET    | `/api/entries/by-category/{category_id}/stats`  | 某分类条目统计                          |
| POST   | `/api/scheduler/digest/trigger`                 | 手动触发摘要邮件                         |
| GET    | `/api/scheduler/digest/logs`                    | 摘要发送日志                           |
| GET    | `/api/system/config`                            | 获取 LLM/邮件/摘要配置                   |
| PUT    | `/api/system/config/llm`                        | 更新 LLM 配置                        |
| POST   | `/api/system/config/llm/test`                   | 测试 LLM 连接                        |
| PUT    | `/api/system/config/email`                      | 更新邮件配置                           |
| POST   | `/api/system/config/email/test`                 | 测试邮件连接                           |
| PUT    | `/api/system/config/digest`                     | 更新摘要配置                           |


以上为预留或多端使用，**不建议删除**，可在后续迭代中由 Web 或其它客户端使用。

### 2.2 Web 功能缺失（已补齐）

| 接口                                                                    | Web 实现说明 |
| --------------------------------------------------------------------- | ----------- |
| `GET /api/dashboard/activity`                                         | 已实现：仪表盘「最近活动」区块，展示最近 10 条条目（标题、来源、时间） |
| `GET /api/dashboard/feed-health`                                      | 已实现：仪表盘「订阅源健康状态」表格（名称、状态、错误次数、最后抓取） |
| `PATCH /api/categories/{id}/toggle`                                   | 已实现：分类列表增加「启用/禁用」行操作及状态列 |
| `POST /api/system/cleanup`                                            | 已实现：设置页「数据管理」中清理旧条目（输入天数 + 执行清理） |
| `GET /api/system/export/entries`、`GET /api/system/export/feeds`       | 已实现：设置页「导出条目」「导出订阅源」按钮触发下载 |
| `GET /api/system/config` + PUT/POST 各 config                          | 已实现：设置页「系统配置」Tab（LLM / 邮件 / 摘要）表单与测试连接 |
| `POST /api/scheduler/digest/trigger`、`GET /api/scheduler/digest/logs` | 已实现：设置页「邮件摘要」区块：手动发送摘要 + 发送记录列表与分页 |


### 2.3 冗余或需修正的接口/文档


| 项目                                  | 说明                                                                 |
| ----------------------------------- | ------------------------------------------------------------------ |
| `PATCH /api/entries/{id}/toggle`    | 条目已统一为 `enabled` 字段，基类 `_toggle` 可正常切换。Web 当前用 `PUT` 更新 `enabled`。 |
| `GET /api/filter-rules/{id}/toggle` | Web 用 PUT 更新 enabled，未用该 PATCH。可保留作为便捷接口。                          |


---

## 三、前端调用但 OpenAPI/后端未覆盖的接口

（已移除：`API.feeds.validate` 已从 api.js 删除。）

---

## 四、OpenAPI 与实现差异（建议同步）

1. **批量删除请求体**：OpenAPI 写 `entry_ids`，后端同时支持 `ids` 与 `entry_ids`。建议在 OpenAPI 中注明两者皆可。
2. **Settings**：补充 `GET /api/settings`、`PUT /api/settings`、`GET /api/settings/db-size` 的定义。
3. **Entries**：条目已统一使用 `enabled` 字段（true=未读，false=已读），`PATCH /api/entries/{id}/toggle` 与基类一致。

---

## 五、总结与建议


| 类型                  | 数量       | 建议                                                    |
| ------------------- | -------- | ----------------------------------------------------- |
| Web 已使用             | 约 28 个端点 | 保持现状，OpenAPI 缺的 settings 建议补上                         |
| OpenAPI 有、Web 未用、保留 | 约 20 个   | 保留，用于预留或多端；可逐步在 Web 使用（仪表盘、设置、分类、摘要等）                 |
| Web 功能缺失            | 7 类能力    | 仪表盘：活动 + 订阅源健康；设置：清理、导出、邮件/摘要/LLM 配置与摘要触发/日志；分类：启用/禁用 |
| 需修正                 | 0 处      | 已处理：条目使用 `enabled`；前端已移除 `feeds.validate` 调用。         |


建议优先：

1. **OpenAPI**：补充 settings 相关接口；批量删除注明 `ids`/`entry_ids`。
2. **Web**：在仪表盘接入「最近活动」与「订阅源健康」；在设置页接入清理、导出、邮件/摘要/LLM 配置及摘要触发与日志；在分类列表接入启用/禁用。

