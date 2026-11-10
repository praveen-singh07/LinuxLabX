from datetime import date

from pydantic import BaseModel


class StreakResponse(BaseModel):
    current_streak: int
    longest_streak: int
    active_days: int
    active_days_this_week: int
    last_active_date: date | None
    timezone: str


class StreakCalendarDay(BaseModel):
    day: date
    is_active: bool
    is_today: bool
    is_future: bool


class StreakCalendarResponse(BaseModel):
    start_date: date
    end_date: date
    active_days: int
    timezone: str
    days: list[StreakCalendarDay]


class LeaderboardEntry(BaseModel):
    rank: int
    user_id: int
    name: str
    total_xp: int
    level: int
    is_current_user: bool


class LeaderboardResponse(BaseModel):
    entries: list[LeaderboardEntry]
    current_user_rank: int | None

