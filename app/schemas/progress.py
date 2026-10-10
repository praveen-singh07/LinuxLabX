from datetime import datetime

from pydantic import BaseModel


class ProgressResponse(BaseModel):
    lessons_completed: int
    practice_completed: int
    quizzes_completed: int
    challenges_completed: int
    progress_percentage: int
    last_activity: str | None
    last_activity_at: datetime | None

    model_config = {"from_attributes": True}