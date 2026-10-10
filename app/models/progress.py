from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class UserProgress(Base):
    __tablename__ = "user_progress"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        unique=True,
        index=True
    )

    lessons_completed: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    practice_completed: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    quizzes_completed: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    challenges_completed: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    progress_percentage: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    last_activity: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    last_activity_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )