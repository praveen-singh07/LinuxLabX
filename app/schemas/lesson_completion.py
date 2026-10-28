from datetime import datetime

from pydantic import BaseModel, ConfigDict


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

    model_config = ConfigDict(from_attributes=True)


class LessonCompletionItem(BaseModel):
    lesson_id: int
    title: str
    completed_at: datetime

    model_config = ConfigDict(from_attributes=True)
