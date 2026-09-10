from contextlib import asynccontextmanager
import time

from fastapi import Depends, FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from w2d3_sqlalchemy_todo.config import settings
from w2d3_sqlalchemy_todo.db import SessionLocal, TodoNotFoundError, engine, get_db, redis_client
from w2d3_sqlalchemy_todo.models import Todo
from w2d3_sqlalchemy_todo.schemas import TodoIn, TodoOut, TodoUpdate

import json
import redis as redis_lib

@asynccontextmanager
async def lifespan(app: FastAPI):
    with SessionLocal() as db:              # 首次启动预置一条;PG 持久化,重启不会重复种
        if db.get(Todo, 1) is None:
            db.add(Todo(title="完成第 1 周综合练习"))
            db.commit()
    print(f"[lifespan] {settings.app_name} 已启动")
    yield

def rate_limit(request: Request):
    try:
        ok = allow_request(f"rl:{request.client.host}")
    except redis_lib.RedisError:
        return                       # Redis 挂了放行(fail-open,生产标准做法)
    if not ok:
        raise HTTPException(429, "Too Many Requests")

app = FastAPI(title=settings.app_name, lifespan=lifespan, dependencies=[Depends(rate_limit)])


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = time.perf_counter() - start
    response.headers["X-Process-Time"] = f"{elapsed:.6f}"
    return response

@app.exception_handler(TodoNotFoundError)
async def todo_not_found_handler(request: Request, exc: TodoNotFoundError):
    return JSONResponse(status_code=404, content={"error": "not_found", "message": str(exc)})

# C:创建
@app.post("/todos", response_model=TodoOut, status_code=201)
def create_todo(todo: TodoIn, db: Session = Depends(get_db)):
    obj = Todo(**todo.model_dump())
    db.add(obj)                 # 只是挂到 session,还没发 SQL
    db.commit()                 # INSERT 在这一刻发出,id 由 PG 序列生成
    db.refresh(obj)             # commit 后对象过期,refresh 取回数据库最终状态
    redis_client.delete("todos:list", f"todos:{obj.id}")
    return obj

# R:查列表 + 查单条
@app.get("/todos", response_model=list[TodoOut])
def list_todos(done: bool | None = None, db: Session = Depends(get_db)):
    if done is not None:
        # 带过滤的查询直接查库不缓存:过滤组合多、命中率低,缓存反而占内存
        stmt = select(Todo).order_by(Todo.id).where(Todo.done == done)
        return db.scalars(stmt).all()
    try:
        cached = redis_client.get("todos:list")
    except redis_lib.RedisError:
        cached = None
    if cached is not None:
        return json.loads(cached)
    todos = db.scalars(select(Todo).order_by(Todo.id)).all()
    payload = [{"id": t.id, "title": t.title, "done": t.done, "created_at": t.created_at.isoformat(), "priority": t.priority} for t in todos]
    redis_client.set("todos:list", json.dumps(payload), ex=30)
    return payload

@app.get("/todos/{todo_id}", response_model=TodoOut)
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    try:
        cached = redis_client.get(f"todos:{todo_id}")
    except redis_lib.RedisError:
        cached = None
    if cached is not None:
        return json.loads(cached)
    obj = db.get(Todo, todo_id)          # 按主键取一行;内存版 6 行循环变 1 行
    if obj is None:
        raise TodoNotFoundError(todo_id)
    data = {"id": obj.id, "title": obj.title, "done": obj.done}
    redis_client.set(f"todos:{todo_id}", json.dumps(data), ex=30)
    return data

# U:局部更新
@app.patch("/todos/{todo_id}", response_model=TodoOut)
def update_todo(todo_id: int, todo: TodoUpdate, db: Session = Depends(get_db)):
    obj = db.get(Todo, todo_id)
    if obj is None:
        raise TodoNotFoundError(todo_id)
    for key, value in todo.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)     # 改对象属性,session 自动标记"脏"
    db.commit()                      # UPDATE 只包含改过的列(echo 里亲眼验证)
    db.refresh(obj)
    redis_client.delete("todos:list", f"todos:{todo_id}")
    return obj

# D:删除
@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    obj = db.get(Todo, todo_id)
    if obj is None:
        raise TodoNotFoundError(todo_id)
    db.delete(obj)
    db.commit()
    redis_client.delete("todos:list", f"todos:{todo_id}")

# 限流 判断是否可以请求,tokens<1 表示拒绝请求,否则允许,每次校验之后更新 tokens以及本次请求的时间戳
def allow_request(key: str, capacity: int = 10, rate: float = 2) -> bool:
    now = time.time()
    tokens, ts = redis_client.hget(key, "tokens"), redis_client.hget(key, "ts")
    tokens = float(tokens if tokens is not None else capacity)   # 新桶 = 满的
    ts = float(ts if ts is not None else now)
    tokens = min(capacity, tokens + (now - ts) * rate)           # 按速率补充,不超过容量
    redis_client.hset(key, mapping={"tokens": tokens - 1, "ts": now})
    redis_client.expire(key, 60)                                 # 闲置 60 秒回收桶
    return tokens >= 1                                            # 补完还不满 1 个 → 拒绝
