from pydantic import BaseModel


class TopicProgress(BaseModel):
    topic_id: int
    title: str
    total_lessons: int
    completed_lessons: int
    progress_percent: int


class LearningPathProgress(BaseModel):
    learning_path_id: int
    title: str
    total_lessons: int
    completed_lessons: int
    progress_percent: int
    is_complete: bool
    next_lesson_id: int | None = None
    next_lesson_title: str | None = None
    next_topic_title: str | None = None
    topics: list[TopicProgress]
