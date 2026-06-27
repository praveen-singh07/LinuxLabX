from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import func

from app.core.database import Base


class Progress(Base):

    __tablename__ = "progress"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    challenge_id = Column(
        Integer,
        ForeignKey("challenges.id"),
        nullable=False
    )

    completed = Column(
        Boolean,
        default=False
    )

    earned_xp = Column(
        Integer,
        default=0
    )

    completed_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )