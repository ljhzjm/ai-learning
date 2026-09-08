from pydantic import BaseModel, ConfigDict, Field

class TodoIn(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    done: bool = False          # 建待办时可以不传,默认 False
class TodoUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    done: bool | None = None
class TodoOut(TodoIn):
    id: int
    model_config = ConfigDict(from_attributes=True)
    # ↑ 关键!让 pydantic 能直接读 ORM 对象的属性。
    # 没有它,接口返回 Todo 实例(而不是 dict)时会报响应验证错误(500)