from sqlalchemy import func, select

from app.models.progress import UserProgress
from app.models.quiz_attempt import QuizAttempt
from app.models.xp import UserXP
from app.models.xp_event import XPEvent


def _answers_for_quiz(client, quiz_id, selected_indexes=None):
    detail_response = client.get(f"/quizzes/{quiz_id}")
    assert detail_response.status_code == 200, detail_response.text
    questions = detail_response.json()["questions"]
    selected_indexes = selected_indexes or [q["display_order"] for q in questions]
    return [
        {"question_id": question["id"], "selected_option_index": selected}
        for question, selected in zip(questions, selected_indexes)
    ], questions


def test_repeated_quiz_attempt_awards_xp_only_once(
    client, login_headers, published_quiz_id
):
    answers, _ = _answers_for_quiz(client, published_quiz_id)
    first = client.post(
        f"/quizzes/{published_quiz_id}/attempts",
        json={"answers": answers},
        headers=login_headers,
    )
    second = client.post(
        f"/quizzes/{published_quiz_id}/attempts",
        json={"answers": answers},
        headers=login_headers,
    )

    assert first.status_code == 200, first.text
    assert second.status_code == 200, second.text
    assert first.json()["xp_awarded"] == 20
    assert second.json()["xp_awarded"] == 0
    assert second.json()["total_xp"] == 20
    assert second.json()["quizzes_completed"] == 1


def test_quiz_attempt_rejects_duplicate_question_answers(
    client, login_headers, published_quiz_id
):
    answers, _ = _answers_for_quiz(client, published_quiz_id)
    payload = {"answers": [answers[0], answers[0]]}
    response = client.post(
        f"/quizzes/{published_quiz_id}/attempts",
        json=payload,
        headers=login_headers,
    )
    assert response.status_code == 422


def test_quiz_attempt_rejects_question_from_another_quiz(
    client, admin_headers, login_headers, sample_quiz_payload, published_quiz_id
):
    other_payload = dict(sample_quiz_payload)
    other_payload["title"] = "Another Quiz"
    other_payload["questions"] = [
        dict(question) for question in sample_quiz_payload["questions"]
    ]
    created = client.post(
        "/admin/quizzes", json=other_payload, headers=admin_headers
    )
    assert created.status_code == 201, created.text
    other_question_id = created.json()["questions"][0]["id"]

    answers, _ = _answers_for_quiz(client, published_quiz_id)
    answers[0]["question_id"] = other_question_id
    response = client.post(
        f"/quizzes/{published_quiz_id}/attempts",
        json={"answers": answers},
        headers=login_headers,
    )
    assert response.status_code == 422


def test_invalid_quiz_submission_does_not_create_attempt_or_award_xp(
    client, login_headers, published_quiz_id, db, test_user
):
    answers, _ = _answers_for_quiz(client, published_quiz_id)
    answers[0]["selected_option_index"] = 99
    response = client.post(
        f"/quizzes/{published_quiz_id}/attempts",
        json={"answers": answers},
        headers=login_headers,
    )
    assert response.status_code == 422

    attempts = db.scalar(
        select(func.count(QuizAttempt.id)).where(
            QuizAttempt.user_id == test_user.id,
            QuizAttempt.quiz_id == published_quiz_id,
        )
    )
    xp_events = db.scalar(
        select(func.count(XPEvent.id)).where(
            XPEvent.user_id == test_user.id,
            XPEvent.activity_type == "quiz",
            XPEvent.activity_id == published_quiz_id,
            XPEvent.event_type == "completion",
        )
    )
    assert attempts == 0
    assert xp_events == 0
    assert db.scalar(
        select(UserXP).where(UserXP.user_id == test_user.id)
    ) is None
    assert db.scalar(
        select(UserProgress).where(UserProgress.user_id == test_user.id)
    ) is None


def test_quiz_attempt_history_only_contains_current_users_attempts(
    client, login_headers, published_quiz_id, db
):
    answers, _ = _answers_for_quiz(client, published_quiz_id)
    submitted = client.post(
        f"/quizzes/{published_quiz_id}/attempts",
        json={"answers": answers},
        headers=login_headers,
    )
    assert submitted.status_code == 200, submitted.text

    from app.core.security import hash_password
    from app.models.user import User

    other = User(
        name="History Student",
        email="history.student@example.com",
        password_hash=hash_password("HistoryPassword123!"),
        role="student",
        is_active=True,
    )
    db.add(other)
    db.commit()
    login = client.post(
        "/auth/login",
        json={"email": other.email, "password": "HistoryPassword123!"},
    )
    assert login.status_code == 200, login.text
    other_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = client.get("/quizzes/attempts/me", headers=other_headers)
    assert response.status_code == 200, response.text
    assert response.json() == []
