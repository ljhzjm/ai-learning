"""SQLAlchemy 模型声明:一张 Todo 表。"""
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass                    # 所有模型继承 Base,SQLAlchemy 据此知道哪些类是表

class Todo(Base):
    __tablename__ = "todos"
    id: Mapped[int] = mapped_column(primary_key=True)    # PG 里生成 SERIAL
    title: Mapped[str] = mapped_column(String(100))      # VARCHAR(100),非空
    done: Mapped[bool] = mapped_column(default=False)    # 插入时不写就填 False

    def __repr__(self):
        return f"<Todo {self.id}: {self.title!r} done={self.done}>"