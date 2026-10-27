from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LearningPathWrite(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    description: str = ""
    display_order: int = Field(default=0, ge=0)
    is_published: bool = False


class TopicWrite(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    description: str = ""
    display_order: int = Field(default=0, ge=0)
    is_published: bool = False


class LessonLinkWrite(BaseModel):
    lesson_id: int = Field(gt=0)
    display_order: int = Field(default=0, ge=0)


class LessonInTopic(BaseModel):
    id: int
    title: str
    description: str
    command: str | None
    difficulty: str
    display_order: int

    model_config = ConfigDict(from_attributes=True)


class TopicSummary(BaseModel):
    id: int
    learning_path_id: int
    title: str
    description: str
    display_order: int
    is_published: bool
    lessons: list[LessonInTopic] = Field(default_factory=list)


class LearningPathSummary(BaseModel):
    id: int
    title: str
    description: str
    display_order: int
    topics_count: int = 0


class LearningPathDetail(LearningPathSummary):
    topics: list[TopicSummary] = Field(default_factory=list)


class LearningPathAdminResponse(LearningPathWrite):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class TopicAdminResponse(TopicWrite):
    id: int
    learning_path_id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
