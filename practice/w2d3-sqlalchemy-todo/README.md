# w2d3-sqlalchemy-todo(第 2 周·周三)

把第 1 周的待办 API 从内存 dict 存储改成 **PostgreSQL + SQLAlchemy 2.0 ORM**。

## 运行

```powershell
# 前置:pg-school 容器(见 guides/今日学习指导_2026-09-08.md 第 0 步)+ 数据库 todo
Copy-Item .env.example .env    # 首次
uv run uvicorn w2d3_sqlalchemy_todo.main:app --reload
uv run pytest                  # 9 个测试
```

## 结构

| 文件 | 职责 |
|---|---|
| `models.py` | ORM 模型声明(Todo 表) |
| `db.py` | engine + session 工厂 + get_db 依赖 |
| `main.py` | CRUD 接口(全部走 ORM 对象) |
| `schemas.py` | Pydantic 校验(TodoOut 需 `from_attributes=True`) |
| `school_demo.py` | 关系映射演示:school 三表 relationship + lazy load |

## 踩坑记录

- 返回 ORM 对象必须 `from_attributes=True`,否则响应校验 500
- `GET /todos?done=true` 过滤要**条件拼接** where,无条件 `Todo.done == None` 会生成 `IS NULL`
- SERIAL 序列显式插 id 后不推进,插新行报 duplicate key → `setval` 修复
- 测试用 `TRUNCATE ... RESTART IDENTITY` 重置数据与序列
