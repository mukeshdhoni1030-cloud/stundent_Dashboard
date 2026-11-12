
from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# Common configuration for reading database objects
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ==================================
# 1. LOGIN SCHEMA
# ==================================

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


# ==================================
# 2. USER SCHEMAS
# ==================================

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    role: Literal["student", "teacher", "principal"]


class UserResponse(BaseSchema):
    id: int
    email: EmailStr
    role: str


# ==================================
# 3. STUDENT SCHEMAS
# ==================================

class StudentCreate(BaseModel):
    user_id: int
    class_id: int
    name: str
    roll_no: str
    parent_name: str
    parent_phone: str


class StudentResponse(BaseSchema):
    id: int
    user_id: int
    class_id: int
    name: str
    roll_no: str
    parent_name: str
    parent_phone: str


# ==================================
# 4. TEACHER SCHEMAS
# ==================================

class TeacherCreate(BaseModel):
    user_id: int
    name: str
    qualification: str
    phone: str


class TeacherResponse(BaseSchema):
    id: int
    user_id: int
    name: str
    qualification: str
    phone: str


# ==================================
# 5. ATTENDANCE SCHEMAS
# ==================================

class AttendanceCreate(BaseModel):
    student_id: int
    attendance_date: date
    status: Literal["present", "absent", "late"]


class AttendanceResponse(BaseSchema):
    id: int
    student_id: int
    date: date
    status: str


class TeacherAttendanceCreate(BaseModel):
    teacher_id: int
    attendance_date: date
    status: Literal["present", "absent", "late"]


# ==================================
# 6. EXAM AND MARKS SCHEMAS
# ==================================

class MarksCreate(BaseModel):
    student_id: int
    exam_id: int
    subject_id: int
    marks_obtained: Decimal = Field(ge=0)
    max_marks: Decimal = Field(gt=0)


class MarksResponse(BaseSchema):
    id: int
    student_id: int
    exam_id: int
    subject_id: int
    marks_obtained: Decimal
    max_marks: Decimal


# ==================================
# 7. FEE SCHEMAS
# ==================================

class FeeCreate(BaseModel):
    student_id: int
    total_fee: Decimal = Field(ge=0)
    paid_amount: Decimal = Field(ge=0)


class FeeResponse(BaseSchema):
    id: int
    student_id: int
    total_fee: Decimal
    paid_amount: Decimal


# ==================================
# 8. SALARY SCHEMAS
# ==================================

class SalaryCreate(BaseModel):
    teacher_id: int
    salary_month: date
    amount: Decimal = Field(ge=0)


class SalaryResponse(BaseSchema):
    id: int
    teacher_id: int
    salary_month: date
    amount: Decimal

# ==================================
# 9. PRINCIPAL MANAGEMENT SCHEMAS
# ==================================

class PrincipalStudentCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    name: str
    class_id: int
    roll_no: str
    parent_name: str
    parent_phone: str


class PrincipalTeacherCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    name: str
    qualification: str
    phone: str

class TeacherAssignmentCreate(BaseModel):
    teacher_id: int
    class_id: int
    subject_id: int

class PrincipalStudentUpdate(BaseModel):
    name: str | None = None
    class_id: int | None = None
    roll_no: str | None = None
    parent_name: str | None = None
    parent_phone: str | None = None


class PrincipalTeacherUpdate(BaseModel):
    name: str | None = None
    qualification: str | None = None
    phone: str | None = None