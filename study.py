# -*- coding: utf-8 -*-
"""学习任务自动化工具 · study.py

用法(在任意目录执行,python study.py <命令>):
  python study.py today            查看今日任务(文件不存在则自动从计划生成)
  python study.py done 3 备注      标记任务 3 完成(备注可选,可写踩坑心得)
  python study.py note 3 补充内容   给任务 3 追加一条备注
  python study.py next             学有余力:把下一个计划日追加进今日清单
  python study.py add 描述//验收    加一个计划外的任务(用 // 分隔验收标准)
  python study.py undo 3           取消任务 3 的完成标记
  python study.py skip 3           跳过任务 3(不做了,进度指针越过它)
  python study.py remove 3         从今日清单删掉任务 3(仅限未完成/已跳过的)
  python study.py sync [日期]      同步清单:读取你手动打的勾,规范化标题与状态
  python study.py finish [--draft] 今日结束:生成学习笔记(骨架)+ 提交推送 GitHub
  python study.py publish [日期]    把指定日期的笔记+任务文件提交并推送
  python study.py log              最近完成记录(简历素材)
  python study.py --selftest       自检:解析计划文档 + 显示进度指针

设计说明:
  - 数据来源:桌面《AI应用开发工程师_技术栈与学习计划.md》第 2 节(只读)
  - 任务文件:tasks/今日任务_YYYY-MM-DD.md(按实际日期,一天可含多个计划日)
  - 状态全部从任务文件推导(✅/⏭️ 标记),tasks/.progress.json 只存跳过的计划
  - 推送走 ~/.ssh/config 里的 SSH 443 通道,本脚本不处理网络
"""

import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

# ---------------------------------------------------------------- 常量

PLAN_PATH = Path(r"C:\Users\l1540\Desktop\AI应用开发工程师_技术栈与学习计划.md")
REPO_DIR = Path(__file__).resolve().parent            # 脚本在仓库根,与 cwd 无关
TASKS_DIR = REPO_DIR / "tasks"
NOTES_DIR = REPO_DIR / "notes"
STATE_FILE = TASKS_DIR / ".progress.json"             # 只存 skipped_keys

WEEKDAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

STATUS_SUFFIX = {"done": " ✅ 已完成", "skipped": " ⏭️ 已跳过", "pending": ""}

IRON_RULES = [
    "周日综合练习提交 GitHub",
    "每天 5 行学习笔记(本文件顶部「今日 5 行速记」)",
    "卡壳 30 分钟就问 AI",
]


def today_str() -> str:
    return date.today().isoformat()


def weekday_cn(d: date) -> str:
    return WEEKDAYS[d.weekday()]


def plan_line(key: str) -> str:
    """计划 key('1-周二') → 文件里的标记行('第 1 周·周二')。"""
    week, day = key.split("-")
    return f"第 {week} 周·{day}"


# ---------------------------------------------------------------- 计划解析

def load_plan():
    """解析桌面计划文档第 2 节,返回 42 条计划条目。

    每条:week(周) / week_title(周主题) / day(周一~周日) / title(主题) /
    content(任务内容) / accept(产出/验收) / hours(用时) / kind(普通|综合练习|里程碑)
    """
    text = PLAN_PATH.read_text(encoding="utf-8")
    plan = []
    week, week_title, in_sec2 = 0, "", False
    for line in text.splitlines():
        if line.startswith("## 2."):
            in_sec2 = True
            continue
        if line.startswith("## 3."):
            break
        if not in_sec2:
            continue
        m = re.match(r"### 第 (\d+) 周:(.+)", line)
        if m:
            week = int(m.group(1))
            week_title = m.group(2).strip()
            continue
        if not line.startswith("| 周"):          # 表格行:以「| 周一」等开头
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 4:
            continue
        day, task_cell, accept, hours = cells
        raw = task_cell.replace("**", "")
        kind = "普通"
        if raw.startswith("综合练习:"):
            kind, title, content = "综合练习", "综合练习", raw.split(":", 1)[1].strip()
        elif raw.startswith("里程碑:"):
            kind, title, content = "里程碑", "里程碑", raw.split(":", 1)[1].strip()
        elif ":" in raw:
            title, content = raw.split(":", 1)
            title, content = title.strip(), content.strip()
        else:
            title, content = raw, ""
        plan.append(dict(week=week, week_title=week_title, day=day,
                         title=title, content=content, accept=accept,
                         hours=hours, kind=kind))
    return plan


def plan_key(item) -> str:
    return f"{item['week']}-{item['day']}"


# ---------------------------------------------------------------- 任务文件

def task_file(d: str) -> Path:
    return TASKS_DIR / f"今日任务_{d}.md"


def parse_tasks(path: Path):
    """解析任务文件 → (header, tasks)

    task 字段:num / title / status(done|skipped|pending) /
    plan_key(如 '1-周二',自定义任务为 None) / accept / checkboxes[(状态,文本)] /
    notes[备注行] / extra[保留的原始附加行,如「完成验收」节,重写时不丢]
    """
    text = path.read_text(encoding="utf-8")
    header_lines, tasks, cur = [], [], None
    for line in text.splitlines():
        m = re.match(r"^## 任务 (\d+):(.+)$", line)
        if m:
            title = m.group(2).strip()
            header_status = "pending"
            # 兼容后缀前有无空格、以及历史上可能重复的后缀
            for st, suf in (("done", " ✅ 已完成"), ("skipped", " ⏭️ 已跳过")):
                suf = suf.strip()
                while title.rstrip().endswith(suf):
                    header_status = st
                    title = title.rstrip()[:-len(suf)].strip()
            cur = dict(num=int(m.group(1)), title=title,
                       header_status=header_status, status="pending",
                       plan_key=None, accept="", checkboxes=[], notes=[], extra=[])
            tasks.append(cur)
            continue
        if cur is None:
            header_lines.append(line)
            continue
        s = line.strip()
        mcb = re.match(r"^- \[(.)\] (.*)$", s)          # - [x] / - [ ] / - [-]
        if mcb:
            mark = {"x": "done", " ": "pending", "-": "skipped"}[mcb.group(1)]
            cur["checkboxes"].append((mark, mcb.group(2).strip()))
            continue
        mp = re.match(r"- 计划:第 (\d+) 周·(周.)", s)
        if mp:
            cur["plan_key"] = f"{int(mp.group(1))}-{mp.group(2)}"
            continue
        if s.startswith("- 验收:"):
            cur["accept"] = s[len("- 验收:"):].strip()
            continue
        if s.startswith("- 💬 备注:"):
            cur["notes"].append(s[len("- 💬 备注:"):].strip())
            continue
        if s:                                       # 其他非空行原样保留
            cur["extra"].append(s)
    for t in tasks:
        # 打勾是唯一的源操作:有勾看勾,标题上的 ✅/⏭️ 只作展示(sync 会统一重写)
        if t["checkboxes"]:
            marks = [cb[0] for cb in t["checkboxes"]]
            if "pending" in marks:
                t["status"] = "pending"
            elif all(m == "done" for m in marks):
                t["status"] = "done"
            elif all(m == "skipped" for m in marks):
                t["status"] = "skipped"
            else:
                t["status"] = "pending"
        else:
            t["status"] = t["header_status"]
        t.pop("header_status")
    return "\n".join(header_lines), tasks


def render_tasks(header: str, tasks) -> str:
    """按统一格式重建任务文件(程序是唯一写手,格式永远规整)。"""
    out = [header.rstrip(), ""]
    for t in tasks:
        out.append(f"## 任务 {t['num']}:{t['title']}{STATUS_SUFFIX[t['status']]}")
        out.append("")
        if t["plan_key"]:
            out.append(f"- 计划:{plan_line(t['plan_key'])}")
            out.append(f"- 验收:{t['accept']}")
        for cb_mark, cb_text in t["checkboxes"]:
            # 任务级状态:done/skipped 统一勾选样式;pending 保留用户手打的每个勾
            if t["status"] != "pending":
                cb_mark = t["status"]
            mark = {"done": "[x]", "skipped": "[-]", "pending": "[ ]"}[cb_mark]
            out.append(f"- {mark} {cb_text}")
        for n in t["notes"]:
            out.append(f"- 💬 备注:{n}")
        for e in t["extra"]:
            out.append(e)
        out.append("")
    return "\n".join(out)


def all_seen_keys():
    """所有任务文件里出现过的计划条目(无论完成与否)。"""
    keys = set()
    if TASKS_DIR.exists():
        for p in TASKS_DIR.glob("今日任务_*.md"):
            _, tasks = parse_tasks(p)
            keys |= {t["plan_key"] for t in tasks if t["plan_key"]}
    return keys


def completed_keys():
    keys = set()
    if TASKS_DIR.exists():
        for p in TASKS_DIR.glob("今日任务_*.md"):
            _, tasks = parse_tasks(p)
            keys |= {t["plan_key"] for t in tasks
                     if t["plan_key"] and t["status"] == "done"}
    return keys


def pending_from_previous_files(exclude: str):
    """之前日期文件里还没处理的任务(顺延到今天的候选)。"""
    out = []
    if TASKS_DIR.exists():
        for p in sorted(TASKS_DIR.glob("今日任务_*.md")):
            if p.name == f"今日任务_{exclude}.md":
                continue
            _, tasks = parse_tasks(p)
            out += [t for t in tasks if t["status"] == "pending"]
    return out


def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {"skipped_keys": []}


def save_state(state):
    TASKS_DIR.mkdir(exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2),
                          encoding="utf-8")


def pointer_item():
    """进度指针:第一条既没出现过、也没被跳过的计划条目。"""
    plan = load_plan()
    seen = all_seen_keys() | set(load_state()["skipped_keys"])
    for item in plan:
        if plan_key(item) not in seen:
            return item
    return None


def next_num(tasks) -> int:
    return max((t["num"] for t in tasks), default=0) + 1


def make_header(d: str) -> str:
    return (f"# 今日任务清单 · {d}({weekday_cn(date.fromisoformat(d))})\n"
            "\n> 目标:逐项完成并在节标题后打 ✅。完成后跟 Claude 说「完成 XX 任务」,\n"
            "> 或自己跑 python study.py done <编号>。全部完成可 python study.py next 继续下一日。")


def task_from_item(item, num: int):
    return dict(num=num, title=item["title"],
                plan_key=plan_key(item), accept=item["accept"],
                checkboxes=[("pending", item["content"])],
                status="pending", notes=[], extra=[])


def find_today_tasks(d: str):
    """返回 (header, tasks),今日文件不存在则自动生成(顺延+指针)。"""
    path = task_file(d)
    if not path.exists():
        TASKS_DIR.mkdir(exist_ok=True)
        header, tasks = make_header(d), []
        for t in pending_from_previous_files(exclude=d):   # 顺延没做完的
            tasks.append(dict(t, num=next_num(tasks)))
        item = pointer_item()                              # 新的计划日
        if item:
            tasks.append(task_from_item(item, next_num(tasks)))
        path.write_text(render_tasks(header, tasks), encoding="utf-8")
    return parse_tasks(path)


def print_today(header, tasks):
    print(header.splitlines()[0])
    if not tasks:
        print("📭 暂无任务(计划条目全部处理完?跑 study.py --selftest 看看)")
        return
    done_n = sum(1 for t in tasks if t["status"] == "done")
    for t in tasks:
        icon = {"done": "✅", "skipped": "⏭️", "pending": "⬜"}[t["status"]]
        origin = f"({plan_line(t['plan_key'])})" if t["plan_key"] else "(自定义)"
        print(f"  {icon} {t['num']:>2}. {t['title']}{origin}")
    all_done = done_n == len(tasks)
    print(f"\n完成 {done_n}/{len(tasks)}"
          + (" 🎉 全部完成!可 python study.py next 继续" if all_done else ""))


# ---------------------------------------------------------------- 各命令

def _get_task(tasks, num):
    for t in tasks:
        if t["num"] == num:
            return t
    print(f"❌ 找不到任务编号 {num},先跑 study.py today 看编号")
    sys.exit(1)


def _rewrite(path, header, tasks):
    path.write_text(render_tasks(header, tasks), encoding="utf-8")


def cmd_today():
    header, tasks = find_today_tasks(today_str())
    print_today(header, tasks)


def cmd_done(args):
    if not args:
        print("用法:python study.py done <编号> [备注]")
        sys.exit(1)
    num, note = int(args[0]), " ".join(args[1:]).strip()
    d = today_str()
    header, tasks = find_today_tasks(d)
    t = _get_task(tasks, num)
    if t["status"] == "done":
        print(f"⚠️ 任务 {num} 已标记完成,无需重复")
        sys.exit(1)
    t["status"] = "done"
    if note:
        t["notes"].append(note)
    _rewrite(task_file(d), header, tasks)
    print(f"✅ 任务 {num}「{t['title']}」已标记完成({d})")
    if note:
        print(f"💬 备注已记录:{note}")
    if not [x for x in tasks if x["status"] == "pending"]:
        print("🎉 今日任务全部完成!学有余力 → python study.py next")


def cmd_note(args):
    if len(args) < 2:
        print("用法:python study.py note <编号> <备注内容>")
        sys.exit(1)
    num, note = int(args[0]), " ".join(args[1:]).strip()
    d = today_str()
    header, tasks = find_today_tasks(d)
    t = _get_task(tasks, num)
    t["notes"].append(note)
    _rewrite(task_file(d), header, tasks)
    print(f"💬 已给任务 {num} 追加备注:{note}")


def cmd_next():
    d = today_str()
    header, tasks = find_today_tasks(d)
    item = pointer_item()
    if item is None:
        print("🎉 6 周计划已全部走完,没有下一个计划日了!")
        sys.exit(0)
    tasks.append(task_from_item(item, next_num(tasks)))
    _rewrite(task_file(d), header, tasks)
    print(f"📥 已把「第 {item['week']} 周·{item['day']}」追加进今日清单:")
    print(f"   {item['title']}——{item['content']}")
    print(f"   验收:{item['accept']}({item['hours']})")


def cmd_add(args):
    if not args:
        print("用法:python study.py add <任务描述>//<验收标准>")
        sys.exit(1)
    desc, accept = (" ".join(args).split("//", 1) + [""])[:2]
    desc, accept = desc.strip(), accept.strip()
    d = today_str()
    header, tasks = find_today_tasks(d)
    tasks.append(dict(num=next_num(tasks), title=desc, status="pending",
                      plan_key=None, accept=accept,
                      checkboxes=[("pending", desc)], notes=[], extra=[]))
    _rewrite(task_file(d), header, tasks)
    print(f"➕ 已添加自定义任务:{desc}" + (f"(验收:{accept})" if accept else ""))


def cmd_undo(args):
    if not args:
        print("用法:python study.py undo <编号>")
        sys.exit(1)
    num = int(args[0])
    d = today_str()
    header, tasks = find_today_tasks(d)
    t = _get_task(tasks, num)
    t["status"] = "pending"
    _rewrite(task_file(d), header, tasks)
    print(f"↩️ 任务 {num}「{t['title']}」已恢复为未完成")


def cmd_sync(args):
    """读取用户手打的勾,把文件规范成统一格式(标题 ✅、状态一致)。"""
    d = args[0] if args else today_str()
    path = task_file(d)
    if not path.exists():
        print(f"❌ {d} 没有任务文件。先跑 study.py today 生成")
        sys.exit(1)
    header, tasks = parse_tasks(path)
    _rewrite(path, header, tasks)
    print(f"🔄 已同步 {path.name} 的打勾状态:")
    print_today(header, tasks)


def cmd_remove(args):
    if not args:
        print("用法:python study.py remove <编号>(仅限未完成/已跳过的任务)")
        sys.exit(1)
    num = int(args[0])
    d = today_str()
    header, tasks = find_today_tasks(d)
    t = _get_task(tasks, num)
    if t["status"] == "done":
        print(f"⚠️ 任务 {num} 已完成,不能删。想重做先 python study.py undo {num}")
        sys.exit(1)
    tasks.remove(t)
    _rewrite(task_file(d), header, tasks)
    print(f"🗑️ 任务 {num}「{t['title']}」已从今日清单删除")


def cmd_skip(args):
    if not args:
        print("用法:python study.py skip <编号>(跳过该任务,进度指针越过它)")
        sys.exit(1)
    num = int(args[0])
    d = today_str()
    header, tasks = find_today_tasks(d)
    t = _get_task(tasks, num)
    t["status"] = "skipped"
    _rewrite(task_file(d), header, tasks)
    if t["plan_key"]:
        state = load_state()
        if t["plan_key"] not in state["skipped_keys"]:
            state["skipped_keys"].append(t["plan_key"])
            save_state(state)
    print(f"⏭️ 任务 {num}「{t['title']}」已跳过")
    if not [x for x in tasks if x["status"] == "pending"]:
        print("🎉 今日任务已全部处理!可 python study.py next 继续")


# ---------------------------------------------------------------- 笔记生成

def collect_note_hits(tasks):
    """备注里找坑/解法素材:含关键词的备注行优先。"""
    all_notes = [n for t in tasks for n in t["notes"]]
    pit = next((n for n in all_notes if re.search(r"坑|报错|失败|问题", n)), None)
    fix = next((n for n in all_notes if re.search(r"解决|解法|方案|办法", n) and n != pit), None)
    return pit, fix


def build_note(d: str, tasks, item_next):
    done = [t for t in tasks if t["status"] == "done"]
    pending = [t for t in tasks if t["status"] == "pending"]
    skipped = [t for t in tasks if t["status"] == "skipped"]
    pit, fix = collect_note_hits(done)
    learned = "、".join(t["title"] for t in done) if done else "【无】"
    tomorrow = (f"{item_next['title']}({item_next['content']})"
                if item_next else "【6 周计划已全部完成】")
    origin = "、".join(sorted({plan_line(t["plan_key"]) for t in done if t["plan_key"]}))
    custom = "、".join(t["title"] for t in done if not t["plan_key"])
    date_obj = date.fromisoformat(d)

    lines = [f"# 学习笔记 · {d} {weekday_cn(date_obj)}(计划进度:{origin or '自定义'})", "",
             "## 今日 5 行速记", "",
             f"1. **学了**:{learned}",
             f"2. **核心坑**:{pit if pit else '【待补充:今天踩了什么坑?】'}",
             f"3. **硬核解法**:{fix if fix else '【待补充:怎么解决的?】'}",
             f"4. **顺手解决**:{custom if custom else '【无】'}",
             f"5. **明天**:{tomorrow}", "",
             "---", "",
             "## 今日完成事项", "",
             "| 任务 | 结果 |", "|---|---|"]
    for t in done:
        origin_t = f"({plan_line(t['plan_key'])})" if t["plan_key"] else ""
        lines.append(f"| {t['title']}{origin_t} | ✅ 已完成 |")
    if skipped:
        lines += ["", "## 已跳过"]
        for t in skipped:
            origin_t = f"({plan_line(t['plan_key'])})" if t["plan_key"] else "(自定义)"
            lines.append(f"- {t['title']}{origin_t}")
    if pending:
        lines += ["", "## 未完成(顺延)"]
        for t in pending:
            origin_t = f"({plan_line(t['plan_key'])})" if t["plan_key"] else "(自定义)"
            lines.append(f"- {t['title']}{origin_t}")
    lines += ["", "---", "",
              "## 常用命令速查(今天实际用过的)", "",
              "【待补充:今天敲过的命令记在这里,回头翻最有用】", "",
              "---", "",
              "## 明天计划", ""]
    if item_next:
        lines.append(f"- {item_next['week_title']} · {item_next['day']}:"
                     f"{item_next['title']}——{item_next['content']}")
        lines.append(f"- 验收:{item_next['accept']}({item_next['hours']})")
    else:
        lines.append("- 6 周计划全部完成,进入项目实战阶段")
    lines += ["", "---", "", "## 每周铁律", ""]
    lines += [f"{i}. {r}" for i, r in enumerate(IRON_RULES, 1)]
    lines.append("")
    return "\n".join(lines)


def git_run(*args):
    r = subprocess.run(["git", "-C", str(REPO_DIR), *args],
                       capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        print(f"❌ git {' '.join(args)} 失败:\n{r.stderr}")
        sys.exit(1)
    return (r.stdout or "").strip()


def cmd_publish(args):
    d = args[0] if args else today_str()
    if not task_file(d).exists() and not (NOTES_DIR / f"{d}.md").exists():
        print(f"❌ {d} 没有任务文件也没有笔记,没东西可推")
        sys.exit(1)
    # 推送前先把所有任务文件的手动打勾同步成规范格式(幂等,无改动时不产生 diff)
    if TASKS_DIR.exists():
        for p in TASKS_DIR.glob("今日任务_*.md"):
            h, ts = parse_tasks(p)
            _rewrite(p, h, ts)
    git_run("add", "tasks", "notes")
    r = subprocess.run(["git", "-C", str(REPO_DIR), "commit",
                        "-m", f"docs: {d} 学习笔记"],
                       capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        # git 的 "nothing to commit" 输出在 stdout,报错在 stderr,两边都查
        if ("nothing to commit" in r.stdout + r.stderr
                or "no changes added" in r.stdout + r.stderr):
            print("📭 没有新改动,无需推送")
            sys.exit(0)
        print(f"❌ git commit 失败:\n{r.stdout}\n{r.stderr}")
        sys.exit(1)
    out = git_run("push")
    print(f"🚀 已推送 GitHub:\n{out}")


def cmd_finish(args):
    draft = "--draft" in args
    d = today_str()
    path = task_file(d)
    if not path.exists():
        print(f"❌ 今天({d})还没有任务文件。先跑 study.py today 生成")
        sys.exit(1)
    header, tasks = parse_tasks(path)
    done = [t for t in tasks if t["status"] == "done"]
    if not done:
        print("❌ 今天一个任务都没完成,不生成笔记(已完成至少 1 个任务再收工)")
        sys.exit(1)
    note_path = NOTES_DIR / f"{d}.md"
    if note_path.exists():
        print(f"⚠️ {d} 的笔记已存在。要推送就跑:python study.py publish {d}")
        sys.exit(1)
    item_next = pointer_item()
    _rewrite(path, header, tasks)          # 生成笔记前先把打勾状态同步进任务文件
    NOTES_DIR.mkdir(exist_ok=True)
    note_path.write_text(build_note(d, tasks, item_next), encoding="utf-8")
    print(f"📝 已生成笔记骨架:{note_path}")
    print("   (5 行速记已自动起草,详细内容可在推送前补充)")
    if draft:
        print("   --draft:不推送。补充完细节后跑:python study.py publish")
        sys.exit(0)
    cmd_publish([d])


def cmd_log():
    if not TASKS_DIR.exists():
        print("📭 还没有任何任务记录")
        return
    for p in sorted(TASKS_DIR.glob("今日任务_*.md"), reverse=True):
        _, tasks = parse_tasks(p)
        done = [t for t in tasks if t["status"] == "done"]
        if not done:
            continue
        d = p.name[len("今日任务_"):-3]
        titles = "、".join(t["title"] for t in done)
        print(f"📅 {d}:完成 {len(done)} 项 → {titles}")


def cmd_selftest():
    plan = load_plan()
    print(f"✅ 计划文档解析成功:{PLAN_PATH}")
    print(f"   共 {len(plan)} 条计划条目(第 {plan[0]['week']}~{plan[-1]['week']} 周)")
    for item in plan[:3]:
        print(f"   示例:{plan_key(item)} {item['title']}——{item['content'][:30]}...")
    seen = all_seen_keys()
    completed = completed_keys()
    skipped = set(load_state()["skipped_keys"])
    print(f"\n📊 进度:已完成 {len(completed)} 条 / 已见过 {len(seen)} 条 / 跳过 {len(skipped)} 条")
    item = pointer_item()
    if item:
        print(f"📍 指针:下一个待学 = 第 {item['week']} 周·{item['day']}「{item['title']}」")
        print(f"   内容:{item['content']}")
        print(f"   验收:{item['accept']}({item['hours']})")
    else:
        print("📍 指针:计划已全部走完 🎉")


# ---------------------------------------------------------------- 入口

def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")   # 中文 + emoji 在 Windows 终端不乱码
    except Exception:
        pass
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(0)
    cmd, rest = args[0], args[1:]
    if cmd == "--selftest":
        cmd_selftest()
    elif cmd == "today":
        cmd_today()
    elif cmd == "done":
        cmd_done(rest)
    elif cmd == "note":
        cmd_note(rest)
    elif cmd == "next":
        cmd_next()
    elif cmd == "add":
        cmd_add(rest)
    elif cmd == "undo":
        cmd_undo(rest)
    elif cmd == "skip":
        cmd_skip(rest)
    elif cmd == "remove":
        cmd_remove(rest)
    elif cmd == "sync":
        cmd_sync(rest)
    elif cmd == "finish":
        cmd_finish(rest)
    elif cmd == "publish":
        cmd_publish(rest)
    elif cmd == "log":
        cmd_log()
    else:
        print(f"❌ 未知命令:{cmd}\n")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
