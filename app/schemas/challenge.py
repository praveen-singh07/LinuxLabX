from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Difficulty = Literal["beginner", "intermediate", "advanced"]


class ChallengeCreate(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    description: str = Field(default="", max_length=5000)
    scenario: str = Field(min_length=1, max_length=10000)
    instructions: str = Field(min_length=1, max_length=10000)
    expected_answers: list[str] = Field(min_length=1, max_length=20)
    hints: list[str] = Field(default_factory=list, max_length=10)
    difficulty: Difficulty = "beginner"
    display_order: int = Field(default=0, ge=0)
    is_published: bool = False

    @field_validator("expected_answers")
    @classmethod
    def validate_answers(cls, answers):
        if any(not answer.strip() for answer in answers):
            raise ValueError("Expected answers cannot be empty")
        return answers

    @field_validator("hints")
    @classmethod
    def validate_hints(cls, hints):
        if any(not hint.strip() for hint in hints):
            raise ValueError("Hints cannot be empty")
        return hints


class ChallengeAnswerSubmit(BaseModel):
    answer: str = Field(min_length=1, max_length=2000)


class ChallengePublic(BaseModel):
    id: int
    title: str
    description: str
    scenario: str
    instructions: str
    hints: list[str]
    difficulty: Difficulty
    display_order: int
    model_config = ConfigDict(from_attributes=True)


class ChallengeAdmin(ChallengeCreate):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ChallengeResult(BaseModel):
    attempt_id: int
    challenge_id: int
    is_correct: bool
    feedback: str
    xp_awarded: int
    total_xp: int
    level: int
    challenges_completed: int
    submitted_at: datetime


class ChallengeHistoryItem(BaseModel):
    id: int
    challenge_id: int
    submitted_answer: str
    is_correct: bool
    submitted_at: datetime
    model_config = ConfigDict(from_attributes=True)
