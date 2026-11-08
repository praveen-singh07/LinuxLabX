from datetime import UTC, datetime, timedelta, timezone as fixed_timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.challenge import ChallengeAttempt
from app.models.practice import PracticeAttempt
from app.models.quiz_attempt import QuizAttempt
from app.models.user import User
from app.models.xp import UserXP
from app.models.xp_event import XPEvent
from app.schemas.gamification import (
    LeaderboardEntry,
    LeaderboardResponse,
    StreakResponse,
)


def get_streak(
    db: Session,
    user_id: int,
    timezone_name: str,
    utc_offset_minutes: int | None = None,
) -> StreakResponse:
    if timezone_name in {"UTC", "Etc/UTC", "GMT"}:
        timezone = UTC
    else:
        try:
            timezone = ZoneInfo(timezone_name)
        except (ZoneInfoNotFoundError, ValueError):
            if utc_offset_minutes is None:
                raise ValueError("Unknown timezone") from None
            # Windows hosts may not have the IANA timezone database installed yet.
            # The browser's live offset keeps streak day-boundaries usable meanwhile.
            timezone = fixed_timezone(timedelta(minutes=-utc_offset_minutes))

    timestamps: list[datetime] = list(
        db.scalars(
            select(XPEvent.created_at)
            .where(
                XPEvent.user_id == user_id,
                XPEvent.event_type == "completion",
            )
            .order_by(XPEvent.created_at.desc())
        ).all()
    )
    timestamps.extend(
        db.scalars(
            select(QuizAttempt.submitted_at).where(QuizAttempt.user_id == user_id)
        ).all()
    )
    timestamps.extend(
        db.scalars(
            select(PracticeAttempt.submitted_at).where(
                PracticeAttempt.user_id == user_id,
                PracticeAttempt.is_correct.is_(True),
            )
        ).all()
    )
    timestamps.extend(
        db.scalars(
            select(ChallengeAttempt.submitted_at).where(
                ChallengeAttempt.user_id == user_id,
                ChallengeAttempt.is_correct.is_(True),
            )
        ).all()
    )
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
