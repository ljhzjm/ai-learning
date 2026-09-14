"""实验 2:约束对比——同一个任务,3 档约束,看模型的服从程度。

控制变量:system 一律不给(约束属于"指令"的一部分,写进 user),
只有 user 里的约束在变。
"""

import sys

from w3d3_prompt_basics.ask import ask, system_user
from w3d3_prompt_basics.settings import Settings

TASK = "什么是 Docker?"

# (标签, user 消息)。第一档不写任何约束,作为对照。
VARIANTS: list[tuple[str, str]] = [
    ("无约束", TASK),
    (
        "要点+字数",
        f"用 3 个要点回答,每个要点不超过 15 个字,不要寒暄,不要结尾总结。问题是:{TASK}",
    ),
    (
        "结构模板",
        f"先给一句话结论,再给两个理由,最后给一个类比。问题是:{TASK}",
    ),
]


def main() -> None:
    sys.stdout.reconfigure(errors="replace")

    s = Settings()
    for label, prompt in VARIANTS:
        print("\n" + "=" * 60)
        print(f"[实验2/{label}]")
        print("=" * 60)
        # max_tokens 调大到 800:否则"无约束"那档会被 300 截断,
        # 看起来像"约束让它变短",其实是被截的,对比就不成立了
        content, usage = ask(s, system_user(None, prompt), max_tokens=800)
        print(content)
        print(f"-- usage: {usage['total_tokens']} tokens")


if __name__ == "__main__":
    main()
