
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models import (
    Student,
    Teacher,
    StudentAttendance,
    TeacherAttendance,
    Fee,
    Salary,
    User,
    Class as SchoolClass,
    Subject,
    TeacherAssignment,
    Mark
)
from app.schemas import (
    PrincipalStudentCreate,
    PrincipalTeacherCreate,
    TeacherAssignmentCreate,
    PrincipalStudentUpdate,
    PrincipalTeacherUpdate,
    SalaryCreate,
    TeacherAttendanceCreate
)
from app.security import get_password_hash
from app.dependencies import require_principal


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/principal",
    tags=["Principal Dashboard"]
)


# ==========================================
# 1. PRINCIPAL DASHBOARD OVERVIEW
# ==========================================

@router.get("/dashboard")
def get_dashboard(
    current_user: User = Depends(require_principal),
    db: Session = Depends(get_db)
):
    return {
        "message": "Welcome to Principal Dashboard",
        "total_students": db.query(Student).count(),
        "total_teachers": db.query(Teacher).count()
    }


# ==========================================
# 2. VIEW ALL STUDENTS
# ==========================================

@router.get("/students")
def get_all_students(
    current_user: User = Depends(require_principal),
    db: Session = Depends(get_db)
):
    records = (
        db.query(Student, User)
        .join(User, Student.user_id == User.id)
        .all()
    )

    return [
        {
            "id": student.id,
            "name": student.name,
            "email": user.email,
            "roll_no": student.roll_no,
            "class_id": student.class_id,
            "parent_name": student.parent_name,
            "parent_phone": student.parent_phone
        }
        for student, user in records
    ]


# ==========================================
# 3. VIEW ALL TEACHERS
# ==========================================

@router.get("/teachers")
def get_all_teachers(
    current_user: User = Depends(require_principal),
    db: Session = Depends(get_db)
):
    records = (
        db.query(Teacher, User)
        .join(User, Teacher.user_id == User.id)
        .all()
    )

    return [
        {
            "id": teacher.id,
            "name": teacher.name,
            "email": user.email,
            "qualification": teacher.qualification,
            "phone": teacher.phone
        }
        for teacher, user in records
    ]


# ==========================================
# 4. VIEW ALL STUDENT ATTENDANCE
# ==========================================

@router.get("/student-attendance")
def get_all_student_attendance(
    current_user: User = Depends(require_principal),
    db: Session = Depends(get_db)
):
    records = (
        db.query(StudentAttendance, Student)
        .join(
            Student,
            StudentAttendance.student_id == Student.id
        )
        .all()
    )

    return [
        {
            "student_id": student.id,
            "student_name": student.name,
            "date": attendance.date,
            "status": attendance.status
        }
        for attendance, student in records
    ]


# ==========================================
# 5. VIEW ALL TEACHER ATTENDANCE
# ==========================================

@router.get("/teacher-attendance")
def get_all_teacher_attendance(
    current_user: User = Depends(require_principal),
    db: Session = Depends(get_db)
):
    records = (
        db.query(TeacherAttendance, Teacher)
        .join(
            Teacher,
            TeacherAttendance.teacher_id == Teacher.id
        )
        .all()
    )

    return [
        {
            "teacher_id": teacher.id,
            "teacher_name": teacher.name,
            "date": attendance.date,
            "status": attendance.status
        }
        for attendance, teacher in records
    ]


# ==========================================
# ADD TEACHER ATTENDANCE
# ==========================================

@router.post(
    "/teacher-attendance",
    status_code=status.HTTP_201_CREATED
)
def create_teacher_attendance(
    attendance_data: TeacherAttendanceCreate,
    current_user: User = Depends(require_principal),
    db: Session = Depends(get_db)
):
    # 1. Check whether teacher exists
    teacher = db.query(Teacher).filter(
        Teacher.id == attendance_data.teacher_id
    ).first()

    if teacher is None:
        raise HTTPException(
            status_code=404,
            detail="Teacher not found"
        )

    # 2. Check duplicate attendance
    existing_attendance = db.query(TeacherAttendance).filter(
        TeacherAttendance.teacher_id == attendance_data.teacher_id,
        TeacherAttendance.date == attendance_data.attendance_date
    ).first()

    if existing_attendance:
        raise HTTPException(
            status_code=409,
            detail="Attendance already marked for this teacher on this date"
        )

    # 3. Create attendance record
    new_attendance = TeacherAttendance(
        teacher_id=attendance_data.teacher_id,
        date=attendance_data.attendance_date,
        status=attendance_data.status
    )

    try:
        db.add(new_attendance)
        db.commit()
        db.refresh(new_attendance)

        return {
            "message": "Teacher attendance marked successfully",
            "attendance_id": new_attendance.id,
            "teacher_id": teacher.id,
            "teacher_name": teacher.name,
            "date": new_attendance.date,
            "status": new_attendance.status
        }

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Attendance already exists for this teacher and date"
        )

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to mark teacher attendance"
        )


# ==========================================
# 6. VIEW ALL STUDENT FEES
# ==========================================

@router.get("/fees")
def get_all_fees(
    current_user: User = Depends(require_principal),
    db: Session = Depends(get_db)
):
    records = (
        db.query(Fee, Student)
        .join(Student, Fee.student_id == Student.id)
        .all()
    )

    return [
        {
            "student_id": student.id,
            "student_name": student.name,
            "total_fee": fee.total_fee,
            "paid_amount": fee.paid_amount,
            "pending_amount": (
                fee.total_fee - fee.paid_amount
            )
        }
        for fee, student in records
    ]


# ==========================================
# 7. VIEW ALL EMPLOYEE SALARIES
# ==========================================

@router.get("/salaries")
def get_all_salaries(
    current_user: User = Depends(require_principal),
    db: Session = Depends(get_db)
):
    records = (
        db.query(Salary, Teacher)
        .join(Teacher, Salary.teacher_id == Teacher.id)
        .all()
    )

    return [
        {
            "teacher_id": teacher.id,
            "teacher_name": teacher.name,
            "salary_month": salary.salary_month,
            "amount": salary.amount
        }
        for salary, teacher in records
    ]


# ==========================================
# 7A. ADD A NEW EMPLOYEE SALARY
# ==========================================

@router.post("/salaries", status_code=status.HTTP_201_CREATED)
def create_salary(
    salary_data: SalaryCreate,
    current_user: User = Depends(require_principal),
    db: Session = Depends(get_db)
):
    # Check whether the teacher exists
    teacher = db.query(Teacher).filter(
        Teacher.id == salary_data.teacher_id
    ).first()

    if teacher is None:
        raise HTTPException(
            status_code=404,
            detail="Teacher not found"
        )

    # Create the salary record
    new_salary = Salary(
        teacher_id=salary_data.teacher_id,
        salary_month=salary_data.salary_month,
        amount=salary_data.amount
    )

    try:
        db.add(new_salary)
        db.commit()
        db.refresh(new_salary)

        return {
            "message": "Salary created successfully",
            "salary_id": new_salary.id,
            "teacher_id": teacher.id,
            "teacher_name": teacher.name,
            "salary_month": new_salary.salary_month,
            "amount": new_salary.amount
        }

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="A salary record already exists for this teacher and month, or the amount is invalid."
        )

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to create salary"
        )


# ==========================================
# 8. ADD A NEW STUDENT
# ==========================================

@router.post("/students", status_code=status.HTTP_201_CREATED)
def create_student(
    data: PrincipalStudentCreate,
    current_user: User = Depends(require_principal),
    db: Session = Depends(get_db)
):
    # Check duplicate email
    existing_user = db.query(User).filter(
        User.email == data.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )

    # Check whether class exists
    school_class = db.query(SchoolClass).filter(
        SchoolClass.id == data.class_id
    ).first()

    if school_class is None:
        raise HTTPException(
            status_code=404,
            detail="Class not found"
        )

    # Check duplicate roll number
    existing_student = db.query(Student).filter(
        Student.class_id == data.class_id,
        Student.roll_no == data.roll_no
    ).first()

    if existing_student:
        raise HTTPException(
            status_code=409,
            detail="Roll number already exists in this class"
        )

    try:
        # Create student login account
        new_user = User(
            email=data.email,
            password_hash=get_password_hash(data.password),
            role="student"
        )

        db.add(new_user)
        db.flush()

        # Create student profile
        new_student = Student(
            user_id=new_user.id,
            class_id=data.class_id,
            name=data.name,
            roll_no=data.roll_no,
            parent_name=data.parent_name,
            parent_phone=data.parent_phone
        )

        db.add(new_student)
        db.commit()
        db.refresh(new_student)

        return {
            "message": "Student created successfully",
            "student_id": new_student.id,
            "email": new_user.email
        }

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to create student"
        )


# ==========================================
# 9. ADD A NEW TEACHER
# ==========================================

@router.post("/teachers", status_code=status.HTTP_201_CREATED)
def create_teacher(
    data: PrincipalTeacherCreate,
    current_user: User = Depends(require_principal),
    db: Session = Depends(get_db)
):
    # Check duplicate email
    existing_user = db.query(User).filter(
        User.email == data.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )

    try:
        # Create teacher login account
        new_user = User(
            email=data.email,
            password_hash=get_password_hash(data.password),
            role="teacher"
        )

        db.add(new_user)
        db.flush()

        # Create teacher profile
        new_teacher = Teacher(
            user_id=new_user.id,
            name=data.name,
            qualification=data.qualification,
            phone=data.phone
        )

        db.add(new_teacher)
        db.commit()
        db.refresh(new_teacher)

        return {
            "message": "Teacher created successfully",
            "teacher_id": new_teacher.id,
            "email": new_user.email
        }

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to create teacher"
        )


# ==========================================
# ASSIGN TEACHER TO CLASS AND SUBJECT
# ==========================================

@router.post("/assign-teacher", status_code=status.HTTP_201_CREATED)
def assign_teacher(
    data: TeacherAssignmentCreate,
    current_user: User = Depends(require_principal),
    db: Session = Depends(get_db)
):
    # Check whether teacher exists
    teacher = db.query(Teacher).filter(
        Teacher.id == data.teacher_id
    ).first()

    if teacher is None:
        raise HTTPException(
            status_code=404,
            detail="Teacher not found"
        )

    # Check whether class exists
    school_class = db.query(SchoolClass).filter(
        SchoolClass.id == data.class_id
    ).first()

    if school_class is None:
        raise HTTPException(
            status_code=404,
            detail="Class not found"
        )

    # Check whether subject exists
    subject = db.query(Subject).filter(
        Subject.id == data.subject_id
    ).first()

    if subject is None:
        raise HTTPException(
            status_code=404,
            detail="Subject not found"
        )

    # Check for duplicate assignment
    existing_assignment = db.query(TeacherAssignment).filter(
        TeacherAssignment.teacher_id == data.teacher_id,
        TeacherAssignment.class_id == data.class_id,
        TeacherAssignment.subject_id == data.subject_id
    ).first()

    if existing_assignment:
        raise HTTPException(
            status_code=409,
            detail="This teacher is already assigned to this class and subject"
        )

    # Create assignment
    new_assignment = TeacherAssignment(
        teacher_id=data.teacher_id,
        class_id=data.class_id,
        subject_id=data.subject_id
    )

    try:
        db.add(new_assignment)
        db.commit()
        db.refresh(new_assignment)

        return {
            "message": "Teacher assigned successfully",
            "assignment_id": new_assignment.id,
            "teacher_id": new_assignment.teacher_id,
            "class_id": new_assignment.class_id,
            "subject_id": new_assignment.subject_id
        }

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to assign teacher"
        )


# ==========================================
# UPDATE TEACHER DETAILS
# ==========================================

@router.put("/teachers/{teacher_id}")
def update_teacher(
    teacher_id: int,
    data: PrincipalTeacherUpdate,
    current_user: User = Depends(require_principal),
    db: Session = Depends(get_db)
):
    teacher = db.query(Teacher).filter(
        Teacher.id == teacher_id
    ).first()

    if teacher is None:
        raise HTTPException(
            status_code=404,
            detail="Teacher not found"
        )

    update_data = data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No update information provided"
        )

    try:
        for field, value in update_data.items():
            setattr(teacher, field, value)

        db.commit()
        db.refresh(teacher)

        return {
            "message": "Teacher updated successfully",
            "teacher_id": teacher.id,
            "name": teacher.name,
            "qualification": teacher.qualification,
            "phone": teacher.phone
        }

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to update teacher"
        )


# ==========================================
# UPDATE STUDENT DETAILS
# ==========================================

@router.put("/students/{student_id}")
def update_student(
    student_id: int,
    data: PrincipalStudentUpdate,
    current_user: User = Depends(require_principal),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(
        Student.id == student_id
    ).first()

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    update_data = data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No update information provided"
        )

    if "class_id" in update_data:
        school_class = db.query(SchoolClass).filter(
            SchoolClass.id == update_data["class_id"]
        ).first()

        if school_class is None:
            raise HTTPException(
                status_code=404,
                detail="Class not found"
            )

    if "roll_no" in update_data or "class_id" in update_data:
        new_class_id = update_data.get("class_id", student.class_id)
        new_roll_no = update_data.get("roll_no", student.roll_no)

        duplicate = db.query(Student).filter(
            Student.id != student_id,
            Student.class_id == new_class_id,
            Student.roll_no == new_roll_no
        ).first()

        if duplicate:
            raise HTTPException(
                status_code=409,
                detail="Roll number already exists in this class"
            )

    try:
        for field, value in update_data.items():
            setattr(student, field, value)

        db.commit()
        db.refresh(student)

        return {
            "message": "Student updated successfully",
            "student_id": student.id,
            "name": student.name,
            "class_id": student.class_id,
            "roll_no": student.roll_no,
            "parent_name": student.parent_name,
            "parent_phone": student.parent_phone
        }

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to update student"
        )


# ==========================================
# PERMANENTLY DELETE STUDENT
# ==========================================

@router.delete("/students/{student_id}")
def delete_student(
    student_id: int,
    current_user: User = Depends(require_principal),
    db: Session = Depends(get_db)
):
    # Find the student and keep the linked login account ID.
    student = db.query(Student).filter(
        Student.id == student_id
    ).first()

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    user_id = student.user_id

    try:
        # Delete records that reference the student first.
        attendance_deleted = db.query(StudentAttendance).filter(
            StudentAttendance.student_id == student_id
        ).delete(synchronize_session=False)

        marks_deleted = db.query(Mark).filter(
            Mark.student_id == student_id
        ).delete(synchronize_session=False)

        fees_deleted = db.query(Fee).filter(
            Fee.student_id == student_id
        ).delete(synchronize_session=False)

        # Delete the student profile after its dependent records.
        student_deleted = db.query(Student).filter(
            Student.id == student_id
        ).delete(synchronize_session=False)

        if student_deleted != 1:
            raise RuntimeError(
                f"Expected to delete 1 student, deleted {student_deleted}"
            )

        # Delete only the linked account if it is a student account.
        user_deleted = db.query(User).filter(
            User.id == user_id,
            User.role == "student"
        ).delete(synchronize_session=False)

        if user_deleted != 1:
            raise RuntimeError(
                f"Expected to delete 1 student user, deleted {user_deleted}"
            )

        # All deletes are committed together.
        db.commit()

        return {
            "message": "Student and related records permanently deleted",
            "student_id": student_id,
            "deleted_records": {
                "attendance": attendance_deleted,
                "marks": marks_deleted,
                "fees": fees_deleted,
                "student_profiles": student_deleted,
                "login_accounts": user_deleted
            }
        }

    except Exception:
        db.rollback()

        # Full traceback is written to the Uvicorn terminal for diagnosis.
        logger.exception(
            "Permanent deletion failed for student_id=%s",
            student_id
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to delete student. The transaction was rolled back. Check the backend terminal."
        )


# ==========================================
# DELETE TEACHER
# ==========================================

@router.delete("/teachers/{teacher_id}")
def delete_teacher(
    teacher_id: int,
    current_user: User = Depends(require_principal),
    db: Session = Depends(get_db)
):
    teacher = db.query(Teacher).filter(
        Teacher.id == teacher_id
    ).first()

    if teacher is None:
        raise HTTPException(
            status_code=404,
            detail="Teacher not found"
        )

    # Check whether teacher has class or subject assignments
    has_assignment = db.query(TeacherAssignment).filter(
        TeacherAssignment.teacher_id == teacher_id
    ).first()

    # Check whether teacher has attendance records
    has_attendance = db.query(TeacherAttendance).filter(
        TeacherAttendance.teacher_id == teacher_id
    ).first()

    # Check whether teacher has salary records
    has_salary = db.query(Salary).filter(
        Salary.teacher_id == teacher_id
    ).first()

    if has_assignment or has_attendance or has_salary:
        raise HTTPException(
            status_code=409,
            detail=(
                "Cannot delete teacher because assignment, "
                "attendance, or salary records exist"
            )
        )

    try:
        user = db.query(User).filter(
            User.id == teacher.user_id
        ).first()

        db.delete(teacher)

        if user:
            db.delete(user)

        db.commit()

        return {
            "message": "Teacher deleted successfully",
            "teacher_id": teacher_id
        }

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to delete teacher"
        )


# ==========================================
# VIEW PENDING FEES
# ==========================================

@router.get("/pending-fees")
def get_pending_fees(
    current_user: User = Depends(require_principal),
    db: Session = Depends(get_db)
):
    records = (
        db.query(Fee, Student)
        .join(Student, Fee.student_id == Student.id)
        .filter(Fee.paid_amount < Fee.total_fee)
        .all()
    )

    return [
        {
            "student_id": student.id,
            "student_name": student.name,
            "roll_no": student.roll_no,
            "total_fee": fee.total_fee,
            "paid_amount": fee.paid_amount,
            "pending_amount": fee.total_fee - fee.paid_amount
        }
        for fee, student in records
    ]


# ==========================================
# ADD NEW STUDENT
# ==========================================

@router.post("/students")
def add_student(
    student_data: PrincipalStudentCreate,
    current_user: User = Depends(require_principal),
    db: Session = Depends(get_db)
):
    # Check existing email
    existing_user = db.query(User).filter(
        User.email == student_data.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )

    # Check whether class exists
    school_class = db.query(SchoolClass).filter(
        SchoolClass.id == student_data.class_id
    ).first()

    if school_class is None:
        raise HTTPException(
            status_code=404,
            detail="Class not found"
        )

    # Check duplicate roll number
    existing_student = db.query(Student).filter(
        Student.class_id == student_data.class_id,
        Student.roll_no == student_data.roll_no
    ).first()

    if existing_student:
        raise HTTPException(
            status_code=409,
            detail="Roll number already exists in this class"
        )

    try:
        # Create login account
        new_user = User(
            email=student_data.email,
            password_hash=get_password_hash(student_data.password),
            role="student"
        )

        db.add(new_user)
        db.flush()

        # Create student profile
        new_student = Student(
            user_id=new_user.id,
            name=student_data.name,
            class_id=student_data.class_id,
            roll_no=student_data.roll_no,
            parent_name=student_data.parent_name,
            parent_phone=student_data.parent_phone
        )

        db.add(new_student)
        db.commit()
        db.refresh(new_student)

        return {
            "message": "Student created successfully",
            "student_id": new_student.id,
            "name": new_student.name,
            "email": new_user.email,
            "roll_no": new_student.roll_no
        }

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to create student"
        )
