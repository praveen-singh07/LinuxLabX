from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Difficulty = Literal["beginner", "intermediate", "advanced"]


class PracticeExerciseCreate(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    description: str = Field(default="", max_length=5000)
    instructions: str = Field(min_length=1, max_length=10000)
    expected_answers: list[str] = Field(min_length=1, max_length=20)
    difficulty: Difficulty = "beginner"
    display_order: int = Field(default=0, ge=0)
    is_published: bool = False

    @field_validator("expected_answers")
    @classmethod
    def validate_answers(cls, answers):
        if any(not answer.strip() for answer in answers):
            raise ValueError("Expected answers cannot be empty")
        return answers


class PracticeAnswerSubmit(BaseModel):
    answer: str = Field(min_length=1, max_length=2000)


class PracticeExercisePublic(BaseModel):
    id: int
    title: str
    description: str
    instructions: str
    difficulty: Difficulty
    display_order: int
    model_config = ConfigDict(from_attributes=True)


class PracticeExerciseAdmin(PracticeExerciseCreate):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class PracticeResult(BaseModel):
    attempt_id: int
    exercise_id: int
    is_correct: bool
    feedback: str
    xp_awarded: int
    total_xp: int
    level: int
    practice_completed: int
    submitted_at: datetime


class PracticeHistoryItem(BaseModel):
    id: int
    exercise_id: int
    submitted_answer: str
    is_correct: bool
    submitted_at: datetime
    model_config = ConfigDict(from_attributes=True)
