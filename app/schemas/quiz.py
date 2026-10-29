from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Difficulty = Literal["beginner", "intermediate", "advanced"]


class QuizQuestionCreate(BaseModel):
    prompt: str = Field(min_length=1, max_length=2000)
    options: list[str] = Field(min_length=2, max_length=6)
    correct_option_index: int = Field(ge=0)
    explanation: str = Field(default="", max_length=4000)
    display_order: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def validate_correct_option(self):
        if self.correct_option_index >= len(self.options):
            raise ValueError("correct_option_index must refer to an existing option")
        if any(not option.strip() for option in self.options):
            raise ValueError("Options cannot be empty")
        return self


class QuizCreate(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    description: str = Field(default="", max_length=5000)
    difficulty: Difficulty = "beginner"
    questions: list[QuizQuestionCreate] = Field(min_length=1, max_length=100)
    is_published: bool = False


class QuizQuestionPublic(BaseModel):
    id: int
    prompt: str
    options: list[str]
    display_order: int

    model_config = ConfigDict(from_attributes=True)


class QuizPublic(BaseModel):
    id: int
    title: str
    description: str
    difficulty: Difficulty
    questions: list[QuizQuestionPublic]

    model_config = ConfigDict(from_attributes=True)


class QuizAdminQuestionResponse(QuizQuestionCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class QuizAdminResponse(BaseModel):
    id: int
    title: str
    description: str
    difficulty: Difficulty
    is_published: bool
    questions: list[QuizAdminQuestionResponse]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QuizSummary(BaseModel):
    id: int
    title: str
    description: str
    difficulty: Difficulty
    question_count: int

    model_config = ConfigDict(from_attributes=True)


class QuizAnswer(BaseModel):
    question_id: int
    selected_option_index: int = Field(ge=0)


class QuizSubmit(BaseModel):
    answers: list[QuizAnswer] = Field(min_length=1, max_length=100)


class QuizResult(BaseModel):
    attempt_id: int
    quiz_id: int
    score: int
    total_questions: int
    percentage: int
    passed: bool
    xp_awarded: int
    total_xp: int
    level: int
    quizzes_completed: int
    submitted_at: datetime


class QuizAttemptHistoryItem(BaseModel):
    id: int
    quiz_id: int
    score: int
    total_questions: int
    percentage: int
    submitted_at: datetime

    model_config = ConfigDict(from_attributes=True)
