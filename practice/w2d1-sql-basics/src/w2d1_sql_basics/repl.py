"""SQL 交互练习台:输一行 SQL 看结果。"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "school.db"
conn = sqlite3.connect(DB_PATH)
print(f"已打开 {DB_PATH.name},输入 SQL(exit 退出):")
while True:
    sql = input("sql> ").strip()
    if not sql:
        continue
    if sql.lower() in ("exit", "quit"):
        break
    try:
        rows = conn.execute(sql).fetchall()
        for r in rows:
            print(r)
        print(f"── {len(rows)} 行")
    except Exception as e:
        print(f"[ERR] {type(e).__name__}: {e}")