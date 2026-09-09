"""SQLAlchemy 模型声明:一张 Todo 表。"""
from datetime import datetime
from sqlalchemy import String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass                    # 所有模型继承 Base,SQLAlchemy 据此知道哪些类是表

class Todo(Base):
    __tablename__ = "todos"
    id: Mapped[int] = mapped_column(primary_key=True)    # PG 里生成 SERIAL
    title: Mapped[str] = mapped_column(String(100))      # VARCHAR(100),非空
    done: Mapped[bool] = mapped_column(default=False)    # 插入时不写就填 False
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    priority: Mapped[int] = mapped_column(server_default="0")
    # server_default=数据库侧默认:加列时库里已有的行会自动填 now()
    # 还记得吗?昨天说过 server_default "今天不用" —— 今天就是它的主场

    def __repr__(self):
        return f"<Todo {self.id}: {self.title!r} done={self.done}>"