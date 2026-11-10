from datetime import UTC, datetime, timedelta, timezone

from app.models.daily_learning_goal import DailyLearningGoal
from app.models.xp_event import XPEvent


def test_daily_goal_defaults_to_50_and_is_created_for_signed_in_user(
    client, db, auth_headers, test_user
):
    response = client.get("/gamification/daily-goal?timezone=UTC", headers=auth_headers)

    assert response.status_code == 200, response.text
    assert response.json() == {
        "target_xp": 50,
        "earned_xp": 0,
        "remaining_xp": 50,
        "progress_percent": 0,
        "is_complete": False,
        "local_date": datetime.now(UTC).date().isoformat(),
        "timezone": "UTC",
    }
    goal = db.query(DailyLearningGoal).one()
    assert goal.user_id == test_user.id


def test_daily_goal_counts_only_signed_in_users_xp_from_today(
    client, db, auth_headers, test_user, admin_user
):
    now = datetime.now(UTC).replace(tzinfo=None)
    db.add_all(
        [
            XPEvent(user_id=test_user.id, activity_type="lesson", activity_id=1, event_type="completion", xp_amount=15, created_at=now),
            XPEvent(user_id=test_user.id, activity_type="quiz", activity_id=1, event_type="completion", xp_amount=20, created_at=now),
            XPEvent(user_id=test_user.id, activity_type="lesson", activity_id=2, event_type="completion", xp_amount=100, created_at=now - timedelta(days=1)),
            XPEvent(user_id=admin_user.id, activity_type="challenge", activity_id=1, event_type="completion", xp_amount=80, created_at=now),
        ]
    )
    db.commit()

    response = client.get("/gamification/daily-goal?timezone=UTC", headers=auth_headers)

    assert response.status_code == 200, response.text
    assert response.json()["earned_xp"] == 35
    assert response.json()["remaining_xp"] == 15
    assert response.json()["progress_percent"] == 70
    assert response.json()["is_complete"] is False


def test_goal_can_be_updated_and_progress_is_capped_when_goal_is_met(
    client, db, auth_headers, test_user
):
    now = datetime.now(UTC).replace(tzinfo=None)
    db.add(
        XPEvent(
            user_id=test_user.id,
            activity_type="challenge",
            activity_id=1,
            event_type="completion",
            xp_amount=30,
            created_at=now,
        )
    )
    db.commit()

    response = client.put(
        "/gamification/daily-goal?timezone=UTC",
        headers=auth_headers,
        json={"target_xp": 25},
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["target_xp"] == 25
    assert body["earned_xp"] == 30
    assert body["remaining_xp"] == 0
    assert body["progress_percent"] == 100
    assert body["is_complete"] is True
    assert db.query(DailyLearningGoal).filter_by(user_id=test_user.id).one().target_xp == 25


def test_daily_goal_uses_local_midnight_for_timezone_day_boundaries(
    client, db, auth_headers, test_user
):
    local_timezone = timezone(timedelta(hours=5, minutes=30))
    local_now = datetime.now(UTC).astimezone(local_timezone)
    local_midnight = datetime.combine(
        local_now.date(), datetime.min.time(), tzinfo=local_timezone
    )
    utc_midnight = local_midnight.astimezone(UTC).replace(tzinfo=None)
    db.add_all(
        [
            XPEvent(user_id=test_user.id, activity_type="lesson", activity_id=1, event_type="completion", xp_amount=80, created_at=utc_midnight - timedelta(seconds=1)),
            XPEvent(user_id=test_user.id, activity_type="lesson", activity_id=2, event_type="completion", xp_amount=15, created_at=utc_midnight),
        ]
    )
    db.commit()

    response = client.get(
        "/gamification/daily-goal?timezone=Asia%2FKolkata&utc_offset_minutes=-330",
        headers=auth_headers,
    )

    assert response.status_code == 200, response.text
    assert response.json()["earned_xp"] == 15
    assert response.json()["timezone"] == "Asia/Kolkata"


def test_daily_goal_validates_targets_timezone_and_authentication(client, auth_headers):
    invalid_target = client.put(
        "/gamification/daily-goal?timezone=UTC",
        headers=auth_headers,
        json={"target_xp": 26},
    )
    invalid_timezone = client.get(
        "/gamification/daily-goal?timezone=Not%2FA_Real_Zone", headers=auth_headers
    )

    assert invalid_target.status_code == 422
    assert invalid_timezone.status_code == 400
    assert client.get("/gamification/daily-goal").status_code == 401
