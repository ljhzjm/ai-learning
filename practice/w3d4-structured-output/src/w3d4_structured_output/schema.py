from pydantic import BaseModel


class Extraction(BaseModel):
    """一条新闻的抽取结果。字段名用英文——它是要进数据库/接口的标识符,
    不是给人看的标签。"""

    name: str | None = None      # 人名
    company: str | None = None   # 公司名
    place: str | None = None     # 地点
    date: str | None = None      # 日期
    amount: str | None = None    # 金额