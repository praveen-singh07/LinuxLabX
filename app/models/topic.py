from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.learning_path import LearningPath
    from app.models.lesson import Lesson


class Topic(Base):
    """A topic in a learning path; existing lessons are linked through TopicLesson."""

    __tablename__ = "topics"
    __table_args__ = (
        UniqueConstraint("learning_path_id", "title", name="uq_topic_path_title"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    learning_path_id: Mapped[int] = mapped_column(
        ForeignKey("learning_paths.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    display_order: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, index=True
    )
    is_published: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # String targets avoid importing peer model modules at runtime.
    learning_path: Mapped[LearningPath] = relationship(
        "LearningPath", back_populates="topics"
    )
    lesson_links: Mapped[list[TopicLesson]] = relationship(
        "TopicLesson",
        back_populates="topic",
        cascade="all, delete-orphan",
        order_by="TopicLesson.display_order, TopicLesson.id",
    )


class TopicLesson(Base):
    """Association table keeps the existing lessons table unchanged."""

    __tablename__ = "topic_lessons"
    __table_args__ = (
        UniqueConstraint("topic_id", "lesson_id", name="uq_topic_lesson"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topic_id: Mapped[int] = mapped_column(
        ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True
    )
    lesson_id: Mapped[int] = mapped_column(
        ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, index=True
    )
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    topic: Mapped[Topic] = relationship("Topic", back_populates="lesson_links")
    lesson: Mapped[Lesson] = relationship("Lesson")
