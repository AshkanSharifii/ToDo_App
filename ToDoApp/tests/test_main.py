from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.dependencies import get_db
from app.main import app
from app.utils.security import create_access_token

# Create test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_db.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create test client
client = TestClient(app)


@pytest.fixture(scope="function")
def test_db():
    # Create the database tables
    Base.metadata.create_all(bind=engine)

    # Create a new session for each test
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop the tables after the test
        Base.metadata.drop_all(bind=engine)


# Override the dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_create_user():
    # Test user creation
    user_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    response = client.post("/auth/signup", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["email"] == "test@example.com"


def test_login():
    # First create a user
    user_data = {
        "email": "login_test@example.com",
        "password": "password123"
    }
    client.post("/auth/signup", json=user_data)

    # Now test login
    login_data = {
        "username": "login_test@example.com",
        "password": "password123"
    }
    response = client.post("/auth/login", data=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_create_task():
    # First create a user
    user_data = {
        "email": "task_test@example.com",
        "password": "password123"
    }
    user_response = client.post("/auth/signup", json=user_data)
    user_id = user_response.json()["id"]

    # Create a token manually for the user
    token = create_access_token({"sub": user_id})

    # Now create a task
    task_data = {
        "title": "Test Task",
        "day": "2025-05-01"
    }
    response = client.post(
        "/tasks/",
        json=task_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["day"] == "2025-05-01"
    assert data["is_completed"] == False