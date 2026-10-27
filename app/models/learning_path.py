from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.topic import Topic

if TYPE_CHECKING:
    from app.models.topic import Topic

# Relationship inside LearningPath class:
topics: Mapped[list[Topic]] = relationship(
    "Topic",
    back_populates="learning_path",
    cascade="all, delete-orphan",
    order_by="Topic.display_order, Topic.id",
)


class LearningPath(Base):
    """An ordered, publishable learning path containing topics."""

    __tablename__ = "learning_paths"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
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

    topics: Mapped[list[Topic]] = relationship(
        back_populates="learning_path",
        cascade="all, delete-orphan",
        order_by="Topic.display_order, Topic.id",
    )
