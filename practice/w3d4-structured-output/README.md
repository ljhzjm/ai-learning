# w3d4-structured-output

第 3 周·周四:结构化输出——JSON mode / tool 强制 / Pydantic 校验 + 失败重试。

## 运行

在项目根目录执行(需要 `.env` 里的 `LLM_API_KEY`):

```powershell
uv run python -m w3d4_structured_output.extract_json   # 三档对比:纯 prompt / json mode / tool 强制(6 条)
uv run python -m w3d4_structured_output.challenge      # 验收挑战:12 条 × 3 档 + 统计表
```

## 三档强度

| 档位 | 手段 | 保证什么 | 不保证什么 |
|---|---|---|---|
| 纯 prompt | 自然语言约束 | 什么都不保证 | 全靠模型自觉 |
| JSON mode | `response_format={"type":"json_object"}` | 语法合法的 JSON | 符合你要的字段结构 |
| tool 强制 | `tools` + `tool_choice` | 字段名/类型按 schema 走 | 值对不对 |

`schema.py` 里的 `Extraction` 是**唯一一份定义**——`Extraction.model_json_schema()` 生成给模型的 schema,`Extraction.model_validate()` 校验模型给的东西,两边不会漂。

## 验收结果

12 条新闻 × 3 档,`tool 强制` 12/12 schema 通过。但**三档都是 12/12**——详见 `notes/2026-09-14.md`。
