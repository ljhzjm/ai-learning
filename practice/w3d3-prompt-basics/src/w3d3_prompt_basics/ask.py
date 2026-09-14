"""公共函数:发一次 chat 请求,返回 (回答内容, usage)。"""

import httpx

from w3d3_prompt_basics.settings import Settings


def ask(s: Settings, messages: list[dict], max_tokens: int = 300) -> tuple[str, dict]:
    r = httpx.post(
        f"{s.base_url}/chat/completions",
        headers={"Authorization": f"Bearer {s.api_key}"},
        json={"model": s.model, "messages": messages, "max_tokens": max_tokens},
        timeout=60,
    )
    r.raise_for_status()
    data = r.json()
    return data["choices"][0]["message"]["content"], data["usage"]


def system_user(system: str | None, user: str) -> list[dict]:
    """拼 messages:有 system 就带,没有就纯 user(用于无角色对照组)。"""
    if system:
        return [{"role": "system", "content": system}, {"role": "user", "content": user}]
    return [{"role": "user", "content": user}]