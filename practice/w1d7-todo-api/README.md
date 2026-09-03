# w1d7-todo-api

第 1 周综合练习:待办事项 API —— CRUD + 内存存储 + pytest 单测。

## 如何运行
uv run uvicorn w1d7_todo_api.main:app --reload
# 浏览器打开 http://127.0.0.1:8000/docs

## 如何测试
uv run pytest
uv run pytest -v