"""信息抽取:zero-shot vs few-shot,逐条对比输出格式稳定性。

控制变量:同一条新闻、同一段抽取指令,唯一区别是有没有 few-shot 示例。
每次只喂一条新闻——一次塞 6 条的话,格式乱了分不清是"示例干扰"
还是"多条挤在一起注意力分散"。
"""

import sys

from w3d3_prompt_basics.ask import ask, system_user
from w3d3_prompt_basics.settings import Settings

FIELDS = ["人名", "公司", "地点", "日期", "金额"]

NEWS = [
    "2025年3月12日,腾讯公司创始人马化腾在深圳宣布,腾讯将向人工智能研究院投资50亿元。",
    "4月8日,字节跳动CEO梁汝波在北京与清华大学签署合作协议,捐赠2亿元用于人才培养。",
    "2024年11月5日,苹果公司CEO蒂姆·库克到访上海,与供应商立讯精密会面,未公布具体金额。",
    "昨日,阿里巴巴集团董事会主席蔡崇信在杭州出席2025全球数字贸易博览会,宣布未来三年投入100亿美元。",
    "2023年9月20日,华为轮值董事长孟晚舟在深圳发布新款手机,华为终端公司未披露研发金额。",
    "2025年1月1日,小米创始人雷军在北京宣布,小米汽车向北京理工大学捐赠5000万元。",
]

# 注意:说"一行一个字段"就必须真的把布局写成多行。
# 原来写成"人名:... / 公司:... / 地点:..."却要求"一行一个字段"是自相矛盾的,
# 模型只能猜——这正是自然语言约束"不稳定"的活例子。
_LAYOUT = "\n".join(f"{f}:..." for f in FIELDS)
_RULES = f"从下面的新闻中抽取人名、公司名、地点、日期、金额,严格按下面的格式输出,不要输出其他内容。未提及的字段写\"无\"。\n格式:\n{_LAYOUT}\n新闻:{{news}}"

ZERO_SHOT_PROMPT = _RULES

FEW_PROMPT = f"""从下面的新闻中抽取人名、公司名、地点、日期、金额,严格按下面的格式输出,不要输出其他内容。未提及的字段写"无"。
格式:
{_LAYOUT}
示例:
新闻:2023年5月10日,阿里巴巴创始人马云在杭州出席活动,宣布向浙江大学捐赠1亿元。
人名:马云
公司:阿里巴巴
地点:杭州
日期:2023年5月10日
金额:1亿元
新闻:昨天,特斯拉CEO埃隆·马斯克到访北京,与商务部官员会面。
人名:埃隆·马斯克
公司:特斯拉
地点:北京
日期:昨天
金额:无
新闻:{{news}}"""


def parse_fields(content: str) -> dict[str, str] | None:
    """尝试把输出解析成 5 个字段;返回 None = 这段输出程序没法直接用。

    全角冒号也算通过(顺手归一化)——但模型什么时候用全角、什么时候用半角
    是不可控的,这本身就是"自然语言约束不够稳"的证据。
    """
    out: dict[str, str] = {}
    for raw in content.strip().splitlines():
        line = raw.strip().replace("：", ":")
        if not line:
            continue
        key, sep, value = line.partition(":")
        if not sep or key.strip() not in FIELDS:
            return None
        out[key.strip()] = value.strip()
    if set(out) != set(FIELDS):
        return None
    return out


def run(s: Settings, label: str, template: str) -> list[dict]:
    print("\n" + "=" * 60)
    print(f"[抽取/{label}] 逐条抽取 {len(NEWS)} 条")
    print("=" * 60)

    rows = []
    for i, news in enumerate(NEWS, 1):
        content, usage = ask(s, system_user(None, template.format(news=news)), max_tokens=400)
        parsed = parse_fields(content)
        rows.append({"news": news, "raw": content.strip(), "parsed": parsed})

        print(f"[{i}] {news}")
        print(content.strip())
        print(f"    -> {'可解析 [OK]' if parsed else '格式不可消费 [ERR]'}")
        print("-" * 60)
    return rows


def main() -> None:
    sys.stdout.reconfigure(errors="replace")

    s = Settings()
    zs = run(s, "zero-shot", ZERO_SHOT_PROMPT)
    fs = run(s, "few-shot ", FEW_PROMPT)

    print("\n" + "=" * 60)
    print("[汇总] 输出格式能否被程序直接解析")
    print("=" * 60)
    ok_zs = sum(r["parsed"] is not None for r in zs)
    ok_fs = sum(r["parsed"] is not None for r in fs)
    print(f"zero-shot 可解析 {ok_zs}/{len(zs)}    few-shot 可解析 {ok_fs}/{len(fs)}")

    # 逐字段比一比两组抽出来的内容是否一致(同样的输入,答案该不该相同?)
    print("\n逐条对比(只列字段值不同的):")
    diff = 0
    for i, (a, b) in enumerate(zip(zs, fs), 1):
        if a["parsed"] and b["parsed"] and a["parsed"] != b["parsed"]:
            diff += 1
            for f in FIELDS:
                if a["parsed"][f] != b["parsed"][f]:
                    print(f"  [{i}] {f}: zero-shot={a['parsed'][f]!r}  few-shot={b['parsed'][f]!r}")
    if diff == 0:
        print("  (无差异)")


if __name__ == "__main__":
    main()
