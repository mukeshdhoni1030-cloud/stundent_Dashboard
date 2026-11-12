
from app.database import SessionLocal
from app.models import (
    User,
    Student,
    Teacher,
    Class as SchoolClass,
    Subject,
    TeacherAssignment
)
from app.security import get_password_hash


db = SessionLocal()

try:
    # ==================================
    # 1. CREATE A SCHOOL CLASS
    # ==================================

    school_class = db.query(SchoolClass).filter(
        SchoolClass.class_name == "10",
        SchoolClass.section == "A"
    ).first()

    if school_class is None:
        school_class = SchoolClass(
            class_name="10",
            section="A"
        )
        db.add(school_class)
        db.commit()
        db.refresh(school_class)

    # ==================================
    # 2. CREATE A SUBJECT
    # ==================================

    subject = db.query(Subject).filter(
        Subject.subject_name == "Mathematics"
    ).first()

    if subject is None:
        subject = Subject(subject_name="Mathematics")
        db.add(subject)
        db.commit()
        db.refresh(subject)

    # ==================================
    # 3. CREATE PRINCIPAL ACCOUNT
    # ==================================

    principal = db.query(User).filter(
        User.email == "principal@school.com"
    ).first()

    if principal is None:
        principal = User(
            email="principal@school.com",
            password_hash=get_password_hash("Principal@123"),
            role="principal"
        )
        db.add(principal)

    # ==================================
    # 4. CREATE STUDENT ACCOUNT
    # ==================================

    student_user = db.query(User).filter(
        User.email == "student@school.com"
    ).first()

    if student_user is None:
        student_user = User(
            email="student@school.com",
            password_hash=get_password_hash("Student@123"),
            role="student"
        )
        db.add(student_user)
        db.commit()
        db.refresh(student_user)

    student_profile = db.query(Student).filter(
        Student.user_id == student_user.id
    ).first()

    if student_profile is None:
        student_profile = Student(
            user_id=student_user.id,
            class_id=school_class.id,
            name="Ravi Kumar",
            roll_no="1001",
            parent_name="Ramesh Kumar",
            parent_phone="9876543210"
        )
        db.add(student_profile)

    # ==================================
    # 5. CREATE TEACHER ACCOUNT
    # ==================================

    teacher_user = db.query(User).filter(
        User.email == "teacher@school.com"
    ).first()

    if teacher_user is None:
        teacher_user = User(
            email="teacher@school.com",
            password_hash=get_password_hash("Teacher@123"),
            role="teacher"
        )
        db.add(teacher_user)
        db.commit()
        db.refresh(teacher_user)

    teacher_profile = db.query(Teacher).filter(
        Teacher.user_id == teacher_user.id
    ).first()

    if teacher_profile is None:
        teacher_profile = Teacher(
            user_id=teacher_user.id,
            name="Suresh Kumar",
            qualification="M.Sc Mathematics",
            phone="9876543211"
        )
        db.add(teacher_profile)
        db.commit()
        db.refresh(teacher_profile)

    # ==================================
    # 6. ASSIGN TEACHER TO CLASS AND SUBJECT
    # ==================================

    assignment = db.query(TeacherAssignment).filter(
        TeacherAssignment.teacher_id == teacher_profile.id,
        TeacherAssignment.class_id == school_class.id,
        TeacherAssignment.subject_id == subject.id
    ).first()

    if assignment is None:
        assignment = TeacherAssignment(
            teacher_id=teacher_profile.id,
            class_id=school_class.id,
            subject_id=subject.id
        )
        db.add(assignment)

    db.commit()

    print("================================")
    print("TEST ACCOUNTS CREATED SUCCESSFULLY")
    print("================================")
    print("Principal: principal@school.com")
    print("Password:  Principal@123")
    print()
    print("Student:   student@school.com")
    print("Password:  Student@123")
    print()
    print("Teacher:   teacher@school.com")
    print("Password:  Teacher@123")
    print("================================")

except Exception as error:
    db.rollback()
    print("ERROR:", error)

finally:
    db.close()
