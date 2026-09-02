# db.py —— 假数据库 + 自定义异常
class ItemNotFoundError(Exception):
    def __init__(self, item_id: int):
        self.item_id = item_id
        super().__init__(f"商品 {item_id} 不存在")

fake_db: dict[str, list[dict]] = {"items": []}