
import pytest

from datetime import date
from decimal import Decimal

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app import models
from app.models import User
from app.security import get_password_hash, create_access_token
from app.routes import principal


# ==================================
# TEMPORARY TEST DATABASE
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
# TEST DATABASE FIXTURE
# ==================================

@pytest.fixture
def principal_client():
    Base.metadata.create_all(bind=test_engine)

    db = TestingSessionLocal()

    # Create classes
    class_a = models.Class(class_name="Class 10", section="A")
    class_b = models.Class(class_name="Class 10", section="B")

    db.add_all([class_a, class_b])
    db.commit()
    db.refresh(class_a)
    db.refresh(class_b)

    # Create users
    principal_user = User(
        email="principal@test.com",
        password_hash=get_password_hash("Principal@123"),
        role="principal"
    )

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

    db.add_all([principal_user, student_user, teacher_user])
    db.commit()

    db.refresh(principal_user)
    db.refresh(student_user)
    db.refresh(teacher_user)

    # Create student profile
    student = models.Student(
        user_id=student_user.id,
        class_id=class_a.id,
        name="Ravi Kumar",
        roll_no="1001",
        parent_name="Ramesh Kumar",
        parent_phone="9876543210"
    )

    # Create teacher profile
    teacher = models.Teacher(
        user_id=teacher_user.id,
        name="Suresh Kumar",
        qualification="M.Sc Mathematics",
        phone="9876543211"
    )

    db.add_all([student, teacher])
    db.commit()

    db.refresh(student)
    db.refresh(teacher)

    # Create subject
    subject = models.Subject(subject_name="Mathematics")
    db.add(subject)
    db.commit()
    db.refresh(subject)

    # Assign teacher to Class A Mathematics
    assignment = models.TeacherAssignment(
        teacher_id=teacher.id,
        class_id=class_a.id,
        subject_id=subject.id
    )

    db.add(assignment)
    db.commit()

    # Create JWT token
    token = create_access_token({
        "sub": str(principal_user.id),
        "role": "principal"
    })

    db.close()

    # Create test FastAPI application
    test_app = FastAPI()
    test_app.include_router(principal.router)

    def override_get_db():
        test_db = TestingSessionLocal()
        try:
            yield test_db
        finally:
            test_db.close()

    test_app.dependency_overrides[get_db] = override_get_db

    with TestClient(test_app) as client:
        yield client, token

    test_app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


# ==================================
# HELPER FUNCTION
# ==================================

def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


# ==================================
# 1. DASHBOARD AND VIEW APIs
# ==================================

def test_principal_dashboard(principal_client):
    client, token = principal_client

    response = client.get(
        "/principal/dashboard",
        headers=auth_headers(token)
    )

    assert response.status_code == 200
    assert response.json()["total_students"] == 1
    assert response.json()["total_teachers"] == 1


@pytest.mark.parametrize("endpoint", [
    "/principal/students",
    "/principal/teachers",
    "/principal/student-attendance",
    "/principal/teacher-attendance",
    "/principal/fees",
    "/principal/salaries",
    "/principal/pending-fees"
])
def test_principal_can_view_management_data(
    principal_client, endpoint
):
    client, token = principal_client

    response = client.get(
        endpoint,
        headers=auth_headers(token)
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


# ==================================
# 2. CREATE STUDENT
# ==================================

def test_principal_can_create_student(principal_client):
    client, token = principal_client

    response = client.post(
        "/principal/students",
        headers=auth_headers(token),
        json={
            "email": "newstudent@test.com",
            "password": "Student@123",
            "name": "Arun Kumar",
            "class_id": 1,
            "roll_no": "1002",
            "parent_name": "Kumar",
            "parent_phone": "9876543212"
        }
    )

    assert response.status_code == 201
    assert response.json()["message"] == "Student created successfully"


def test_principal_cannot_create_duplicate_email(principal_client):
    client, token = principal_client

    response = client.post(
        "/principal/students",
        headers=auth_headers(token),
        json={
            "email": "student@test.com",
            "password": "Student@123",
            "name": "Duplicate Student",
            "class_id": 1,
            "roll_no": "1003",
            "parent_name": "Parent",
            "parent_phone": "9876543212"
        }
    )

    assert response.status_code == 409


# ==================================
# 3. CREATE TEACHER
# ==================================

def test_principal_can_create_teacher(principal_client):
    client, token = principal_client

    response = client.post(
        "/principal/teachers",
        headers=auth_headers(token),
        json={
            "email": "newteacher@test.com",
            "password": "Teacher@123",
            "name": "Ramesh Kumar",
            "qualification": "M.Tech",
            "phone": "9876543213"
        }
    )

    assert response.status_code == 201
    assert response.json()["message"] == "Teacher created successfully"


# ==================================
# 4. ASSIGN TEACHER
# ==================================

def test_principal_can_assign_teacher(principal_client):
    client, token = principal_client

    response = client.post(
        "/principal/assign-teacher",
        headers=auth_headers(token),
        json={
            "teacher_id": 1,
            "class_id": 2,
            "subject_id": 1
        }
    )

    assert response.status_code == 201
    assert response.json()["message"] == "Teacher assigned successfully"


def test_principal_cannot_duplicate_teacher_assignment(
    principal_client
):
    client, token = principal_client

    response = client.post(
        "/principal/assign-teacher",
        headers=auth_headers(token),
        json={
            "teacher_id": 1,
            "class_id": 1,
            "subject_id": 1
        }
    )

    assert response.status_code == 409


# ==================================
# 5. UPDATE STUDENT
# ==================================

def test_principal_can_update_student(principal_client):
    client, token = principal_client

    response = client.put(
        "/principal/students/1",
        headers=auth_headers(token),
        json={
            "name": "Ravi Updated",
            "parent_phone": "9999999999"
        }
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Ravi Updated"


def test_principal_cannot_update_missing_student(
    principal_client
):
    client, token = principal_client

    response = client.put(
        "/principal/students/999",
        headers=auth_headers(token),
        json={"name": "Unknown"}
    )

    assert response.status_code == 404


# ==================================
# 6. UPDATE TEACHER
# ==================================

def test_principal_can_update_teacher(principal_client):
    client, token = principal_client

    response = client.put(
        "/principal/teachers/1",
        headers=auth_headers(token),
        json={"qualification": "M.Tech"}
    )

    assert response.status_code == 200
    assert response.json()["qualification"] == "M.Tech"


def test_principal_cannot_update_missing_teacher(
    principal_client
):
    client, token = principal_client

    response = client.put(
        "/principal/teachers/999",
        headers=auth_headers(token),
        json={"qualification": "M.Tech"}
    )

    assert response.status_code == 404


# ==================================
# 7. DELETE PROTECTION
# ==================================

def test_principal_cannot_delete_assigned_teacher(
    principal_client
):
    client, token = principal_client

    response = client.delete(
        "/principal/teachers/1",
        headers=auth_headers(token)
    )

    assert response.status_code == 409


def test_principal_cannot_delete_missing_student(
    principal_client
):
    client, token = principal_client

    response = client.delete(
        "/principal/students/999",
        headers=auth_headers(token)
    )

    assert response.status_code == 404
