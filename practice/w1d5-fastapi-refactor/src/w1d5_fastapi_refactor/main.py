import time
from w1d5_fastapi_refactor.config import settings
from contextlib import asynccontextmanager

from w1d5_fastapi_refactor.db import ItemNotFoundError, fake_db

from fastapi import FastAPI,Depends, Query
from pydantic import BaseModel, Field
from fastapi import Request
from fastapi.responses import JSONResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行一次:预置数据
    fake_db["items"].extend([
        {"id": 1, "name": "键盘", "price": 299.5, "is_offer": False},
        {"id": 2, "name": "显示器", "price": 1299.0, "is_offer": True},
    ])
    print(f"[lifespan] 启动完成,预置 {len(fake_db['items'])} 件商品")
    yield                       # ← 应用运行期间停在这里
    # 关闭时执行一次:清理
    print("[lifespan] 正在关闭,清理资源")

app = FastAPI(lifespan=lifespan)

@app.middleware("http")
async def log_time(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)   # 放行给真正的接口
    elapsed = (time.perf_counter() - start) * 1000
    response.headers["X-Process-Time"] = f"{elapsed:.2f}ms"
    print(f"{request.method} {request.url.path} -> {response.status_code} ({elapsed:.2f}ms)")
    return response

def get_settings():          # 依赖 1:配置
    return settings

def get_db():                # 依赖 2:假数据库
    return fake_db

def get_pagination(          # 依赖 3:分页参数(依赖里也能做校验!)
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
):
    return {"skip": skip, "limit": limit}


@app.get("/")
def root(s = Depends(get_settings)):
    return {"app": s.app_name, "docs": "http://127.0.0.1:8000/docs"}


# 接口 1:路径参数 + 注入配置
@app.get("/hello/{name}")
def hello(name: str, s = Depends(get_settings)):
    return {"message": f"Hello, {name}!", "from": s.app_name}

# 接口 2:查询参数 → 由 get_pagination 统一接管
@app.get("/items")
def list_items(p = Depends(get_pagination), db = Depends(get_db)):
    items = db["items"]
    return {"items": items[p["skip"] : p["skip"] + p["limit"]]}

# 接口 3:POST 现在真的写入"数据库"
class Item(BaseModel):
    name: str
    price: float
    is_offer: bool = False
@app.post("/items", status_code=201)
def create_item(item: Item, db = Depends(get_db)):
    new_id = max((i["id"] for i in db["items"]), default=0) + 1
    record = item.model_dump()      # Pydantic 模型 → dict
    record["id"] = new_id
    db["items"].append(record)
    return record

@app.get("/items/{item_id}")
def get_item(item_id: int, db = Depends(get_db)):
    for item in db["items"]:
        if item["id"] == item_id:
            return item
    raise ItemNotFoundError(item_id)   # 找不到 → 抛自定义异常

@app.exception_handler(ItemNotFoundError)
async def item_not_found_handler(request: Request, exc: ItemNotFoundError):
    return JSONResponse(status_code=404, content={"error": "not_found", "message": str(exc)})

class DiscountIn(BaseModel):
    discount: float = Field(ge=0, le=1)

@app.post("/items/{item_id}/offer")
def offer_item(item_id: int, payload: DiscountIn, db = Depends(get_db)):
    for item in db["items"]:
        if item["id"] == item_id:
            item["is_offer"] = True
            item["price"] = round(item["price"] * payload.discount, 2)
            return item
    raise ItemNotFoundError(item_id)
