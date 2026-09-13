# w3d1-hello-llm

第 3 周·周一:用 httpx 手写 OpenAI 兼容 chat 接口,理解 messages / token / max_tokens。供应商:**DeepSeek 官方**(无 embedding 接口,第 4 周 embedding 日需换供应商或本地 bge-m3)。

## 运行

1. 复制 `.env.example` 为 `.env`,填入你的 `LLM_API_KEY`(https://platform.deepseek.com 创建)
2. `uv sync`
3. `uv run python -m w3d1_hello_llm.hello` —— 第一发请求(控制台看到回答 + usage)
4. `uv run python -m w3d1_hello_llm.multi_turn` —— 终端多轮对话(验证"记忆来自 messages")
5. `uv run python -m w3d1_hello_llm.challenge` —— 验收挑战(中英 token 对比 / 截断证据)
