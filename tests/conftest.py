"""Shared fixtures for LinuxLabX API tests.

Important: DATABASE_URL is set before importing the application, because main.py
calls Base.metadata.create_all() during import.
"""

from __future__ import annotations

import os
import tempfile
from collections.abc import Iterator
from pathlib import Path

# Isolate the application's import-time create_all() from linuxlabx.db.
_TEST_DB_DIR = tempfile.mkdtemp(prefix="linuxlabx_pytest_")
_TEST_DB_PATH = Path(_TEST_DB_DIR) / "linuxlabx_test.db"
os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DB_PATH.as_posix()}"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

from app.core.database import Base, get_db
from app.core.security import create_access_token, hash_password
from app.models.learning_path import LearningPath  # noqa: F401
from app.models.lesson import Lesson  # noqa: F401
from app.models.lesson_completion import LessonCompletion  # noqa: F401
from app.models.progress import UserProgress  # noqa: F401
from app.models.quiz import Quiz, QuizQuestion  # noqa: F401
from app.models.quiz_attempt import QuizAttempt  # noqa: F401
from app.models.topic import Topic, TopicLesson  # noqa: F401

# Import all models before create_all so their tables are registered.
from app.models.user import User
from app.models.xp import UserXP  # noqa: F401
from app.models.xp_event import XPEvent  # noqa: F401
from main import app

TEST_DATABASE_URL = f"sqlite:///{_TEST_DB_PATH.as_posix()}"
_test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=NullPool,
)
_TestSessionLocal = sessionmaker(
    bind=_test_engine, autoflush=False, autocommit=False, expire_on_commit=False
)


@pytest.fixture()
def db() -> Iterator[Session]:
    """A fresh schema and DB session for each test; never touches linuxlabx.db."""
    Base.metadata.drop_all(bind=_test_engine)
    Base.metadata.create_all(bind=_test_engine)
    session = _TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=_test_engine)


@pytest.fixture()
def client(db: Session) -> Iterator[TestClient]:
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)


def make_user(
    db: Session,
    *,
    name: str,
    email: str,
    password: str,
    role: str = "student",
    is_active: bool = True,
) -> User:
    user = User(
        name=name,
        email=email,
        password_hash=hash_password(password),
        role=role,
        is_active=is_active,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture()
def test_user(db: Session) -> User:
    return make_user(
        db,
        name="Test Student",
        email="student@example.com",
        password="TestPassword123!",
        role="student",
    )


@pytest.fixture()
def admin_user(db: Session) -> User:
    return make_user(
        db,
        name="Test Admin",
        email="admin@example.com",
        password="TestPassword123!",
        role="admin",
    )


@pytest.fixture()
def auth_headers(test_user: User) -> dict[str, str]:
    token = create_access_token(user_id=test_user.id, role=test_user.role)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def admin_headers(admin_user: User) -> dict[str, str]:
    token = create_access_token(user_id=admin_user.id, role=admin_user.role)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def login_headers(client: TestClient, test_user: User) -> dict[str, str]:
    """Exercise the real login route and return its bearer header."""
    response = client.post(
        "/auth/login",
        json={"email": test_user.email, "password": "TestPassword123!"},
    )
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def sample_quiz_payload() -> dict:
    return {
        "title": "Linux Basics Quiz",
        "description": "A test quiz",
        "difficulty": "beginner",
        "questions": [
            {
                "prompt": "Which command lists files?",
                "options": ["ls", "cd", "pwd", "mkdir"],
                "correct_option_index": 0,
                "explanation": "ls lists directory entries.",
                "display_order": 0,
            },
            {
                "prompt": "Which command prints the current directory?",
                "options": ["cat", "pwd", "rm", "touch"],
                "correct_option_index": 1,
                "explanation": "pwd prints the working directory.",
                "display_order": 1,
            },
        ],
        "is_published": False,
    }


@pytest.fixture()
def published_quiz_id(
    client: TestClient, admin_headers: dict[str, str], sample_quiz_payload: dict
) -> int:
    created = client.post(
        "/admin/quizzes", json=sample_quiz_payload, headers=admin_headers
    )
    assert created.status_code == 201, created.text
    quiz_id = created.json()["id"]
    published = client.patch(f"/admin/quizzes/{quiz_id}/publish", headers=admin_headers)
    assert published.status_code == 200, published.text
    return quiz_id
