from datetime import UTC, datetime

from sqlalchemy import select

from app.core.security import create_access_token, hash_password
from app.models.notification import Notification
from app.models.user import User
from app.models.xp_event import XPEvent


def _other_headers(db):
    other = User(
        name="Another Student", email="another.student@example.com",
        password_hash=hash_password("AnotherPassword123!"), role="student", is_active=True,
    )
    db.add(other)
    db.commit()
    return {"Authorization": f"Bearer {create_access_token(user_id=other.id, role=other.role)}"}


def _lesson(client, admin_headers):
    response = client.post("/admin/lessons", headers=admin_headers, json={
        "title": "Files and folders", "description": "Learn pwd", "command": "pwd",
        "syntax": "pwd", "examples": [], "expected_output": "/home/student",
        "options": [], "tips": [], "common_mistakes": [], "difficulty": "beginner",
        "display_order": 0, "is_published": True,
    })
    assert response.status_code == 201, response.text
    return response.json()


def test_notification_endpoints_require_authentication(client):
    assert client.get("/notifications/me").status_code == 401
    assert client.post("/notifications/read-all").status_code == 401
    assert client.post("/notifications/daily-goal-reminder").status_code == 401


def test_lesson_completion_creates_one_learning_and_badge_notification(
    client, admin_headers, auth_headers, test_user, db
):
    lesson = _lesson(client, admin_headers)
    first = client.post(f"/lessons/{lesson['id']}/complete", headers=auth_headers)
    duplicate = client.post(f"/lessons/{lesson['id']}/complete", headers=auth_headers)
    assert first.status_code == duplicate.status_code == 200
    rows = list(db.scalars(select(Notification).where(Notification.user_id == test_user.id)).all())
    assert len(rows) == 2
    assert {row.category for row in rows} == {"learning", "achievement"}
    assert any("Files and folders" in row.message for row in rows)


def test_passed_quiz_and_new_badges_are_notified(client, published_quiz_id, auth_headers, test_user, db):
    quiz = client.get(f"/quizzes/{published_quiz_id}").json()
    result = client.post(f"/quizzes/{published_quiz_id}/attempts", headers=auth_headers, json={
        "answers": [
            {"question_id": question["id"], "selected_option_index": 0 if index == 0 else 1}
            for index, question in enumerate(quiz["questions"])
        ]
    })
    assert result.status_code == 200, result.text
    rows = list(db.scalars(select(Notification).where(Notification.user_id == test_user.id)).all())
    assert any(row.category == "learning" and "Quiz passed" == row.title for row in rows)
    assert any(row.category == "achievement" and "Quiz Master" in row.title for row in rows)


def test_correct_practice_and_challenge_are_notified(client, admin_headers, auth_headers, test_user, db):
    practice = client.post("/admin/practice", headers=admin_headers, json={
        "title": "Print working directory", "instructions": "Type pwd", "expected_answers": ["pwd"],
        "difficulty": "beginner", "display_order": 1, "is_published": False,
    }).json()
    assert client.patch(f"/admin/practice/{practice['id']}/publish", headers=admin_headers).status_code == 200
    practice_result = client.post(f"/practice/{practice['id']}/attempts", headers=auth_headers, json={"answer": "pwd"})
    assert practice_result.status_code == 200

    challenge = client.post("/admin/challenges", headers=admin_headers, json={
        "title": "Find system log", "scenario": "Find system.log", "instructions": "Use find",
        "expected_answers": ["find /var/log -name system.log"], "hints": [],
        "difficulty": "beginner", "display_order": 1, "is_published": False,
    }).json()
    assert client.patch(f"/admin/challenges/{challenge['id']}/publish", headers=admin_headers).status_code == 200
    challenge_result = client.post(f"/challenges/{challenge['id']}/attempts", headers=auth_headers, json={"answer": "find /var/log -name system.log"})
    assert challenge_result.status_code == 200

    rows = list(db.scalars(select(Notification).where(Notification.user_id == test_user.id)).all())
    learning_titles = {row.title for row in rows if row.category == "learning"}
    badge_titles = {row.title for row in rows if row.category == "achievement"}
    assert "Practice exercise solved" in learning_titles
    assert "Linux challenge solved" in learning_titles
    assert "Command Learner" in " ".join(badge_titles)
    assert "Challenge Solver" in " ".join(badge_titles)


def test_notification_list_is_private_and_mark_read_is_owner_scoped(client, db, auth_headers, test_user):
    own = Notification(user_id=test_user.id, category="learning", title="Lesson done", message="Nice work", dedupe_key="own")
    db.add(own)
    db.commit()
    other_headers = _other_headers(db)

    own_list = client.get("/notifications/me", headers=auth_headers)
    other_list = client.get("/notifications/me", headers=other_headers)
    assert own_list.status_code == other_list.status_code == 200
    assert [item["title"] for item in own_list.json()["items"]] == ["Lesson done"]
    assert other_list.json()["items"] == []
    assert other_list.json()["unread_count"] == 0
    assert client.patch(f"/notifications/{own.id}/read", headers=other_headers).status_code == 404


def test_read_one_is_idempotent_and_read_all_clears_count(client, db, auth_headers, test_user):
    rows = [Notification(user_id=test_user.id, category="learning", title=f"Update {index}", message="Details", dedupe_key=f"update:{index}") for index in range(3)]
    db.add_all(rows)
    db.commit()
    first = client.patch(f"/notifications/{rows[0].id}/read", headers=auth_headers)
    second = client.patch(f"/notifications/{rows[0].id}/read", headers=auth_headers)
    assert first.status_code == second.status_code == 200
    assert first.json()["is_read"] is True
    assert client.get("/notifications/me", headers=auth_headers).json()["unread_count"] == 2
    assert client.post("/notifications/read-all", headers=auth_headers).json()["updated_count"] == 2
    assert client.get("/notifications/me", headers=auth_headers).json()["unread_count"] == 0


def test_notification_list_paginates_and_counts_unread(client, db, auth_headers, test_user):
    db.add_all([
        Notification(user_id=test_user.id, category="reminder", title=f"Reminder {index}", message="Study", dedupe_key=f"reminder:{index}")
        for index in range(3)
    ])
    db.commit()
    first = client.get("/notifications/me?limit=2&offset=0", headers=auth_headers).json()
    second = client.get(f"/notifications/me?limit=2&offset={first['next_offset']}", headers=auth_headers).json()
    assert len(first["items"]) == 2
    assert first["has_more"] is True
    assert first["unread_count"] == 3
    assert len(second["items"]) == 1
    assert second["has_more"] is False


def test_daily_goal_reminder_is_idempotent_per_local_day(client, auth_headers):
    url = "/notifications/daily-goal-reminder?timezone=Asia%2FKolkata&utc_offset_minutes=-330"
    first = client.post(url, headers=auth_headers).json()
    second = client.post(url, headers=auth_headers).json()
    assert first["status"] == "created"
    assert second["status"] == "already_exists"
    assert first["notification"]["id"] == second["notification"]["id"]
    assert "50 XP" in first["notification"]["message"]


def test_daily_reminder_is_not_created_after_goal_is_complete(client, db, auth_headers, test_user):
    db.add(XPEvent(
        user_id=test_user.id, activity_type="lesson", activity_id=987,
        event_type="completion", xp_amount=50, created_at=datetime.now(UTC).replace(tzinfo=None),
    ))
    db.commit()
    result = client.post("/notifications/daily-goal-reminder?timezone=UTC", headers=auth_headers)
    assert result.status_code == 200
    assert result.json()["status"] == "goal_complete"
    assert result.json()["notification"] is None
    assert client.get("/notifications/me", headers=auth_headers).json()["items"] == []
