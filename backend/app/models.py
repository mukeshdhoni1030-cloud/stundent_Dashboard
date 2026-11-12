
from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    ForeignKey,
    Numeric,
    UniqueConstraint,
    CheckConstraint
)

from app.database import Base


# ==========================================
# 1. USERS TABLE
# ==========================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "role IN ('student', 'teacher', 'principal')",
            name="valid_user_role"
        ),
    )


# ==========================================
# 2. CLASSES TABLE
# ==========================================

class Class(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    class_name = Column(String(30), nullable=False)
    section = Column(String(10), nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "class_name",
            "section",
            name="unique_class_section"
        ),
    )


# ==========================================
# 3. STUDENTS TABLE
# ==========================================

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)

    name = Column(String(100), nullable=False)
    roll_no = Column(String(30), nullable=False)
    parent_name = Column(String(100))
    parent_phone = Column(String(20))

    __table_args__ = (
        UniqueConstraint(
            "class_id",
            "roll_no",
            name="unique_student_roll"
        ),
    )


# ==========================================
# 4. TEACHERS TABLE
# ==========================================

class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    name = Column(String(100), nullable=False)
    qualification = Column(String(100))
    phone = Column(String(20))


# ==========================================
# 5. SUBJECTS TABLE
# ==========================================

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    subject_name = Column(String(100), unique=True, nullable=False)


# ==========================================
# 6. TEACHER ASSIGNMENTS TABLE
# ==========================================

class TeacherAssignment(Base):
    __tablename__ = "teacher_assignments"

    id = Column(Integer, primary_key=True, index=True)

    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "teacher_id",
            "class_id",
            "subject_id",
            name="unique_teacher_assignment"
        ),
    )


# ==========================================
# 7. STUDENT ATTENDANCE TABLE
# ==========================================

class StudentAttendance(Base):
    __tablename__ = "student_attendance"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)

    date = Column(Date, nullable=False)
    status = Column(String(20), nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "date",
            name="unique_student_attendance"
        ),
        CheckConstraint(
            "status IN ('present', 'absent', 'late')",
            name="valid_student_attendance"
        ),
    )


# ==========================================
# 8. TEACHER ATTENDANCE TABLE
# ==========================================

class TeacherAttendance(Base):
    __tablename__ = "teacher_attendance"

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)

    date = Column(Date, nullable=False)
    status = Column(String(20), nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "teacher_id",
            "date",
            name="unique_teacher_attendance"
        ),
        CheckConstraint(
            "status IN ('present', 'absent', 'late')",
            name="valid_teacher_attendance"
        ),
    )


# ==========================================
# 9. EXAMS TABLE
# ==========================================

class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True)
    exam_name = Column(String(100), nullable=False)
    exam_date = Column(Date, nullable=False)


# ==========================================
# 10. MARKS TABLE
# ==========================================

class Mark(Base):
    __tablename__ = "marks"

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)

    marks_obtained = Column(Numeric(6, 2), nullable=False)
    max_marks = Column(Numeric(6, 2), nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "exam_id",
            "subject_id",
            name="unique_student_exam_subject"
        ),
        CheckConstraint(
            "marks_obtained >= 0 AND max_marks > 0 AND marks_obtained <= max_marks",
            name="valid_exam_marks"
        ),
    )


# ==========================================
# 11. FEES TABLE
# ==========================================

class Fee(Base):
    __tablename__ = "fees"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)

    total_fee = Column(Numeric(10, 2), nullable=False)
    paid_amount = Column(Numeric(10, 2), default=0, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "total_fee >= 0 AND paid_amount >= 0 AND paid_amount <= total_fee",
            name="valid_fee_amount"
        ),
    )


# ==========================================
# 12. SALARIES TABLE
# ==========================================

class Salary(Base):
    __tablename__ = "salaries"

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)

    salary_month = Column(Date, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "teacher_id",
            "salary_month",
            name="unique_teacher_salary_month"
        ),
        CheckConstraint(
            "amount >= 0",
            name="valid_salary_amount"
        ),
    )
