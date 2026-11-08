from datetime import UTC, datetime, timedelta

from app.core.security import hash_password
from app.models.user import User
from app.models.xp import UserXP
from app.models.xp_event import XPEvent


def test_streak_counts_distinct_activity_days_in_requested_timezone(
    client, db, auth_headers, test_user
):
    today = datetime.now(UTC).replace(hour=12, minute=0, second=0, microsecond=0)
    for activity_id, days_ago in enumerate((0, 0, 1, 3, 4), start=1):
        db.add(
            XPEvent(
                user_id=test_user.id,
                activity_type="lesson",
                activity_id=activity_id,
                event_type="completion",
                xp_amount=10,
                created_at=(today - timedelta(days=days_ago)).replace(tzinfo=None),
            )
        )
    db.commit()

    response = client.get(
        "/gamification/streak?timezone=UTC", headers=auth_headers
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["current_streak"] == 2
    assert body["longest_streak"] == 2
    assert body["active_days"] == 4
    assert body["last_active_date"] == today.date().isoformat()


def test_streak_rejects_unknown_timezone(client, auth_headers):
    response = client.get(
        "/gamification/streak?timezone=Not/A_Real_Zone", headers=auth_headers
    )

    assert response.status_code == 400


def test_streak_accepts_browser_offset_for_windows_timezone_fallback(
    client, auth_headers
):
    response = client.get(
        "/gamification/streak?timezone=Asia%2FKolkata&utc_offset_minutes=-330",
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    assert response.json()["timezone"] == "Asia/Kolkata"


def test_leaderboard_ranks_active_students_and_marks_current_user(
    client, db, auth_headers, test_user, admin_user
):
    other_student = User(
        name="High Scorer",
        email="high.scorer@example.com",
        password_hash=hash_password("TestPassword123!"),
        role="student",
        is_active=True,
    )
    inactive_student = User(
        name="Inactive Learner",
        email="inactive@example.com",
        password_hash=hash_password("TestPassword123!"),
        role="student",
        is_active=False,
    )
    db.add_all([other_student, inactive_student])
    db.flush()
    db.add_all(
        [
            UserXP(user_id=test_user.id, total_xp=500, level=6),
            UserXP(user_id=other_student.id, total_xp=800, level=9),
            UserXP(user_id=admin_user.id, total_xp=5000, level=51),
            UserXP(user_id=inactive_student.id, total_xp=9000, level=91),
        ]
    )
    db.commit()

    response = client.get("/gamification/leaderboard?limit=10", headers=auth_headers)

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["current_user_rank"] == 2
    assert [entry["name"] for entry in body["entries"]] == [
        "High Scorer",
        test_user.name,
    ]
    assert body["entries"][1]["is_current_user"] is True
