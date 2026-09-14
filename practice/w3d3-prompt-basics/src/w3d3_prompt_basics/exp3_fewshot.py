"""实验 3:few-shot 对比——逐条分类 8 条标题,看输出能不能被程序直接消费。

控制变量:同一条标题、同一段指令,唯一区别是有没有 few-shot 示例。
逐条调用(8 条 × 2 组 = 16 次),否则整批塞进去模型自然按行输出,
"格式是否稳定"这个现象根本暴露不出来。
"""

import sys

from w3d3_prompt_basics.ask import ask, system_user
from w3d3_prompt_basics.settings import Settings

CATEGORIES = ["科技", "体育", "娱乐", "财经"]

TITLES = [
    "苹果发布新一代自研芯片,性能提升 40%",
    "国足客场 2:1 逆转对手,晋级希望重燃",
    "某明星新片票房突破 20 亿",
    "央行宣布降准 0.5 个百分点",
    "开源大模型在数学竞赛中首次超过人类金牌选手",
    "湖人队签下全明星后卫,下赛季阵容豪华",
    "某综艺节目因版权问题下架",
    "A 股三大指数集体收涨,北向资金净流入超百亿",
]

ZERO_SHOT = "把下面的新闻标题分类到:科技、体育、娱乐、财经。只输出类别名称,不要解释。标题:{title}"

FEW_SHOT = """把下面的新闻标题分类到:科技、体育、娱乐、财经。只输出类别名称。
示例:
标题:某公司发布折叠屏手机 → 科技
标题:国乒包揽世锦赛全部金牌 → 体育
标题:某上市公司股价连续三日涨停 → 财经
标题:{title}"""


def is_clean(content: str) -> bool:
    """输出能不能被程序直接消费:去掉空白后正好是一个类别名。

    这就是"LLM 应用"和"聊天"的分水岭——干净 = 可以字符串比较、可以落库。
    """
    return content.strip() in CATEGORIES


def run(s: Settings, label: str, template: str) -> list[dict]:
    """逐条调用,返回每条的结果。"""
    print("\n" + "=" * 60)
    print(f"[实验3/{label}] 逐条调用 {len(TITLES)} 次")
    print("=" * 60)

    rows = []
    for i, title in enumerate(TITLES, 1):
        content, usage = ask(s, system_user(None, template.format(title=title)))
        out = content.strip()
        clean = is_clean(out)
        rows.append({"title": title, "out": out, "clean": clean})

        mark = "干净" if clean else "带杂质"
        print(f"[{i}] {title}")
        print(f"    -> {out!r}  [{mark}]")
    return rows


def main() -> None:
    sys.stdout.reconfigure(errors="replace")

    s = Settings()
    zs = run(s, "zero-shot", ZERO_SHOT)
    fs = run(s, "few-shot ", FEW_SHOT)

    print("\n" + "=" * 60)
    print("[实验3/汇总] 输出能否被程序直接消费")
    print("=" * 60)
    print(f"{'#':<4}{'zero-shot':<12}{'few-shot':<12}标题")
    for i, (a, b) in enumerate(zip(zs, fs), 1):
        za = "干净" if a["clean"] else "带杂质"
        fb = "干净" if b["clean"] else "带杂质"
        print(f"{i:<4}{za:<12}{fb:<12}{a['title']}")

    n_zs = sum(r["clean"] for r in zs)
    n_fs = sum(r["clean"] for r in fs)
    print(f"\nzero-shot 干净 {n_zs}/{len(zs)}    few-shot 干净 {n_fs}/{len(fs)}")


if __name__ == "__main__":
    main()
