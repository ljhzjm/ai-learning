# ai-learning

AI 应用开发工程师学习仓库(6 周学习计划 + 项目实战)。

## 目录结构

```
ai-learning/
├── README.md
├── study.py         # 学习任务自动化工具(任务清单/笔记生成/自动推送)
├── tasks/           # 每日任务清单(按实际日期,自动生成与更新)
├── notes/           # 每日学习笔记(每天 5 行速记 + 详细记录)
└── ...              # 后续练习代码按周加入(week01/ week02/ ...)
```

## 学习自动化工具 study.py

任务清单与学习笔记的小管家:完成任务自动更新清单,一天可以连续推进多个计划日,收工时一键生成笔记并推送 GitHub。

### 每日使用循环

1. 开始学习:`python study.py today` 看今日任务(首次会自动从桌面学习计划生成)
2. 完成一个任务:跟 Claude 说「完成 XX」,或自己跑 `python study.py done <编号> 备注`
3. 学有余力:`python study.py next` 把下一个计划日接进来(不按日历走也没关系)
4. 收工:`python study.py finish` 生成当日笔记并推送到 GitHub

### 命令速查

| 命令 | 作用 |
|---|---|
| `python study.py today` | 查看今日任务(文件不存在则自动生成) |
| `python study.py done 3 备注` | 标记任务 3 完成(备注写踩坑心得,会进笔记) |
| `python study.py note 3 内容` | 给任务 3 追加一条备注 |
| `python study.py next` | 把下一个计划日追加进今日清单 |
| `python study.py add 描述//验收` | 加一个计划外任务 |
| `python study.py undo 3` / `skip 3` / `remove 3` | 取消完成 / 跳过(指针越过)/ 删除 |
| `python study.py finish [--draft]` | 今日结束:生成笔记 + 提交推送(--draft 只生成不推) |
| `python study.py publish [日期]` | 手动把指定日期的笔记+任务推送 |
| `python study.py log` | 最近完成记录(简历素材) |
| `python study.py --selftest` | 自检计划解析与进度指针 |

### 工作原理

- 计划数据源:桌面《AI应用开发工程师_技术栈与学习计划.md》(只读解析,42 条逐日任务)
- 进度状态全部从 `tasks/` 里的 ✅/⏭️ 标记推导,`.progress.json` 只记跳过的计划
- 任务文件按实际日期命名,一天可以包含多个计划日的任务
- 推送走本机 SSH 443 通道(见 notes/2026-08-31.md 的排查记录)

## 每周铁律

- 周日综合练习提交 GitHub
- 每天 5 行学习笔记
- 卡壳 30 分钟就问 AI
