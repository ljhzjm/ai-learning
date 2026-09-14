"""发一次 chat 请求,返回原始 response dict。"""

import httpx

from w3d4_structured_output.settings import Settings

MAX_TOKENS = 400


def call(s: Settings, messages: list[dict], **extra) -> dict:
    """extra 用来透传 response_format / tools / tool_choice 等。"""
    r = httpx.post(
        f"{s.base_url}/chat/completions",
        headers={"Authorization": f"Bearer {s.api_key}"},
        json={"model": s.model, "messages": messages, "max_tokens": MAX_TOKENS, **extra},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()