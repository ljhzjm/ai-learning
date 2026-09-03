import pytest
from fastapi.testclient import TestClient

from w1d7_todo_api.db import reset_db
from w1d7_todo_api.main import app

client = TestClient(app)        # 不用起服务器

@pytest.fixture(autouse=True)
def clean_db():
    reset_db()                  # 每个测试前重置,互不污染

def test_list_todos():
    r = client.get("/todos")
    assert r.status_code == 200
    todos = r.json()
    assert len(todos) == 1
    assert todos[0]["title"] == "完成第 1 周综合练习"

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
   
