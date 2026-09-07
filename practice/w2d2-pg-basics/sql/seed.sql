-- 播种:6 学生 / 4 课程 / 17 条选课(与 w2d1 完全一致)
INSERT INTO students (id, name, class_id) VALUES
(1, '张伟', 1), (2, '李娜', 1), (3, '王强', 2),
(4, '赵敏', 2), (5, '陈晨', 2), (6, '刘洋', 1);

INSERT INTO courses (id, name, credit) VALUES
(1, '语文', 4), (2, '数学', 4), (3, '英语', 3), (4, '体育', 1);

INSERT INTO enrollments (student_id, course_id, score) VALUES
(1, 1, 92), (1, 2, 85), (1, 3, 88),
(2, 1, 78), (2, 2, NULL), (2, 4, 90),
(3, 1, 61), (3, 2, 95), (3, 3, 73),
(4, 2, 82), (4, 3, NULL),
(5, 1, 55), (5, 2, 68), (5, 3, 70), (5, 4, 88),
(6, 1, NULL), (6, 2, 66);