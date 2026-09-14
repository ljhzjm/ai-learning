# w3d3-prompt-basics

第 3 周·周三:Prompt 四要素(角色/指令/约束/few-shot)控制变量实验。

## 运行

在项目根目录执行(需要 `.env` 里的 `LLM_API_KEY`):

```powershell
uv run python -m w3d3_prompt_basics.exp1_role        # 实验1 角色对比    4 次调用
uv run python -m w3d3_prompt_basics.exp2_constraint  # 实验2 约束对比    3 次调用
uv run python -m w3d3_prompt_basics.exp3_fewshot     # 实验3 few-shot    16 次调用
uv run python -m w3d3_prompt_basics.extract          # 信息抽取对比      12 次调用
```

控制台若报 `UnicodeEncodeError`(模型爱吐 emoji,GBK 控制台装不下),
先 `$env:PYTHONUTF8=1` 再跑,或依赖各脚本里已有的 `errors="replace"` 兜底。

## 目录

- `ask.py` —— 公共请求函数 `ask()` / `system_user()`,四个实验共用
- `exp1~3` / `extract` —— 三组对比实验 + 信息抽取
- 实验结论写在 `notes/2026-09-14.md`
