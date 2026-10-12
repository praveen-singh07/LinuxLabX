from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Lesson(Base):
    """Read-only lesson catalogue entry. Does not alter existing tables."""

    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    command: Mapped[str | None] = mapped_column(String(160), nullable=True)
    syntax: Mapped[str] = mapped_column(Text, nullable=False, default="")
    examples: Mapped[list[dict[str, str]]] = mapped_column(
        JSON, nullable=False, default=list
    )
    expected_output: Mapped[str] = mapped_column(Text, nullable=False, default="")
    options: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    tips: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    common_mistakes: Mapped[list[str]] = mapped_column(
        JSON, nullable=False, default=list
    )
    difficulty: Mapped[str] = mapped_column(
        String(20), nullable=False, default="beginner", index=True
    )
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
