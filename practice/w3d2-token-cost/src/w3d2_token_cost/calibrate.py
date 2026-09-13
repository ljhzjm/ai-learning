import statistics

import httpx
from w3d2_token_cost.cost import estimate_cost
from w3d2_token_cost.settings import Settings



# 5 段不同长度的中文样本(自己写,10~400 字,题材随意)
SAMPLES_ZH = [
    "今天天气不错。",
    "今天天气不错,适合出门散步,顺便去菜市场买点水果回来。",
    "今天天气一般,适合睡觉。"
]


def real_tokens(s: Settings, text: str) -> int:
    r = httpx.post(
        f"{s.base_url}/chat/completions",
        headers={"Authorization": f"Bearer {s.api_key}"},
        json={"model": s.model, "messages": [{"role": "user", "content": text}], "max_tokens": 1},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()["usage"]["prompt_tokens"]


def main() -> None:
    s = Settings()
    lengths = [len(t) for t in SAMPLES_ZH]      # x:字数
    tokens = [real_tokens(s, t) for t in SAMPLES_ZH]  # y:真实 token
    for length, token in zip(lengths, tokens):
        print(f"字数 {length:4d} -> {token:4d} tokens")
    slope, intercept = statistics.linear_regression(lengths, tokens)
    for t in SAMPLES_ZH:
        est_cost, actual_cost = estimate_cost(s, t, 100)
        print(f"中文「{t}」: 预估 ¥{est_cost:.7f}, 实际 ¥{actual_cost:.7f}, 误差 {(est_cost - actual_cost) / actual_cost * 100:.7f}%")
    print(f"\n拟合:token = {slope:.3f} × 字数 + {intercept:.2f}")
    print(f"结论:中文每字约 {slope:.2f} token,每条消息固定开销约 {intercept:.0f} token")

if __name__ == "__main__":
    main()