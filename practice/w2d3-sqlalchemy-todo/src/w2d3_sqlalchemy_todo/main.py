from contextlib import asynccontextmanager
import time

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from w2d3_sqlalchemy_todo.config import settings
from w2d3_sqlalchemy_todo.db import SessionLocal, TodoNotFoundError, engine, get_db
from w2d3_sqlalchemy_todo.models import Base, Todo
from w2d3_sqlalchemy_todo.schemas import TodoIn, TodoOut, TodoUpdate

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)        # 表不存在就建(周四换成 Alembic)
    with SessionLocal() as db:              # 首次启动预置一条;PG 持久化,重启不会重复种
        if db.get(Todo, 1) is None:
            db.add(Todo(title="完成第 1 周综合练习"))
            db.commit()
    print(f"[lifespan] {settings.app_name} 已启动")
    yield

app = FastAPI(title=settings.app_name, lifespan=lifespan)

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
    return obj

# R:查列表 + 查单条
@app.get("/todos", response_model=list[TodoOut])
def list_todos(done: bool | None = None, db: Session = Depends(get_db)):
    stmt = select(Todo).order_by(Todo.id)
    if done is not None:
        stmt = stmt.where(Todo.done == done)   # 只在传了 done 时过滤
    return db.scalars(stmt).all()
    
@app.get("/todos/{todo_id}", response_model=TodoOut)
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    obj = db.get(Todo, todo_id)          # 按主键取一行;内存版 6 行循环变 1 行
    if obj is None:
        raise TodoNotFoundError(todo_id)
    return obj

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
    return obj

# D:删除
@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    obj = db.get(Todo, todo_id)
    if obj is None:
        raise TodoNotFoundError(todo_id)
    db.delete(obj)
    db.commit()