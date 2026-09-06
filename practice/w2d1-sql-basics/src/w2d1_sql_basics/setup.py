"""建库播种:3 张表(学生/课程/选课)+ 示例数据。"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "school.db"   # 项目根目录

def create_db():
    if DB_PATH.exists():
        DB_PATH.unlink()          # 重复跑时重建,保证数据一致
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE students (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        class_id INTEGER NOT NULL
    );
    CREATE TABLE courses (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        credit REAL NOT NULL
    );
    CREATE TABLE enrollments (
        student_id INTEGER NOT NULL,
        course_id INTEGER NOT NULL,
        score REAL,                          -- NULL = 缺考
        PRIMARY KEY (student_id, course_id)
    );
    """)
    students = [(1, "张伟", 1), (2, "李娜", 1), (3, "王强", 2),
                (4, "赵敏", 2), (5, "陈晨", 2), (6, "刘洋", 1)]
    courses = [(1, "语文", 4), (2, "数学", 4), (3, "英语", 3), (4, "体育", 1)]
    enrollments = [
        (1, 1, 92), (1, 2, 85), (1, 3, 88),
        (2, 1, 78), (2, 2, None), (2, 4, 90),      # 李娜数学缺考
        (3, 1, 61), (3, 2, 95), (3, 3, 73),
        (4, 2, 82), (4, 3, None),                  # 赵敏英语缺考
        (5, 1, 55), (5, 2, 68), (5, 3, 70), (5, 4, 88),
        (6, 1, None), (6, 2, 66),                  # 刘洋语文缺考
    ]
    cur.executemany("INSERT INTO students VALUES (?, ?, ?)", students)
    cur.executemany("INSERT INTO courses VALUES (?, ?, ?)", courses)
    cur.executemany("INSERT INTO enrollments VALUES (?, ?, ?)", enrollments)
    conn.commit()
    conn.close()
    print(f"[OK] 已建库 {DB_PATH}")

if __name__ == "__main__":
    create_db()