# Alembic 配置完成！

## ✅ 已完成的配置

1. **安装 Alembic**: `uv add alembic`
2. **配置 `migrations/env.py`**: 集成 MindWeaver 的配置系统
3. **配置 `alembic.ini`**: 启用日期前缀和 ruff 格式化
4. **更新迁移模板**: 添加详细的文档注释
5. **创建初始迁移**: `001_initial_schema.py`
6. **标记现有数据库**: `alembic stamp 001`
7. **添加使用文档**: `docs/alembic_guide.md`

## 📋 常用命令

```bash
# 查看当前版本
alembic current

# 查看迁移历史
alembic history

# 应用所有待执行的迁移
alembic upgrade head

# 回滚最后一个迁移
alembic downgrade -1

# 创建新迁移（自动检测模型变更）
alembic revision --autogenerate -m "描述变更"

# 创建空迁移（用于复杂的数据迁移）
alembic revision -m "描述变更"

# 标记数据库为当前版本（不执行迁移）
alembic stamp head
```

## 🔄 日常工作流程

```bash
# 1. 修改 SQLAlchemy 模型
# 编辑 src/spider_aggregation/models/*.py

# 2. 生成迁移脚本
alembic revision --autogenerate -m "add new field"

# 3. 检查生成的迁移文件
cat migrations/versions/2026_XX_XX_XXXX_XXX_add_new_field.py

# 4. 测试迁移
alembic upgrade head
sqlite3 data/spider_aggregation.db ".schema table_name"

# 5. 如需回滚
alembic downgrade -1

# 6. 提交代码
git add migrations/versions/
git commit -m "feat: add new field"
```

## 🎯 下次添加新字段时

```python
# 1. 修改模型
class FeedModel(Base):
    favicon_url = Column(String(2048), nullable=True)  # 新字段

# 2. 生成迁移
alembic revision --autogenerate -m "add feed favicon URL"

# 3. 查看生成的迁移（检查是否正确）
cat migrations/versions/XXXX_add_feed_favicon_url.py

# 4. 应用迁移
alembic upgrade head
```

## ⚠️ 注意事项

1. **生产环境操作前务必备份数据库**
   ```bash
   cp data/spider_aggregation.db backups/spider_aggregation_$(date +%Y%m%d_%H%M%S).db
   ```

2. **始终审查自动生成的迁移** - 不要盲目应用

3. **SQLite 的 ALTER TABLE 限制** - Alembic 已配置批量模式处理

4. **已存在的数据库** - 使用 `alembic stamp head` 标记为当前版本

## 📚 相关文档

- 详细指南: `docs/alembic_guide.md`
- Alembic 官方文档: https://alembic.sqlalchemy.org/

## ✅ 当前状态

```
当前版本: 001 (head)
迁移历史:
  <base> -> 001 (head), Initial schema: create all tables
```

## 🚀 下一步

现在你可以安全地修改数据库结构了！

- 开发环境: `alembic upgrade head`
- 生产环境: 在备份后运行 `alembic upgrade head`
- 回滚: `alembic downgrade -1`
