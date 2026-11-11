from datetime import date
from typing import Literal

from pydantic import BaseModel


DailyGoalTarget = Literal[25, 50, 75, 100]


class DailyLearningGoalWrite(BaseModel):
    target_xp: DailyGoalTarget


class DailyLearningGoalResponse(BaseModel):
    target_xp: DailyGoalTarget
    earned_xp: int
    remaining_xp: int
    progress_percent: int
    is_complete: bool
    local_date: date
    timezone: str
