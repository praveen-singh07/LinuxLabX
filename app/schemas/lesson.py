from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Difficulty = Literal["beginner", "intermediate", "advanced"]


class LessonSummary(BaseModel):
    id: int
    title: str
    description: str
    command: str | None
    difficulty: Difficulty
    display_order: int

    model_config = ConfigDict(from_attributes=True)


class LessonDetail(LessonSummary):
    syntax: str
    examples: list[dict[str, str]] = Field(default_factory=list)
    expected_output: str
    options: list[str] = Field(default_factory=list)
    tips: list[str] = Field(default_factory=list)
    common_mistakes: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
