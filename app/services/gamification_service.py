from datetime import UTC, datetime, time, timedelta, timezone as fixed_timezone, tzinfo
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.challenge import ChallengeAttempt
from app.models.daily_learning_goal import DailyLearningGoal
from app.models.practice import PracticeAttempt
from app.models.quiz_attempt import QuizAttempt
from app.models.user import User
from app.models.xp import UserXP
from app.models.xp_event import XPEvent
from app.schemas.gamification import (
    LeaderboardEntry,
    LeaderboardResponse,
    StreakCalendarDay,
    StreakCalendarResponse,
    StreakResponse,
)
from app.schemas.daily_learning_goal import DailyLearningGoalResponse


def _resolve_timezone(
    timezone_name: str, utc_offset_minutes: int | None
) -> tzinfo:
    if timezone_name in {"UTC", "Etc/UTC", "GMT"}:
        return UTC
    try:
        return ZoneInfo(timezone_name)
    except (ZoneInfoNotFoundError, ValueError):
        if utc_offset_minutes is None:
            raise ValueError("Unknown timezone") from None
        # Windows hosts may not have the IANA timezone database installed yet.
        return fixed_timezone(timedelta(minutes=-utc_offset_minutes))


def _get_or_create_daily_goal(db: Session, user_id: int) -> DailyLearningGoal:
    goal = db.scalar(
        select(DailyLearningGoal).where(DailyLearningGoal.user_id == user_id)
    )
    if goal is not None:
        return goal

    goal = DailyLearningGoal(user_id=user_id, target_xp=50)
    try:
        with db.begin_nested():
            db.add(goal)
            db.flush()
    except IntegrityError:
        goal = db.scalar(
            select(DailyLearningGoal).where(DailyLearningGoal.user_id == user_id)
        )
        if goal is None:
            raise
    return goal


def get_daily_learning_goal(
    db: Session,
    user_id: int,
    timezone_name: str,
    utc_offset_minutes: int | None = None,
) -> DailyLearningGoalResponse:
    timezone = _resolve_timezone(timezone_name, utc_offset_minutes)
    goal = _get_or_create_daily_goal(db, user_id)
    now_local = datetime.now(UTC).astimezone(timezone)
    day_start = datetime.combine(now_local.date(), time.min, tzinfo=timezone)
    next_day_start = day_start + timedelta(days=1)
    # XPEvent timestamps are stored as naive UTC datetimes in the current schema.
    start_utc = day_start.astimezone(UTC).replace(tzinfo=None)
    end_utc = next_day_start.astimezone(UTC).replace(tzinfo=None)
    earned_xp = db.scalar(
        select(func.coalesce(func.sum(XPEvent.xp_amount), 0)).where(
            XPEvent.user_id == user_id,
            XPEvent.event_type == "completion",
            XPEvent.created_at >= start_utc,
            XPEvent.created_at < end_utc,
        )
    ) or 0
    target_xp = goal.target_xp
    return DailyLearningGoalResponse(
        target_xp=target_xp,
        earned_xp=earned_xp,
        remaining_xp=max(0, target_xp - earned_xp),
        progress_percent=min(100, int(earned_xp * 100 / target_xp)),
        is_complete=earned_xp >= target_xp,
        local_date=now_local.date(),
        timezone=timezone_name,
    )


def set_daily_learning_goal(
    db: Session,
    user_id: int,
    target_xp: int,
    timezone_name: str,
    utc_offset_minutes: int | None = None,
) -> DailyLearningGoalResponse:
    _resolve_timezone(timezone_name, utc_offset_minutes)
    goal = _get_or_create_daily_goal(db, user_id)
    goal.target_xp = target_xp
    db.commit()
    return get_daily_learning_goal(db, user_id, timezone_name, utc_offset_minutes)


def _get_activity_timestamps(
    db: Session,
    user_id: int,
    start_utc: datetime | None = None,
    end_utc: datetime | None = None,
) -> list[datetime]:
    def read_timestamps(model, timestamp_column, *criteria) -> list[datetime]:
        statement = select(timestamp_column).where(model.user_id == user_id, *criteria)
        if start_utc is not None and end_utc is not None:
            start_bound = start_utc
            end_bound = end_utc
            if not getattr(timestamp_column.type, "timezone", False):
                start_bound = start_bound.replace(tzinfo=None)
                end_bound = end_bound.replace(tzinfo=None)
            statement = statement.where(
                timestamp_column >= start_bound,
                timestamp_column < end_bound,
            )
        return list(db.scalars(statement).all())

    return (
        read_timestamps(XPEvent, XPEvent.created_at, XPEvent.event_type == "completion")
        + read_timestamps(QuizAttempt, QuizAttempt.submitted_at)
        + read_timestamps(
            PracticeAttempt,
            PracticeAttempt.submitted_at,
            PracticeAttempt.is_correct.is_(True),
        )
        + read_timestamps(
            ChallengeAttempt,
            ChallengeAttempt.submitted_at,
            ChallengeAttempt.is_correct.is_(True),
        )
    )


def get_streak_calendar(
    db: Session,
    user_id: int,
    timezone_name: str,
    utc_offset_minutes: int | None = None,
) -> StreakCalendarResponse:
    timezone = _resolve_timezone(timezone_name, utc_offset_minutes)
    today = datetime.now(UTC).astimezone(timezone).date()
    start_date = today - timedelta(days=today.weekday() + 21)
    end_date = start_date + timedelta(days=27)
    start_utc = datetime.combine(start_date, time.min, tzinfo=timezone).astimezone(UTC)
    end_utc = datetime.combine(
        end_date + timedelta(days=1), time.min, tzinfo=timezone
    ).astimezone(UTC)
    active_dates = {
        (timestamp.replace(tzinfo=UTC) if timestamp.tzinfo is None else timestamp)
        .astimezone(timezone)
        .date()
        for timestamp in _get_activity_timestamps(db, user_id, start_utc, end_utc)
    }
    days = [
        StreakCalendarDay(
            day=start_date + timedelta(days=index),
            is_active=(start_date + timedelta(days=index)) in active_dates
            and (start_date + timedelta(days=index)) <= today,
            is_today=(start_date + timedelta(days=index)) == today,
            is_future=(start_date + timedelta(days=index)) > today,
        )
        for index in range(28)
    ]
    return StreakCalendarResponse(
        start_date=start_date,
        end_date=end_date,
        active_days=sum(day.is_active for day in days),
        timezone=timezone_name,
        days=days,
    )


def get_streak(
    db: Session,
    user_id: int,
    timezone_name: str,
    utc_offset_minutes: int | None = None,
) -> StreakResponse:
    timezone = _resolve_timezone(timezone_name, utc_offset_minutes)

    timestamps = _get_activity_timestamps(db, user_id)
    active_dates = sorted(
        {
            (timestamp.replace(tzinfo=UTC) if timestamp.tzinfo is None else timestamp)
            .astimezone(timezone)
            .date()
            for timestamp in timestamps
        }
    )

    if not active_dates:
        return StreakResponse(
            current_streak=0,
            longest_streak=0,
            active_days=0,
            active_days_this_week=0,
            last_active_date=None,
            timezone=timezone_name,
        )

    active_set = set(active_dates)
    today = datetime.now(UTC).astimezone(timezone).date()
    week_start = today - timedelta(days=today.weekday())
    current_anchor = today if today in active_set else today - timedelta(days=1)
    current_streak = 0
    while current_anchor in active_set:
        current_streak += 1
        current_anchor -= timedelta(days=1)

    longest_streak = 0
    run = 0
    previous = None
    for active_day in active_dates:
        run = run + 1 if previous and active_day == previous + timedelta(days=1) else 1
        longest_streak = max(longest_streak, run)
        previous = active_day

    return StreakResponse(
        current_streak=current_streak,
        longest_streak=longest_streak,
        active_days=len(active_dates),
        active_days_this_week=sum(
            day >= week_start and day <= today for day in active_dates
        ),
        last_active_date=active_dates[-1],
        timezone=timezone_name,
    )


def get_leaderboard(
    db: Session, current_user_id: int, limit: int = 10
) -> LeaderboardResponse:
    rows = db.execute(
        select(User, UserXP)
        .outerjoin(UserXP, UserXP.user_id == User.id)
        .where(User.is_active.is_(True), User.role == "student")
        .order_by(func.coalesce(UserXP.total_xp, 0).desc(), User.id.asc())
    ).all()
    ranked = [
        (rank, user, xp.total_xp if xp else 0, xp.level if xp else 1)
        for rank, (user, xp) in enumerate(rows, start=1)
    ]
    current_rank = next(
        (rank for rank, user, _, _ in ranked if user.id == current_user_id), None
    )
    entries = [
        LeaderboardEntry(
            rank=rank,
            user_id=user.id,
            name=user.name,
            total_xp=total_xp,
            level=level,
            is_current_user=user.id == current_user_id,
        )
        for rank, user, total_xp, level in ranked[:limit]
    ]
    return LeaderboardResponse(entries=entries, current_user_rank=current_rank)
