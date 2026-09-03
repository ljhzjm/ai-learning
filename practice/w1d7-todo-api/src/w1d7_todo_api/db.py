class TodoNotFoundError(Exception):
    def __init__(self, todo_id: int):
        self.todo_id = todo_id
        super().__init__(f"待办 {todo_id} 不存在")

fake_db: dict[str, list[dict]] = {"todos": []}

def reset_db():
    """清空并预置一条数据。lifespan 启动时和测试夹具里都调它。"""
    fake_db["todos"] = [{"id": 1, "title": "完成第 1 周综合练习", "done": False}]