from datetime import UTC, datetime, timedelta

from app.models.challenge import Challenge, ChallengeAttempt
from app.models.lesson import Lesson
from app.models.lesson_completion import LessonCompletion
from app.models.practice import PracticeAttempt, PracticeExercise
from app.models.quiz import Quiz
from app.models.quiz_attempt import QuizAttempt


def test_activity_feed_requires_authentication(client):
    response = client.get("/activity/me")

    assert response.status_code == 401


def test_activity_feed_merges_latest_activity_types_and_keeps_user_data_private(
    client, db, auth_headers, test_user, admin_user
):
    now = datetime.now(UTC).replace(microsecond=0, tzinfo=None)
    lesson = Lesson(title="List files", syntax="ls", is_published=True)
    quiz = Quiz(title="Filesystem quiz", difficulty="beginner", is_published=True)
    practice = PracticeExercise(
        title="Find the current folder",
        instructions="Enter the command",
        expected_answers=["pwd"],
        is_published=True,
    )
    challenge = Challenge(
        title="Inspect a directory",
        scenario="A directory needs inspection",
        instructions="Choose the command",
        expected_answers=["ls"],
        is_published=True,
    )
    db.add_all([lesson, quiz, practice, challenge])
    db.flush()
    db.add_all(
        [
            LessonCompletion(
                user_id=test_user.id,
                lesson_id=lesson.id,
                completed_at=now - timedelta(minutes=4),
            ),
            QuizAttempt(
                user_id=test_user.id,
                quiz_id=quiz.id,
                score=4,
                total_questions=5,
                percentage=80,
                answers=[],
                submitted_at=now - timedelta(minutes=2),
            ),
            PracticeAttempt(
                user_id=test_user.id,
                exercise_id=practice.id,
                submitted_answer="ls",
                is_correct=False,
                submitted_at=now - timedelta(minutes=3),
            ),
            ChallengeAttempt(
                user_id=test_user.id,
                challenge_id=challenge.id,
                submitted_answer="ls",
                is_correct=True,
                submitted_at=now - timedelta(minutes=1),
            ),
            LessonCompletion(
                user_id=admin_user.id,
                lesson_id=lesson.id,
                completed_at=now + timedelta(days=1),
            ),
        ]
    )
    db.commit()

    response = client.get("/activity/me?limit=3", headers=auth_headers)

    assert response.status_code == 200, response.text
    items = response.json()["items"]
    assert [item["activity_type"] for item in items] == [
        "challenge",
        "quiz",
        "practice",
    ]
    assert [item["title"] for item in items] == [
        "Inspect a directory",
        "Filesystem quiz",
        "Find the current folder",
    ]
    assert items[0]["status"] == "Solved"
    assert items[1]["status"] == "Passed"
    assert items[2]["status"] == "Retry"
    assert response.json()["has_more"] is True
    assert response.json()["next_offset"] == 3
    timestamp = datetime.fromisoformat(items[0]["happened_at"].replace("Z", "+00:00"))
    assert timestamp.utcoffset() == timedelta(0)


def test_activity_feed_returns_empty_list_and_validates_limit(
    client, auth_headers
):
    response = client.get("/activity/me", headers=auth_headers)
    invalid_limit = client.get("/activity/me?limit=51", headers=auth_headers)
    invalid_offset = client.get("/activity/me?offset=501", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == {"items": [], "has_more": False, "next_offset": None}
    assert invalid_limit.status_code == 422
    assert invalid_offset.status_code == 422


def test_activity_feed_supports_global_offset_pagination(
    client, db, auth_headers, test_user
):
    now = datetime.now(UTC).replace(microsecond=0, tzinfo=None)
    lessons = [Lesson(title=f"Lesson {index}", syntax="ls", is_published=True) for index in range(3)]
    db.add_all(lessons)
    db.flush()
    db.add_all(
        [
            LessonCompletion(
                user_id=test_user.id,
                lesson_id=lesson.id,
                completed_at=now - timedelta(minutes=index),
            )
            for index, lesson in enumerate(lessons)
        ]
    )
    db.commit()

    first = client.get("/activity/me?limit=2&offset=0", headers=auth_headers)
    second = client.get("/activity/me?limit=2&offset=2", headers=auth_headers)

    assert first.status_code == second.status_code == 200
    first_items = first.json()["items"]
    second_items = second.json()["items"]
    assert [item["title"] for item in first_items + second_items] == [
        "Lesson 0",
        "Lesson 1",
        "Lesson 2",
    ]
    assert first.json()["has_more"] is True
    assert first.json()["next_offset"] == 2
    assert second.json()["has_more"] is False
    assert second.json()["next_offset"] is None
