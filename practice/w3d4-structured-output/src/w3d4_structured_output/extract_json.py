"""三档结构化输出强度对比:纯 prompt / JSON mode / tool 强制。

同一批新闻、同一个 schema、同一套重试逻辑,唯一变量是"靠什么保证格式"。
"""

import json
import sys

from pydantic import ValidationError

from w3d4_structured_output.ask import call
from w3d4_structured_output.schema import Extraction
from w3d4_structured_output.settings import Settings

NEWS = [
    "2025年3月12日,腾讯公司创始人马化腾在深圳宣布,腾讯将向人工智能研究院投资50亿元。",
    "4月8日,字节跳动CEO梁汝波在北京与清华大学签署合作协议,捐赠2亿元用于人才培养。",
    "2024年11月5日,苹果公司CEO蒂姆·库克到访上海,与供应商立讯精密会面,未公布具体金额。",
    "昨日,阿里巴巴集团董事会主席蔡崇信在杭州出席2025全球数字贸易博览会,宣布未来三年投入100亿美元。",
    "2023年9月20日,华为轮值董事长孟晚舟在深圳发布新款手机,华为终端公司未披露研发金额。",
    "2025年1月1日,小米创始人雷军在北京宣布,小米汽车向北京理工大学捐赠5000万元。",
]

# ① 纯 prompt:用自然语言把 json 格式"请求"出来
PROMPT_ONLY = """从下面的新闻中抽取人名、公司、地点、日期、金额。
以 json 输出,字段名用 name/company/place/date/amount,未提及的字段填 null。
只输出 json,不要输出其他内容。
新闻:{news}"""

# ③ tool 强制:不用再说"以 json 输出"——schema 已经把形状说死了
PROMPT_TOOL = """从下面的新闻中抽取人名、公司、地点、日期、金额。
新闻:{news}"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "emit_extraction",
            "description": "输出新闻抽取结果",
            "parameters": Extraction.model_json_schema(),  # Pydantic 直接生成 schema
        },
    }
]


def _with_hint(prompt: str, hint: str | None) -> str:
    """重试时把上次的错误回灌进 prompt——不带信息的重试只是重复犯错。"""
    if not hint:
        return prompt
    return prompt + f"\n\n上次的输出不合格:{hint}。请只输出修正后的 json。"


def extract_prompt_only(s: Settings, news: str, hint: str | None = None) -> dict:
    r = call(s, [{"role": "user", "content": _with_hint(PROMPT_ONLY.format(news=news), hint)}])
    return json.loads(r["choices"][0]["message"]["content"])


def extract_json_mode(s: Settings, news: str, hint: str | None = None) -> dict:
    r = call(
        s,
        [{"role": "user", "content": _with_hint(PROMPT_ONLY.format(news=news), hint)}],
        response_format={"type": "json_object"},
    )
    return json.loads(r["choices"][0]["message"]["content"])


def extract_tool(s: Settings, news: str, hint: str | None = None) -> dict:
    r = call(
        s,
        [{"role": "user", "content": _with_hint(PROMPT_TOOL.format(news=news), hint)}],
        tools=TOOLS,
        tool_choice={"type": "function", "function": {"name": "emit_extraction"}},
    )
    msg = r["choices"][0]["message"]
    args = msg["tool_calls"][0]["function"]["arguments"]  # 字符串,不是 dict
    return json.loads(args)


STRATEGIES = [
    ("纯 prompt ", extract_prompt_only),
    ("json mode ", extract_json_mode),
    ("tool 强制 ", extract_tool),
]


def extract_with_retry(
    s: Settings, news: str, fn, tries: int = 3
) -> tuple[Extraction | None, int, bool]:
    """返回 (结果, 尝试次数, 首次输出是否为合法 json)。

    全失败返回 (None, tries, ...)。
    """
    hint = None
    first_json_ok = False
    for i in range(1, tries + 1):
        try:
            raw = fn(s, news, hint)
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            hint = f"不是合法 json({type(e).__name__})"
            continue
        if i == 1:
            first_json_ok = True
        try:
            return Extraction.model_validate(raw), i, first_json_ok
        except ValidationError as e:
            first = e.errors()[0]
            hint = f"字段 {first['loc']} 不合法({first['msg']})"
    return None, tries, first_json_ok


def main() -> None:
    sys.stdout.reconfigure(errors="replace")

    s = Settings()
    for label, fn in STRATEGIES:
        print("\n" + "=" * 60)
        print(f"[{label}]")
        print("=" * 60)
        for news in NEWS:
            result, tries, _ = extract_with_retry(s, news, fn)
            tag = "[OK]" if result else "[ERR] 3 次重试后仍失败"
            retry_note = f" (重试 {tries - 1} 次)" if tries > 1 else ""
            print(f"{tag}{retry_note} {result}")
            print(f"      原文: {news}")


if __name__ == "__main__":
    main()
