from sqlalchemy import func, select

from app.models.lesson_completion import LessonCompletion
from app.models.progress import UserProgress
from app.models.xp import UserXP
from app.models.xp_event import XPEvent


def _create_lesson(client, admin_headers, *, title="Test Lesson", published=True):
    payload = {
        "title": title,
        "description": "Lesson completion test",
        "command": "pwd",
        "syntax": "pwd",
        "examples": [{"command": "pwd", "output": "/home/student"}],
        "expected_output": "/home/student",
        "options": [],
        "tips": [],
        "common_mistakes": [],
        "difficulty": "beginner",
        "display_order": 0,
        "is_published": published,
    }
    response = client.post("/admin/lessons", json=payload, headers=admin_headers)
    assert response.status_code == 201, response.text
    return response.json()


def _complete(client, lesson_id, headers):
    return client.post(f"/lessons/{lesson_id}/complete", headers=headers)


def test_lesson_completion_requires_authentication(client, admin_headers):
    lesson = _create_lesson(client, admin_headers)
    response = client.post(f"/lessons/{lesson['id']}/complete")
    assert response.status_code == 401


def test_student_can_complete_published_lesson_and_receive_xp(
    client, admin_headers, login_headers, db, test_user
):
    lesson = _create_lesson(client, admin_headers)
    response = _complete(client, lesson["id"], login_headers)

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["lesson_id"] == lesson["id"]
    assert body["completed"] is True
    assert body["already_completed"] is False
    assert body["xp_awarded"] == 10
    assert body["total_xp"] == 10
    assert body["level"] == 1
    assert body["lessons_completed"] == 1
    assert body["progress_percentage"] == 100

    completion_count = db.scalar(
        select(func.count(LessonCompletion.id)).where(
            LessonCompletion.user_id == test_user.id,
            LessonCompletion.lesson_id == lesson["id"],
        )
    )
    assert completion_count == 1

    event = db.scalar(
        select(XPEvent).where(
            XPEvent.user_id == test_user.id,
            XPEvent.activity_type == "lesson",
            XPEvent.activity_id == lesson["id"],
            XPEvent.event_type == "completion",
        )
    )
    assert event is not None
    assert event.xp_amount == 10


def test_repeating_lesson_completion_does_not_duplicate_xp_or_progress(
    client, admin_headers, login_headers, db, test_user
):
    lesson = _create_lesson(client, admin_headers)
    first = _complete(client, lesson["id"], login_headers)
    second = _complete(client, lesson["id"], login_headers)

    assert first.status_code == 200, first.text
    assert second.status_code == 200, second.text
    body = second.json()
    assert body["already_completed"] is True
    assert body["xp_awarded"] == 0
    assert body["total_xp"] == 10
    assert body["lessons_completed"] == 1

    completions = db.scalar(
        select(func.count(LessonCompletion.id)).where(
            LessonCompletion.user_id == test_user.id,
            LessonCompletion.lesson_id == lesson["id"],
        )
    )
    events = db.scalar(
        select(func.count(XPEvent.id)).where(
            XPEvent.user_id == test_user.id,
            XPEvent.activity_type == "lesson",
            XPEvent.activity_id == lesson["id"],
            XPEvent.event_type == "completion",
        )
    )
    assert completions == 1
    assert events == 1


def test_unpublished_lesson_cannot_be_completed(
    client, admin_headers, login_headers
):
    lesson = _create_lesson(client, admin_headers, published=False)
    response = _complete(client, lesson["id"], login_headers)
    assert response.status_code == 404


def test_nonexistent_lesson_cannot_be_completed(client, login_headers):
    response = _complete(client, 999999, login_headers)
    assert response.status_code == 404


def test_progress_percentage_uses_published_lessons(
    client, admin_headers, login_headers
):
    first = _create_lesson(client, admin_headers, title="Published One")
    _create_lesson(client, admin_headers, title="Published Two")
    _create_lesson(client, admin_headers, title="Draft", published=False)

    response = _complete(client, first["id"], login_headers)
    assert response.status_code == 200, response.text
    assert response.json()["progress_percentage"] == 50


def test_completed_lesson_list_requires_authentication(client):
    response = client.get("/lessons/completed/me")
    assert response.status_code == 401


def test_completed_lesson_list_only_returns_current_users_records(
    client, admin_headers, login_headers, db
):
    lesson = _create_lesson(client, admin_headers)
    own_completion = _complete(client, lesson["id"], login_headers)
    assert own_completion.status_code == 200

    # Create a second user and authenticate through the real login route.
    from app.models.user import User
    from app.core.security import hash_password

    other = User(
        name="Other Student",
        email="other.student@example.com",
        password_hash=hash_password("OtherPassword123!"),
        role="student",
        is_active=True,
    )
    db.add(other)
    db.commit()

    login = client.post(
        "/auth/login",
        json={"email": other.email, "password": "OtherPassword123!"},
    )
    assert login.status_code == 200, login.text
    other_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = client.get("/lessons/completed/me", headers=other_headers)
    assert response.status_code == 200, response.text
    assert response.json() == []


def test_lesson_completion_updates_existing_progress_and_xp_rows(
    client, admin_headers, login_headers, db, test_user
):
    lesson = _create_lesson(client, admin_headers)
    response = _complete(client, lesson["id"], login_headers)
    assert response.status_code == 200, response.text

    progress = db.scalar(
        select(UserProgress).where(UserProgress.user_id == test_user.id)
    )
    xp = db.scalar(select(UserXP).where(UserXP.user_id == test_user.id))
    assert progress is not None
    assert progress.lessons_completed == 1
    assert progress.progress_percentage == 100
    assert xp is not None
    assert xp.total_xp == 10
