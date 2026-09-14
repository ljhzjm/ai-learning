"""实验 1:角色对比——同一个问题换 4 种角色,看回答的知识深度/语气/视角差异。

控制变量:user 消息(问题)完全一致,只有 system(角色)在变。
"""

import sys

from w3d3_prompt_basics.ask import ask, system_user
from w3d3_prompt_basics.settings import Settings

QUESTION = "我最近睡眠不好,有什么建议?"

# (标签, system 角色)。system=None 即"无角色"对照组。
ROLES: list[tuple[str, str | None]] = [
    ("无角色", None),
    ("睡眠科医生", "你是一位三甲医院睡眠科医生"),
    ("健身教练", "你是一位健身教练"),
    ("东北大爷", "你是一位说话爱用比喻的东北大爷"),
]


def main() -> None:
    # GBK 控制台遇到 emoji 会崩,replace 让它降级成 ? 而不是报错
    sys.stdout.reconfigure(errors="replace")

    s = Settings()
    for label, role in ROLES:
        print("\n" + "=" * 60)
        print(f"[实验1/{label}] system={role!r}")
        print("=" * 60)
        content, usage = ask(s, system_user(role, QUESTION))
        print(content)
        print(f"-- usage: {usage['total_tokens']} tokens")


if __name__ == "__main__":
    main()
