from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.daily_learning_goal import (
    DailyLearningGoalResponse,
    DailyLearningGoalWrite,
)
from app.schemas.gamification import (
    LeaderboardResponse,
    StreakCalendarResponse,
    StreakResponse,
)
from app.services.gamification_service import (
    get_daily_learning_goal,
    get_streak_calendar,
    get_leaderboard,
    get_streak,
    set_daily_learning_goal,
)

router = APIRouter(prefix="/gamification", tags=["Gamification"])


@router.get("/activity-calendar", response_model=StreakCalendarResponse)
def read_streak_calendar(
    timezone: str = Query(default="UTC", min_length=1, max_length=64),
    utc_offset_minutes: int | None = Query(default=None, ge=-840, le=840),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_streak_calendar(db, current_user.id, timezone, utc_offset_minutes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None


@router.get("/daily-goal", response_model=DailyLearningGoalResponse)
def read_daily_learning_goal(
    timezone: str = Query(default="UTC", min_length=1, max_length=64),
    utc_offset_minutes: int | None = Query(default=None, ge=-840, le=840),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        result = get_daily_learning_goal(
            db, current_user.id, timezone, utc_offset_minutes
        )
        db.commit()
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None


@router.put("/daily-goal", response_model=DailyLearningGoalResponse)
def update_daily_learning_goal(
    data: DailyLearningGoalWrite,
    timezone: str = Query(default="UTC", min_length=1, max_length=64),
    utc_offset_minutes: int | None = Query(default=None, ge=-840, le=840),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return set_daily_learning_goal(
            db,
            current_user.id,
            data.target_xp,
            timezone,
            utc_offset_minutes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None


@router.get("/streak", response_model=StreakResponse)
def read_streak(
    timezone: str = Query(default="UTC", min_length=1, max_length=64),
    utc_offset_minutes: int | None = Query(default=None, ge=-840, le=840),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_streak(db, current_user.id, timezone, utc_offset_minutes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None


@router.get("/leaderboard", response_model=LeaderboardResponse)
def read_leaderboard(
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_leaderboard(db, current_user.id, limit)
