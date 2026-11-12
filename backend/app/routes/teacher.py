
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    User,
    Teacher,
    TeacherAssignment,
    Student,
    StudentAttendance,
    TeacherAttendance,
    Mark,
    Exam,
    Subject
)
from app.schemas import AttendanceCreate, MarksCreate
from app.dependencies import require_teacher

router = APIRouter(
    prefix="/teacher",
    tags=["Teacher Dashboard"]
)


# ==================================
# FIND THE LOGGED-IN TEACHER
# ==================================

def get_teacher_record(current_user: User, db: Session):
    teacher = db.query(Teacher).filter(
        Teacher.user_id == current_user.id
    ).first()

    if teacher is None:
        raise HTTPException(
            status_code=404,
            detail="Teacher profile not found"
        )

    return teacher


# ==================================
# CHECK TEACHER CLASS ASSIGNMENT
# ==================================

def check_teacher_class(
    teacher_id: int,
    class_id: int,
    db: Session
):
    assignment = db.query(TeacherAssignment).filter(
        TeacherAssignment.teacher_id == teacher_id,
        TeacherAssignment.class_id == class_id
    ).first()

    if assignment is None:
        raise HTTPException(
            status_code=403,
            detail="You are not assigned to this class"
        )


# ==================================
# 1. TEACHER PROFILE
# ==================================

@router.get("/me")
def get_teacher_profile(
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db)
):
    teacher = get_teacher_record(current_user, db)

    return {
        "id": teacher.id,
        "name": teacher.name,
        "email": current_user.email,
        "qualification": teacher.qualification,
        "phone": teacher.phone
    }


# ==================================
# 2. VIEW ASSIGNED CLASS STUDENTS
# ==================================

@router.get("/students")
def get_assigned_students(
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db)
):
    teacher = get_teacher_record(current_user, db)

    assignments = db.query(TeacherAssignment).filter(
        TeacherAssignment.teacher_id == teacher.id
    ).all()

    class_ids = list(set(
        assignment.class_id for assignment in assignments
    ))

    if not class_ids:
        return []

    students = db.query(Student).filter(
        Student.class_id.in_(class_ids)
    ).all()

    return [
        {
            "id": student.id,
            "name": student.name,
            "roll_no": student.roll_no,
            "class_id": student.class_id
        }
        for student in students
    ]


# ==================================
# 3. VIEW STUDENT ATTENDANCE BY DATE
# ==================================

@router.get("/attendance")
def get_student_attendance_by_date(
    attendance_date: date,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db)
):
    teacher = get_teacher_record(current_user, db)

    assignments = db.query(TeacherAssignment).filter(
        TeacherAssignment.teacher_id == teacher.id
    ).all()

    class_ids = list(set(
        assignment.class_id for assignment in assignments
    ))

    if not class_ids:
        return []

    records = (
        db.query(StudentAttendance, Student)
        .join(
            Student,
            Student.id == StudentAttendance.student_id
        )
        .filter(
            Student.class_id.in_(class_ids),
            StudentAttendance.date == attendance_date
        )
        .all()
    )

    return [
        {
            "student_id": student.id,
            "student_name": student.name,
            "roll_no": student.roll_no,
            "date": record.date,
            "status": record.status
        }
        for record, student in records
    ]


# ==================================
# 4. MARK STUDENT ATTENDANCE
# ==================================

@router.post("/attendance")
def mark_student_attendance(
    attendance_data: AttendanceCreate,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db)
):
    teacher = get_teacher_record(current_user, db)

    student = db.query(Student).filter(
        Student.id == attendance_data.student_id
    ).first()

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    check_teacher_class(
        teacher.id,
        student.class_id,
        db
    )

    existing_record = db.query(StudentAttendance).filter(
        StudentAttendance.student_id == student.id,
        StudentAttendance.date == attendance_data.attendance_date
    ).first()

    if existing_record:
        raise HTTPException(
            status_code=409,
            detail="Attendance already recorded for this date"
        )

    record = StudentAttendance(
        student_id=student.id,
        date=attendance_data.attendance_date,
        status=attendance_data.status
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "message": "Student attendance saved successfully",
        "attendance_id": record.id
    }


# ==================================
# 5. UPLOAD STUDENT MARKS
# ==================================

@router.post("/marks")
def upload_student_marks(
    marks_data: MarksCreate,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db)
):
    teacher = get_teacher_record(current_user, db)

    student = db.query(Student).filter(
        Student.id == marks_data.student_id
    ).first()

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    check_teacher_class(
        teacher.id,
        student.class_id,
        db
    )

    subject_assignment = db.query(TeacherAssignment).filter(
        TeacherAssignment.teacher_id == teacher.id,
        TeacherAssignment.class_id == student.class_id,
        TeacherAssignment.subject_id == marks_data.subject_id
    ).first()

    if subject_assignment is None:
        raise HTTPException(
            status_code=403,
            detail="You are not assigned to this subject"
        )

    exam = db.query(Exam).filter(
        Exam.id == marks_data.exam_id
    ).first()

    if exam is None:
        raise HTTPException(
            status_code=404,
            detail="Exam not found"
        )

    subject = db.query(Subject).filter(
        Subject.id == marks_data.subject_id
    ).first()

    if subject is None:
        raise HTTPException(
            status_code=404,
            detail="Subject not found"
        )

    if marks_data.marks_obtained > marks_data.max_marks:
        raise HTTPException(
            status_code=400,
            detail="Obtained marks cannot exceed maximum marks"
        )

    existing_mark = db.query(Mark).filter(
        Mark.student_id == student.id,
        Mark.exam_id == marks_data.exam_id,
        Mark.subject_id == marks_data.subject_id
    ).first()

    if existing_mark:
        raise HTTPException(
            status_code=409,
            detail="Marks already uploaded for this exam and subject"
        )

    mark = Mark(
        student_id=student.id,
        exam_id=marks_data.exam_id,
        subject_id=marks_data.subject_id,
        marks_obtained=marks_data.marks_obtained,
        max_marks=marks_data.max_marks
    )

    db.add(mark)
    db.commit()
    db.refresh(mark)

    return {
        "message": "Student marks uploaded successfully",
        "mark_id": mark.id
    }


# ==================================
# 6. VIEW TEACHER ATTENDANCE
# ==================================

@router.get("/attendance/me")
def get_my_attendance(
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db)
):
    teacher = get_teacher_record(current_user, db)

    records = db.query(TeacherAttendance).filter(
        TeacherAttendance.teacher_id == teacher.id
    ).order_by(TeacherAttendance.date.desc()).all()

    return [
        {
            "date": record.date,
            "status": record.status
        }
        for record in records
    ]


# ==================================
# 7. GET AVAILABLE EXAMS
# ==================================

@router.get("/exams")
def get_available_exams(
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db)
):
    exams = db.query(Exam).order_by(
        Exam.exam_date.desc()
    ).all()

    return [
        {
            "id": exam.id,
            "exam_name": exam.exam_name,
            "exam_date": exam.exam_date
        }
        for exam in exams
    ]


# ==================================
# 8. GET TEACHER ASSIGNED SUBJECTS
# ==================================

@router.get("/subjects")
def get_teacher_subjects(
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db)
):
    teacher = get_teacher_record(current_user, db)

    assignments = db.query(TeacherAssignment).filter(
        TeacherAssignment.teacher_id == teacher.id
    ).all()

    subject_ids = list(set(
        assignment.subject_id for assignment in assignments
    ))

    if not subject_ids:
        return []

    subjects = db.query(Subject).filter(
        Subject.id.in_(subject_ids)
    ).all()

    return [
        {
            "id": subject.id,
            "subject_name": subject.subject_name
        }
        for subject in subjects
    ]
