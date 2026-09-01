from w1d4_fastapi_demo.config import settings



from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

@app.get("/")
def root():
    return {"app": settings.app_name, "docs": "http://127.0.0.1:8000/docs"}
# 接口 1:路径参数 —— /hello/{name} 里的 {name} 会被捕获
@app.get("/hello/{name}")
def hello(name: str):
    return {"message": f"Hello, {name}!"}

# 接口 2:查询参数 —— ?skip=5&limit=3,不传就用默认值 0 和 10
@app.get("/items")
def list_items(skip: int = 0, limit: int = 10):
    all_items = list(range(100))
    return {"items": all_items[skip : skip + limit]}

# 接口 3:请求体 + Pydantic 校验
class Item(BaseModel):
    name: str
    price: float
    is_offer: bool = False

@app.post("/items")
def create_item(item: Item):
    return {"created": item.name, "price": item.price, "is_offer": item.is_offer}