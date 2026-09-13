"""验收挑战:中英 token 对比 / max_tokens 截断证据。(挑战 3 的 401 优雅报错在 hello.py)"""

import httpx

from w3d1_hello_llm.settings import Settings


def token_compare(s: Settings) -> None:
    """挑战 1:同一句话,中英各查一次 usage,对比 prompt_tokens(不加 system,控制变量)。"""
    zh = "我爱编程"
    en = "I love programming"
    counts = []
    for text in (zh, en):
        r = httpx.post(
            f"{s.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {s.api_key}"},
            json={"model": s.model, "messages": [{"role": "user", "content": text}], "max_tokens": 1},
            timeout=60,
        )
        r.raise_for_status()
        counts.append(r.json()["usage"]["prompt_tokens"])
    print(f"[挑战1] 中文「{zh}」: {counts[0]} tokens | 英文「{en}」: {counts[1]} tokens")


def truncation_evidence(s: Settings) -> None:
    """挑战 2:max_tokens=5 强制截断,finish_reason 应为 length。"""
    r = httpx.post(
        f"{s.base_url}/chat/completions",
        headers={"Authorization": f"Bearer {s.api_key}"},
        json={
            "model": s.model,
            "messages": [{"role": "user", "content": "给我讲一个很长的故事"}],
            "max_tokens": 5,
        },
        timeout=60,
    )
    r.raise_for_status()
    data = r.json()
    print(f"[挑战2] finish_reason = {data['choices'][0]['finish_reason']!r}  (截断证据,应为 'length')")
    print(f"        回答: {data['choices'][0]['message']['content']!r}")


def main() -> None:
    s = Settings()
    token_compare(s)
    truncation_evidence(s)


if __name__ == "__main__":
    main()
