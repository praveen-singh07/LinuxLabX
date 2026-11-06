from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.achievement import AchievementState


class LessonCompletionResponse(BaseModel):
    lesson_id: int
    completed: bool
    already_completed: bool
    completed_at: datetime
    xp_awarded: int
    total_xp: int
    level: int
    lessons_completed: int
    progress_percentage: int
    newly_unlocked: list[AchievementState] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class LessonCompletionItem(BaseModel):
    lesson_id: int
    title: str
    completed_at: datetime

    model_config = ConfigDict(from_attributes=True)
