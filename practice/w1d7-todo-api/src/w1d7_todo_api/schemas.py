from pydantic import BaseModel, Field

class TodoIn(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    done: bool = False          # 建待办时可以不传,默认 False
class TodoUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    done: bool | None = None
class TodoOut(TodoIn):
    id: int                     # 输出多一个 id,由服务器分配