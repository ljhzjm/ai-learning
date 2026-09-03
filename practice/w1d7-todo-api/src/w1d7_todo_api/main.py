from contextlib import asynccontextmanager
import time

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse

from w1d7_todo_api.config import settings
from w1d7_todo_api.db import TodoNotFoundError, fake_db, reset_db
from w1d7_todo_api.schemas import TodoIn, TodoOut, TodoUpdate

@asynccontextmanager
async def lifespan(app: FastAPI):
    reset_db()                            # 启动时预置数据
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

def get_db():
    return fake_db

@app.exception_handler(TodoNotFoundError)
async def todo_not_found_handler(request: Request, exc: TodoNotFoundError):
    return JSONResponse(status_code=404, content={"error": "not_found", "message": str(exc)})

# C:创建
@app.post("/todos", response_model=TodoOut, status_code=201)
def create_todo(todo: TodoIn, db=Depends(get_db)):
    new_id = max((t["id"] for t in db["todos"]), default=0) + 1
    record = todo.model_dump()
    record["id"] = new_id
    db["todos"].append(record)
    return record

# R:查列表 + 查单条
@app.get("/todos", response_model=list[TodoOut])
def list_todos(db=Depends(get_db)):
    return db["todos"]

@app.get("/todos/{todo_id}", response_model=TodoOut)
def get_todo(todo_id: int, db=Depends(get_db)):
    for t in db["todos"]:
        if t["id"] == todo_id:
            return t
    raise TodoNotFoundError(todo_id)

# U:局部更新
@app.patch("/todos/{todo_id}", response_model=TodoOut)
def update_todo(todo_id: int, todo: TodoUpdate, db=Depends(get_db)):
    for t in db["todos"]:
        if t["id"] == todo_id:
            t.update(todo.model_dump(exclude_unset=True))   # 只更新请求里出现的字段
            return t
    raise TodoNotFoundError(todo_id)

# D:删除
@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int, db=Depends(get_db)):
    for i, t in enumerate(db["todos"]):
        if t["id"] == todo_id:
            db["todos"].pop(i)
            return                   # 返回 None,204 无响应体
    raise TodoNotFoundError(todo_id)                        # 返回 None,204 无响应体