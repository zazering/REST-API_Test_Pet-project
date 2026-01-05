import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from infrastructure.database import Base
from infrastructure.repositories import TaskRepository, UserRepository
from application.services import TaskService, AuthService
from main import app

TEST_DATABASE_URL = "sqlite:///./test_database.db"

@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test_database.db"):
        os.remove("./test_database.db")

@pytest.fixture(scope="function")
def test_db_session(test_engine):
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestSessionLocal()
    yield session
    session.rollback()
    session.close()

@pytest.fixture(scope="function")
def task_repository(test_db_session):
    repo = TaskRepository()
    repo.db = test_db_session
    return repo

@pytest.fixture(scope="function")
def user_repository(test_db_session):
    repo = UserRepository()
    repo.db = test_db_session
    return repo

@pytest.fixture(scope="function")
def task_service(task_repository):
    return TaskService(task_repository)

@pytest.fixture(scope="function")
def auth_service(user_repository):
    return AuthService(user_repository)

@pytest.fixture(scope="function")
def client():
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(scope="function")
def test_user(auth_service):
    from application.schemas import UserCreate
    user_data = UserCreate(username="testuser", email="test@example.com", password="password123")
    user = auth_service.register_user(user_data)
    return user

@pytest.fixture(scope="function")
def auth_token(client, test_user):
    response = client.post(
        "/api/auth/login",
        data={"username": "testuser", "password": "password123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    return response.json()["access_token"]

@pytest.fixture(scope="function")
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}

def pytest_configure(config):
    debug_level = os.environ.get("DEBUG", "0")
    
    if debug_level == "1":
        config.option.markexpr = "unit"
        print("\n🧪 DEBUG=1: Running UNIT tests (Business Logic)")
    elif debug_level == "2":
        config.option.markexpr = "integration"
        print("\n🔌 DEBUG=2: Running INTEGRATION tests (API Endpoints)")
    elif debug_level == "3":
        config.option.markexpr = "e2e"
        print("\n🌐 DEBUG=3: Running E2E tests (Full Stack)")
    elif debug_level == "all":
        print("\n🚀 DEBUG=all: Running ALL tests")
    else:
        print("\n✨ Running tests based on pytest arguments")
