-- schema.sql:PG 版 school 建表(对比昨天 SQLite 的 setup.py)
CREATE TABLE students (
    id SERIAL PRIMARY KEY,          -- SQLite: INTEGER PRIMARY KEY
    name TEXT NOT NULL,
    class_id INTEGER NOT NULL
);
CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    credit NUMERIC(3,1) NOT NULL    -- SQLite: REAL
);
CREATE TABLE enrollments (
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    score NUMERIC(4,1),             -- NULL = 缺考
    PRIMARY KEY (student_id, course_id)
);