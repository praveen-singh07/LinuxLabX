from sqlalchemy import func, select

from app.models.achievement import Achievement, UserAchievement
from app.models.lesson_completion import LessonCompletion


def _create_published_lesson(client, admin_headers, *, title="Achievement Lesson"):
    response = client.post(
        "/admin/lessons",
        headers=admin_headers,
        json={
            "title": title,
            "description": "Lesson used by achievement tests.",
            "command": "pwd",
            "syntax": "pwd",
            "examples": [{"command": "pwd", "output": "/home/student"}],
            "expected_output": "/home/student",
            "options": [],
            "tips": [],
            "common_mistakes": [],
            "difficulty": "beginner",
            "display_order": 0,
            "is_published": True,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_achievement_collection_requires_authentication(client):
    response = client.get("/achievements/me")
    assert response.status_code == 401


def test_achievement_catalog_contains_twelve_locked_badges(client, auth_headers):
    response = client.get("/achievements/me", headers=auth_headers)

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["total"] == 12
    assert body["unlocked_count"] == 0
    assert len(body["achievements"]) == 12
    assert all(not badge["unlocked"] for badge in body["achievements"])
    assert all(badge["criteria"] and badge["icon_path"].endswith(".svg") for badge in body["achievements"])


def test_first_lesson_unlocks_first_steps_and_returns_new_badge(
    client, admin_headers, auth_headers, test_user, db
):
    lesson = _create_published_lesson(client, admin_headers)

    response = client.post(
        f"/lessons/{lesson['id']}/complete", headers=auth_headers
    )

    assert response.status_code == 200, response.text
    assert [badge["code"] for badge in response.json()["newly_unlocked"]] == [
        "first_steps"
    ]
    first_steps = db.scalar(
        select(Achievement).where(Achievement.code == "first_steps")
    )
    unlocked = db.scalar(
        select(UserAchievement).where(
            UserAchievement.user_id == test_user.id,
            UserAchievement.achievement_id == first_steps.id,
        )
    )
    assert unlocked is not None


def test_repeating_lesson_does_not_unlock_duplicate_badge(
    client, admin_headers, auth_headers, test_user, db
):
    lesson = _create_published_lesson(client, admin_headers)
    first = client.post(f"/lessons/{lesson['id']}/complete", headers=auth_headers)
    second = client.post(f"/lessons/{lesson['id']}/complete", headers=auth_headers)

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["newly_unlocked"] == []
    first_steps = db.scalar(
        select(Achievement).where(Achievement.code == "first_steps")
    )
    unlock_count = db.scalar(
        select(func.count(UserAchievement.id)).where(
            UserAchievement.user_id == test_user.id,
            UserAchievement.achievement_id == first_steps.id,
        )
    )
    assert unlock_count == 1
    completion_count = db.scalar(
        select(func.count(LessonCompletion.id)).where(
            LessonCompletion.user_id == test_user.id,
            LessonCompletion.lesson_id == lesson["id"],
        )
    )
    assert completion_count == 1


def test_perfect_quiz_unlocks_quiz_and_perfect_score_badges(
    client, published_quiz_id, auth_headers
):
    quiz = client.get(f"/quizzes/{published_quiz_id}")
    assert quiz.status_code == 200, quiz.text
    answers = [
        {"question_id": question["id"], "selected_option_index": expected_index}
        for question, expected_index in zip(quiz.json()["questions"], [0, 1])
    ]

    response = client.post(
        f"/quizzes/{published_quiz_id}/attempts",
        headers=auth_headers,
        json={"answers": answers},
    )

    assert response.status_code == 200, response.text
    assert response.json()["percentage"] == 100
    assert {badge["code"] for badge in response.json()["newly_unlocked"]} == {
        "quiz_master",
        "perfect_score",
    }


def test_unlocked_badges_are_private_to_each_user(
    client, admin_headers, auth_headers
):
    lesson = _create_published_lesson(client, admin_headers)
    completed = client.post(
        f"/lessons/{lesson['id']}/complete", headers=auth_headers
    )
    assert completed.status_code == 200

    registration = client.post(
        "/auth/register",
        json={
            "name": "Second Student",
            "email": "second.student@example.com",
            "password": "OtherSafePassword123!",
        },
    )
    assert registration.status_code == 201, registration.text
    login = client.post(
        "/auth/login",
        json={
            "email": "second.student@example.com",
            "password": "OtherSafePassword123!",
        },
    )
    assert login.status_code == 200, login.text
    other_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = client.get("/achievements/me", headers=other_headers)
    assert response.status_code == 200, response.text
    assert response.json()["unlocked_count"] == 0
    assert all(not badge["unlocked"] for badge in response.json()["achievements"])
