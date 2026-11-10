from datetime import UTC, date, datetime, time, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.challenge import ChallengeAttempt
from app.models.lesson_completion import LessonCompletion
from app.models.practice import PracticeAttempt
from app.models.quiz_attempt import QuizAttempt
from app.models.user import User
from app.models.xp_event import XPEvent
from app.schemas.admin_analytics import AdminAnalyticsDay, AdminAnalyticsResponse


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _window_start(column, day: date) -> datetime:
    value = datetime.combine(day, time.min, tzinfo=UTC)
    if getattr(column.type, "timezone", False):
        return value
    return value.replace(tzinfo=None)


def get_admin_analytics(db: Session, days: int = 7) -> AdminAnalyticsResponse:
    end_date = datetime.now(UTC).date()
    start_date = end_date - timedelta(days=days - 1)
    totals_by_day = {
        start_date + timedelta(days=index): {
            "learners": set(),
            "activities": 0,
            "xp": 0,
        }
        for index in range(days)
    }

    def add_activities(model, timestamp_column) -> None:
        rows = db.execute(
            select(model.user_id, timestamp_column)
            .join(User, User.id == model.user_id)
            .where(
                User.role == "student",
                User.is_active.is_(True),
                timestamp_column >= _window_start(timestamp_column, start_date),
                timestamp_column < _window_start(
                    timestamp_column, end_date + timedelta(days=1)
                ),
            )
        ).all()
        for user_id, timestamp in rows:
            day = _as_utc(timestamp).date()
            if day in totals_by_day:
                totals_by_day[day]["learners"].add(user_id)
                totals_by_day[day]["activities"] += 1

    add_activities(LessonCompletion, LessonCompletion.completed_at)
    add_activities(QuizAttempt, QuizAttempt.submitted_at)
    add_activities(PracticeAttempt, PracticeAttempt.submitted_at)
    add_activities(ChallengeAttempt, ChallengeAttempt.submitted_at)

    xp_rows = db.execute(
        select(XPEvent.user_id, XPEvent.created_at, XPEvent.xp_amount)
        .join(User, User.id == XPEvent.user_id)
        .where(
            User.role == "student",
            User.is_active.is_(True),
            XPEvent.event_type == "completion",
            XPEvent.created_at >= _window_start(XPEvent.created_at, start_date),
            XPEvent.created_at
            < _window_start(XPEvent.created_at, end_date + timedelta(days=1)),
        )
    ).all()
    for _, timestamp, xp_amount in xp_rows:
        day = _as_utc(timestamp).date()
        if day in totals_by_day:
            totals_by_day[day]["xp"] += xp_amount

    daily = [
        AdminAnalyticsDay(
            day=day,
            active_learners=len(values["learners"]),
            activities=values["activities"],
            xp_earned=values["xp"],
        )
        for day, values in totals_by_day.items()
    ]
    unique_learners = set().union(
        *(values["learners"] for values in totals_by_day.values())
    )
    return AdminAnalyticsResponse(
        start_date=start_date,
        end_date=end_date,
        days=days,
        active_learners=len(unique_learners),
        activities=sum(day.activities for day in daily),
        xp_earned=sum(day.xp_earned for day in daily),
        daily=daily,
    )
