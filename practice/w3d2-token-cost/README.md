# w3d2-token-cost

第 3 周·周二:token 估算 + 计价公式,写「估算请求成本」脚本。供应商:DeepSeek 官方。

## 运行

1. 复制 `.env.example` 为 `.env`,填入 `LLM_API_KEY`;`LLM_PRICE_IN_PER_M` / `LLM_PRICE_OUT_PER_M` 按 [DeepSeek 价格页](https://platform.deepseek.com)当前值填写(元/百万 tokens)
2. `uv sync`
3. `uv run python -m w3d2_token_cost.calibrate` —— 实测校准:多段不同长度文本线性拟合,求「每字 token 系数 + 固定开销」,把系数回填 estimate.py
4. `uv run python -m w3d2_token_cost.cost` —— 计价:预估 ¥ vs 实际 ¥(cost.py 提供 estimate_cost 函数)
5. `uv run python -m w3d2_token_cost.challenge` —— 验收挑战:3 段新文本误差 < 20%

## 校准结果(2026-09-13)

中文:token ≈ 0.705 × 字数 + 4.20(仅对 deepseek-chat 有效,换模型要重新校准)
