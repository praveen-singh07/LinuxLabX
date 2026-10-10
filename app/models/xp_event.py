from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class XPEvent(Base):
    __tablename__ = "xp_events"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    activity_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    activity_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    event_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    xp_amount: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "activity_type",
            "activity_id",
            "event_type",
            name="uq_xp_event"
        ),
    )