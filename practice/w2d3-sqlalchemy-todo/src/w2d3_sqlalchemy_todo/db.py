"""数据库通道:engine(连接池)+ session 工厂 + FastAPI 依赖。"""
from collections.abc import Generator
import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from w2d3_sqlalchemy_todo.config import settings

if not settings.database_url:
    raise RuntimeError("TODO_DATABASE_URL 未配置,请复制 .env.example 为 .env")

engine = create_engine(settings.database_url, echo=settings.debug)
# echo=True:每条 SQL 都打印出来,学 ORM 最有用的开关

SessionLocal = sessionmaker(bind=engine)
# 默认 expire_on_commit=True:commit 后对象属性"过期",
# 下次访问会重新 SELECT —— 所以 create/update 后要 db.refresh() 取回数据库最终状态

def get_db() -> Generator[Session, None, None]:
    """FastAPI 依赖:每个请求发一个 session,请求结束关闭(归还连接,防泄漏)。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class TodoNotFoundError(Exception):
    def __init__(self, todo_id: int):
        self.todo_id = todo_id
        super().__init__(f"待办 {todo_id} 不存在")

redis_client = redis.Redis.from_url(settings.redis_url, decode_responses=True)