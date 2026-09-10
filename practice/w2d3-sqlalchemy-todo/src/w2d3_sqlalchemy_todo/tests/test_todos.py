import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from w2d3_sqlalchemy_todo.db import engine, redis_client
from w2d3_sqlalchemy_todo.main import app
from w2d3_sqlalchemy_todo.models import Base

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.create_all(engine)        # 幂等:表已存在则跳过
    redis_client.delete("rl:testclient")    # 每个测试重置限流桶,否则请求多了会 429
    with engine.begin() as conn:            # 每个测试前清空并预置,互不污染
        conn.execute(text("TRUNCATE TABLE todos RESTART IDENTITY"))
        conn.execute(text("INSERT INTO todos (title, done) VALUES ('完成第 1 周综合练习', false)"))                # 每个测试前重置,互不污染

def test_list_todos():
    r = client.get("/todos")
    assert r.status_code == 200
    todos = r.json()
    assert len(todos) == 1
    assert todos[0]["title"] == "完成第 1 周综合练习"

def test_list_todos_done_filter():
    r = client.get("/todos?done=true")
    assert r.status_code == 200
    assert r.json() == []                   # 预置那条 done=false,过滤后应为空

def test_create_todo():
    r = client.post("/todos", json={"title": "学 pytest"})
    assert r.status_code == 201
    body = r.json()
    assert body["id"] == 2          # 预置 1 条,新的是 2
    assert body["done"] is False    # 没传 done → 默认 False

def test_get_todos():
    r = client.get("/todos/1")
    assert r.status_code == 200
    body = r.json()
    assert body["id"] == 1
    assert body["title"] == "完成第 1 周综合练习"
    assert body["done"] is False

def test_update_todo_partial():
    r = client.patch("/todos/1", json={"done": True})
    assert r.status_code == 200
    body = r.json()
    assert body["id"] == 1
    assert body["done"] is True
    assert body["title"] == "完成第 1 周综合练习"

def test_update_todo_missing():
    r = client.patch("/todos/5", json={"title": "学 pytest"})
    assert r.status_code == 404

def test_delete_todo():
    r = client.delete("/todos/1")
    assert r.status_code == 204

def test_delete_todo_missing():
    r = client.delete("/todos/5")
    assert r.status_code == 404

def test_create_validation():
    r = client.post("/todos", json={"title": ""})
    assert r.status_code == 422

def test_process_time_header():
    r = client.get("/todos")
    assert r.status_code == 200
    assert "x-process-time" in r.headers
    elapsed = float(r.headers["x-process-time"])
    assert elapsed >= 0
   
