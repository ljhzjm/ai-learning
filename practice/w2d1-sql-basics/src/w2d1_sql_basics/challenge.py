"""验收挑战:独立手写 5 道查询。每题打印结果,与注释里的预期比对。"""
import sqlite3
from pathlib import Path

conn = sqlite3.connect(Path(__file__).resolve().parents[2] / "school.db")

def q(sql, note):
    print(f"\n── {note}")
    for r in conn.execute(sql).fetchall():
        print(r)

# 1. 基础:2 班所有学生姓名,按 id 升序     预期:王强 / 赵敏 / 陈晨
q("SELECT name FROM students WHERE class_id = 2 ORDER BY id", "题1:2 班学生姓名,按 id 升序")

# 2. 分组:平均分 ≥ 80 的学生 id 和平均分    预期:(1, 88.33) / (2, 84.0) / (4, 82.0)
q("""SELECT student_id, ROUND(AVG(score), 2) AS avg_score
     FROM enrollments GROUP BY student_id
     HAVING AVG(score) >= 80""", "题2:平均分 ≥80 的学生")

# 3. 子查询:没选「体育」的学生姓名          预期:张伟 / 王强 / 赵敏 / 刘洋
q("""SELECT name FROM students WHERE id NOT IN (
     SELECT student_id FROM enrollments WHERE course_id = 4)""", "题3A:NOT IN 子查询")

# 写法 B:LEFT JOIN + IS NULL(条件必须写进 ON,写进 WHERE 会把没选课的行也滤掉)
q("""SELECT s.name FROM students s
     LEFT JOIN enrollments e ON e.student_id = s.id AND e.course_id = 4
     WHERE e.student_id IS NULL""", "题3B:LEFT JOIN + IS NULL")

# 4. JOIN:列出每个学生「语文」成绩,缺考的显示 NULL  预期:张伟92 / 李娜78 / 王强61 / 陈晨55 / 刘洋None
q("""SELECT s.name, e.score
     FROM students s
     JOIN enrollments e ON e.student_id = s.id
     JOIN courses c ON c.id = e.course_id
     WHERE c.id = 1""", "题4:每个学生的语文成绩(缺考显示 NULL)")

# 5. EXPLAIN:给 enrollments(course_id) 建索引前后,各 EXPLAIN 一次
#    `SELECT * FROM enrollments WHERE course_id = 2`,说出扫描方式的变化
#    (注意:第 2 步已经给 student_id 建过索引,所以要用 course_id 才看得出对比)
print("\n── 题5:建索引前")
for r in conn.execute("EXPLAIN QUERY PLAN SELECT * FROM enrollments WHERE course_id = 2"):
    print(r)
conn.execute("CREATE INDEX idx_enr_course ON enrollments(course_id)")
print("\n── 题5:建索引后")
for r in conn.execute("EXPLAIN QUERY PLAN SELECT * FROM enrollments WHERE course_id = 2"):
    print(r)
