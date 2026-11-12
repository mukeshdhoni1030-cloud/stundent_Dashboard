
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    User,
    Student,
    StudentAttendance,
    Mark,
    Exam,
    Subject,
    Fee
)
from app.dependencies import require_student

router = APIRouter(
    prefix="/student",
    tags=["Student Dashboard"]
)


# ==================================
# FIND THE LOGGED-IN STUDENT
# ==================================

def get_student_record(current_user: User, db: Session):
    student = db.query(Student).filter(
        Student.user_id == current_user.id
    ).first()

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )

    return student


# ==================================
# 1. STUDENT PERSONAL DETAILS
# ==================================

@router.get("/me")
def get_my_profile(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    student = get_student_record(current_user, db)

    return {
        "id": student.id,
        "name": student.name,
        "email": current_user.email,
        "roll_no": student.roll_no,
        "class_id": student.class_id,
        "parent_name": student.parent_name,
        "parent_phone": student.parent_phone
    }


# ==================================
# 2. STUDENT ATTENDANCE
# ==================================

@router.get("/attendance")
def get_my_attendance(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    student = get_student_record(current_user, db)

    records = db.query(StudentAttendance).filter(
        StudentAttendance.student_id == student.id
    ).order_by(StudentAttendance.date.desc()).all()

    return [
        {
            "date": record.date,
            "status": record.status
        }
        for record in records
    ]


# ==================================
# 3. STUDENT MARKS / REPORT CARD
# ==================================

@router.get("/marks")
def get_my_marks(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    student = get_student_record(current_user, db)

    records = (
        db.query(Mark, Exam, Subject)
        .join(Exam, Mark.exam_id == Exam.id)
        .join(Subject, Mark.subject_id == Subject.id)
        .filter(Mark.student_id == student.id)
        .all()
    )

    return [
        {
            "exam_name": exam.exam_name,
            "exam_date": exam.exam_date,
            "subject": subject.subject_name,
            "marks_obtained": mark.marks_obtained,
            "max_marks": mark.max_marks
        }
        for mark, exam, subject in records
    ]


# ==================================
# 4. STUDENT FEE DETAILS
# ==================================

@router.get("/fees")
def get_my_fees(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    student = get_student_record(current_user, db)

    records = db.query(Fee).filter(
        Fee.student_id == student.id
    ).all()

    return [
        {
            "total_fee": record.total_fee,
            "paid_amount": record.paid_amount,
            "pending_amount": (
                record.total_fee - record.paid_amount
            )
        }
        for record in records
    ]
