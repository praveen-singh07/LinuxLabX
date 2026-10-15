from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Difficulty = Literal["beginner", "intermediate", "advanced"]


class LessonCreate(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    description: str = ""
    command: str | None = Field(default=None, max_length=160)
    syntax: str = ""
    examples: list[dict[str, str]] = Field(default_factory=list)
    expected_output: str = ""
    options: list[str] = Field(default_factory=list)
    tips: list[str] = Field(default_factory=list)
    common_mistakes: list[str] = Field(default_factory=list)
    difficulty: Difficulty = "beginner"
    display_order: int = Field(default=0, ge=0)
    # Draft by default: admins must explicitly publish a lesson.
    is_published: bool = False


class LessonAdminResponse(LessonCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
