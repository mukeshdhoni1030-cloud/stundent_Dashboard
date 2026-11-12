
import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app import models
from app.models import User
from app.security import get_password_hash
from app.routes import auth


# Create a separate temporary SQLite database
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


@pytest.fixture
def client():
    Base.metadata.create_all(bind=test_engine)

    db = TestingSessionLocal()

    # Create sample users for testing
    test_users = [
        User(
            email="teststudent@example.com",
            password_hash=get_password_hash("Student@123"),
            role="student"
        ),
        User(
            email="testteacher@example.com",
            password_hash=get_password_hash("Teacher@123"),
            role="teacher"
        ),
        User(
            email="testprincipal@example.com",
            password_hash=get_password_hash("Principal@123"),
            role="principal"
        )
    ]

    db.add_all(test_users)
    db.commit()
    db.close()

    test_app = FastAPI()
    test_app.include_router(auth.router)

    def override_get_db():
        test_db = TestingSessionLocal()
        try:
            yield test_db
        finally:
            test_db.close()

    test_app.dependency_overrides[get_db] = override_get_db

    with TestClient(test_app) as test_client:
        yield test_client

    test_app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


@pytest.mark.parametrize(
    "email, password, expected_role",
    [
        ("teststudent@example.com", "Student@123", "student"),
        ("testteacher@example.com", "Teacher@123", "teacher"),
        ("testprincipal@example.com", "Principal@123", "principal")
    ]
)
def test_valid_login(client, email, password, expected_role):
    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["access_token"]
    assert data["token_type"] == "bearer"
    assert data["role"] == expected_role


def test_invalid_password(client):
    response = client.post(
        "/auth/login",
        json={
            "email": "teststudent@example.com",
            "password": "WrongPassword"
        }
    )

    assert response.status_code == 401


def test_non_existing_email(client):
    response = client.post(
        "/auth/login",
        json={
            "email": "unknown@example.com",
            "password": "Unknown@123"
        }
    )

    assert response.status_code == 401
