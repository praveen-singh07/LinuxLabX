from datetime import datetime

from pydantic import BaseModel


class AchievementState(BaseModel):
    id: int
    code: str
    title: str
    description: str
    category: str
    criteria: str
    icon_path: str
    unlocked: bool
    unlocked_at: datetime | None = None


class AchievementCollection(BaseModel):
    total: int
    unlocked_count: int
    achievements: list[AchievementState]
