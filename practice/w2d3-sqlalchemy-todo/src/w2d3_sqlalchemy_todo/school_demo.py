"""school_demo.py:给 school 三张表写 ORM 模型,体会 relationship。"""
from decimal import Decimal

from sqlalchemy import ForeignKey, String, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship

engine = create_engine(
    "postgresql+psycopg://postgres:postgres@localhost:5432/school", echo=True
)

class Base(DeclarativeBase):
    pass

class Student(Base):
    __tablename__ = "students"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    class_id: Mapped[int]
    enrollments: Mapped[list["Enrollment"]] = relationship(back_populates="student")

class Course(Base):
    __tablename__ = "courses"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    credit: Mapped[Decimal]              # NUMERIC 列 ↔ Python Decimal(精确小数)
    enrollments: Mapped[list["Enrollment"]] = relationship(back_populates="course")

class Enrollment(Base):
    __tablename__ = "enrollments"
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), primary_key=True)
    score: Mapped[Decimal | None]        # NULL = 缺考
    student: Mapped[Student] = relationship(back_populates="enrollments")
    course: Mapped[Course] = relationship(back_populates="enrollments")

with Session(engine) as db:
    # 1. 张伟的所有选课(等价周一 JOIN 三表的 SQL,但不用写 JOIN):
    zhangwei = db.scalar(select(Student).where(Student.name == "张伟"))
    for e in zhangwei.enrollments:       # 访问属性 = 自动发查询(lazy load)
        print(f"[1] {e.course.name}: {e.score}")

    # 2. 反向走:数学课有哪些人选了:
    math = db.scalar(select(Course).where(Course.name == "数学"))
    for e in math.enrollments:
        print(f"[2] {e.student.name}: {e.score}")

    # 3. 每个学生的平均分(ORM 版 GROUP BY,呼应周一 challenge 第 2 题):
    rows = db.execute(
        select(Student.name, func.avg(Enrollment.score).label("avg"))
        .join(Enrollment)
        .group_by(Student.id)
        .order_by(Student.id)
    ).all()
    for name, avg in rows:
        print(f"[3] {name}: {avg:.2f}")

    rows_1 = db.execute(
        select(Student.name, func.avg(Enrollment.score).label("avg"))
        .where(Student.class_id == 1)
        .join(Enrollment)
        .group_by(Student.id)
        .order_by(Student.id)
    ).all()
    for name, avg in rows_1:
        print(f"[4] {name}: {avg:.2f}")

    db.add(Student(name="新同学", class_id=1))
    db.commit()