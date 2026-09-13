import httpx
from w3d2_token_cost.estimate import estimate_tokens_zh
from w3d2_token_cost.settings import Settings


def estimate_cost(s: Settings, prompt: str, max_out: int) -> tuple[float, float]:
    """返回 (预估成本, 实际成本):实际成本需真实发一次请求。"""
    est_in = estimate_tokens_zh(prompt)          # 用校准后的系数
    est_cost = est_in / 1_000_000 * s.price_in_per_m + max_out / 1_000_000 * s.price_out_per_m
    # ...真实调用一次,用 usage 里的 prompt_tokens/completion_tokens 算 actual
    r = httpx.post(
        f"{s.base_url}/chat/completions",
        headers={"Authorization": f"Bearer {s.api_key}"},
        json={"model": s.model, "messages": [{"role": "user", "content": prompt}], "max_tokens": max_out},
        timeout=60,
    )
    r.raise_for_status()
    actual_cost = r.json()["usage"]["completion_tokens"] / 1_000_000 * s.price_out_per_m + r.json()["usage"]["prompt_tokens"] / 1_000_000 * s.price_in_per_m
    # 注意:真实调用时请求里 max_tokens=max_out,不然输出价格对不上
    return est_cost, actual_cost