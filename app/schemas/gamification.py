from datetime import date

from pydantic import BaseModel


class StreakResponse(BaseModel):
    current_streak: int
    longest_streak: int
    active_days: int
    active_days_this_week: int
    last_active_date: date | None
    timezone: str


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

