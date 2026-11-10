from datetime import UTC, datetime, timedelta

from app.core.security import hash_password
from app.models.challenge import Challenge, ChallengeAttempt
from app.models.lesson import Lesson
from app.models.lesson_completion import LessonCompletion
from app.models.practice import PracticeAttempt, PracticeExercise
from app.models.quiz import Quiz
from app.models.quiz_attempt import QuizAttempt
from app.models.user import User
from app.models.xp_event import XPEvent


def test_admin_analytics_summarizes_recent_student_activity(
    client, db, admin_headers, test_user, admin_user
):
    lesson = Lesson(title="Linux lesson", syntax="", examples=[], options=[], tips=[], common_mistakes=[])
    old_lesson = Lesson(title="Older lesson", syntax="", examples=[], options=[], tips=[], common_mistakes=[])
    quiz = Quiz(title="Linux quiz", description="", difficulty="beginner", is_published=True)
    exercise = PracticeExercise(title="Practice", instructions="", expected_answers=[])
    challenge = Challenge(title="Challenge", scenario="", instructions="", expected_answers=[])
    db.add_all([lesson, old_lesson, quiz, exercise, challenge])
    db.flush()

    now = datetime.now(UTC).replace(hour=12, minute=0, second=0, microsecond=0, tzinfo=None)
    yesterday = now - timedelta(days=1)
    old = now - timedelta(days=8)
    db.add_all(
        [
            LessonCompletion(user_id=test_user.id, lesson_id=lesson.id, completed_at=yesterday),
            LessonCompletion(user_id=test_user.id, lesson_id=old_lesson.id, completed_at=old),
            QuizAttempt(user_id=test_user.id, quiz_id=quiz.id, score=1, total_questions=1, percentage=100, answers=[], submitted_at=now),
            PracticeAttempt(user_id=test_user.id, exercise_id=exercise.id, submitted_answer="pwd", is_correct=True, submitted_at=now),
            ChallengeAttempt(user_id=test_user.id, challenge_id=challenge.id, submitted_answer="ls", is_correct=True, submitted_at=yesterday),
            XPEvent(user_id=test_user.id, activity_type="quiz", activity_id=1, event_type="completion", xp_amount=20, created_at=now),
            XPEvent(user_id=test_user.id, activity_type="lesson", activity_id=1, event_type="completion", xp_amount=10, created_at=yesterday),
            XPEvent(user_id=test_user.id, activity_type="lesson", activity_id=2, event_type="completion", xp_amount=100, created_at=old),
            XPEvent(user_id=admin_user.id, activity_type="challenge", activity_id=3, event_type="completion", xp_amount=500, created_at=now),
        ]
    )
    db.commit()

    response = client.get("/admin/analytics?days=7", headers=admin_headers)

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["days"] == 7
    assert body["active_learners"] == 1
    assert body["activities"] == 4
    assert body["xp_earned"] == 30
    assert len(body["daily"]) == 7
    by_day = {entry["day"]: entry for entry in body["daily"]}
    assert by_day[now.date().isoformat()]["activities"] == 2
    assert by_day[now.date().isoformat()]["xp_earned"] == 20
    assert by_day[yesterday.date().isoformat()]["activities"] == 2
    assert by_day[yesterday.date().isoformat()]["xp_earned"] == 10


def test_admin_analytics_requires_admin_and_accepts_only_supported_window(
    client, auth_headers, admin_headers
):
    assert client.get("/admin/analytics").status_code == 401
    assert client.get("/admin/analytics", headers=auth_headers).status_code == 403
    invalid = client.get("/admin/analytics?days=6", headers=admin_headers)
    assert invalid.status_code == 422


def test_admin_page_includes_learning_analytics_panel(client):
    response = client.get("/app/admin")

    assert response.status_code == 200
    assert "Learning engagement" in response.text
    assert "analytics-chart" in response.text
