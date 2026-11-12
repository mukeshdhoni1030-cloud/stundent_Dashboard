
import pytest

from datetime import date

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app import models
from app.models import User
from app.security import get_password_hash, create_access_token
from app.routes import principal, student as student_routes, teacher as teacher_routes


# ==================================
# TEMPORARY SQLITE DATABASE
# ==================================

test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)


# ==================================
# TEST DATABASE + JWT TOKENS
# ==================================

@pytest.fixture
def client_and_tokens():
    Base.metadata.create_all(bind=test_engine)

    db = TestingSessionLocal()

    # Create a class
    school_class = models.Class(
        class_name="Class 10",
        section="A"
    )
    db.add(school_class)
    db.commit()
    db.refresh(school_class)

    # Create test users
    student_user = User(
        email="student@test.com",
        password_hash=get_password_hash("Student@123"),
        role="student"
    )

    teacher_user = User(
        email="teacher@test.com",
        password_hash=get_password_hash("Teacher@123"),
        role="teacher"
    )

    principal_user = User(
        email="principal@test.com",
        password_hash=get_password_hash("Principal@123"),
        role="principal"
    )

    db.add_all([student_user, teacher_user, principal_user])
    db.commit()

    db.refresh(student_user)
    db.refresh(teacher_user)
    db.refresh(principal_user)

    # Create Student profile
    student_profile = models.Student(
        user_id=student_user.id,
        class_id=school_class.id,
        name="Test Student",
        roll_no="TEST1001",
        parent_name="Test Parent",
        parent_phone="9876543210"
    )

    # Create Teacher profile
    teacher_profile = models.Teacher(
        user_id=teacher_user.id,
        name="Test Teacher",
        qualification="M.Sc Mathematics",
        phone="9876543211"
    )

    db.add_all([student_profile, teacher_profile])
    db.commit()

    db.refresh(student_profile)
    db.refresh(teacher_profile)

    # Create subject
    subject = models.Subject(
        subject_name="Mathematics"
    )
    db.add(subject)
    db.commit()
    db.refresh(subject)

    # Assign teacher to class and subject
    assignment = models.TeacherAssignment(
        teacher_id=teacher_profile.id,
        class_id=school_class.id,
        subject_id=subject.id
    )
    db.add(assignment)

    # Create exam
    exam = models.Exam(
        exam_name="Test Examination",
        exam_date=date.today()
    )
    db.add(exam)
    db.commit()
    db.refresh(exam)

    # Generate JWT tokens
    tokens = {
        "student": create_access_token({
            "sub": str(student_user.id),
            "role": "student"
        }),
        "teacher": create_access_token({
            "sub": str(teacher_user.id),
            "role": "teacher"
        }),
        "principal": create_access_token({
            "sub": str(principal_user.id),
            "role": "principal"
        })
    }

    db.close()

    # Create test FastAPI application
    test_app = FastAPI()

    test_app.include_router(principal.router)
    test_app.include_router(student_routes.router)
    test_app.include_router(teacher_routes.router)

    def override_get_db():
        test_db = TestingSessionLocal()
        try:
            yield test_db
        finally:
            test_db.close()

    test_app.dependency_overrides[get_db] = override_get_db

    with TestClient(test_app) as test_client:
        yield test_client, tokens

    test_app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


# ==================================
# PRINCIPAL PERMISSION TESTS
# ==================================

def test_student_cannot_access_principal_dashboard(client_and_tokens):
    client, tokens = client_and_tokens

    response = client.get(
        "/principal/dashboard",
        headers={"Authorization": f"Bearer {tokens['student']}"}
    )

    assert response.status_code == 403


def test_teacher_cannot_access_principal_dashboard(client_and_tokens):
    client, tokens = client_and_tokens

    response = client.get(
        "/principal/dashboard",
        headers={"Authorization": f"Bearer {tokens['teacher']}"}
    )

    assert response.status_code == 403


def test_principal_can_access_dashboard(client_and_tokens):
    client, tokens = client_and_tokens

    response = client.get(
        "/principal/dashboard",
        headers={"Authorization": f"Bearer {tokens['principal']}"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Welcome to Principal Dashboard"
    assert data["total_students"] == 1
    assert data["total_teachers"] == 1


def test_no_token_cannot_access_principal_dashboard(client_and_tokens):
    client, tokens = client_and_tokens

    response = client.get("/principal/dashboard")

    assert response.status_code == 401


# ==================================
# STUDENT API ACCESS TESTS
# ==================================

@pytest.mark.parametrize("endpoint", [
    "/student/me",
    "/student/attendance",
    "/student/marks",
    "/student/fees"
])
def test_student_can_access_own_apis(client_and_tokens, endpoint):
    client, tokens = client_and_tokens

    response = client.get(
        endpoint,
        headers={"Authorization": f"Bearer {tokens['student']}"}
    )

    assert response.status_code == 200


@pytest.mark.parametrize("role", ["teacher", "principal"])
@pytest.mark.parametrize("endpoint", [
    "/student/me",
    "/student/attendance",
    "/student/marks",
    "/student/fees"
])
def test_other_roles_cannot_access_student_apis(
    client_and_tokens, role, endpoint
):
    client, tokens = client_and_tokens

    response = client.get(
        endpoint,
        headers={"Authorization": f"Bearer {tokens[role]}"}
    )

    assert response.status_code == 403


def test_no_token_cannot_access_student_profile(client_and_tokens):
    client, tokens = client_and_tokens

    response = client.get("/student/me")

    assert response.status_code == 401


# ==================================
# TEACHER API ACCESS TESTS
# ==================================

@pytest.mark.parametrize("endpoint", [
    "/teacher/me",
    "/teacher/students",
    "/teacher/attendance/me"
])
def test_teacher_can_access_own_apis(client_and_tokens, endpoint):
    client, tokens = client_and_tokens

    response = client.get(
        endpoint,
        headers={"Authorization": f"Bearer {tokens['teacher']}"}
    )

    assert response.status_code == 200


def test_teacher_can_mark_student_attendance(client_and_tokens):
    client, tokens = client_and_tokens

    response = client.post(
        "/teacher/attendance",
        headers={"Authorization": f"Bearer {tokens['teacher']}"},
        json={
            "student_id": 1,
            "attendance_date": str(date.today()),
            "status": "present"
        }
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Student attendance saved successfully"


def test_teacher_can_upload_student_marks(client_and_tokens):
    client, tokens = client_and_tokens

    response = client.post(
        "/teacher/marks",
        headers={"Authorization": f"Bearer {tokens['teacher']}"},
        json={
            "student_id": 1,
            "exam_id": 1,
            "subject_id": 1,
            "marks_obtained": 85,
            "max_marks": 100
        }
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Student marks uploaded successfully"


# ==================================
# STUDENT AND PRINCIPAL CANNOT
# ACCESS TEACHER APIs
# ==================================

@pytest.mark.parametrize("role", ["student", "principal"])
@pytest.mark.parametrize("endpoint", [
    "/teacher/me",
    "/teacher/students",
    "/teacher/attendance/me"
])
def test_other_roles_cannot_access_teacher_get_apis(
    client_and_tokens, role, endpoint
):
    client, tokens = client_and_tokens

    response = client.get(
        endpoint,
        headers={"Authorization": f"Bearer {tokens[role]}"}
    )

    assert response.status_code == 403


@pytest.mark.parametrize("role", ["student", "principal"])
@pytest.mark.parametrize(
    "endpoint,payload",
    [
        (
            "/teacher/attendance",
            {
                "student_id": 1,
                "attendance_date": str(date.today()),
                "status": "present"
            }
        ),
        (
            "/teacher/marks",
            {
                "student_id": 1,
                "exam_id": 1,
                "subject_id": 1,
                "marks_obtained": 85,
                "max_marks": 100
            }
        )
    ]
)
def test_other_roles_cannot_access_teacher_post_apis(
    client_and_tokens, role, endpoint, payload
):
    client, tokens = client_and_tokens

    response = client.post(
        endpoint,
        headers={"Authorization": f"Bearer {tokens[role]}"},
        json=payload
    )

    assert response.status_code == 403


def test_no_token_cannot_access_teacher_profile(client_and_tokens):
    client, tokens = client_and_tokens

    response = client.get("/teacher/me")

    assert response.status_code == 401
