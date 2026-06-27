from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import func

from app.core.database import Base


class Challenge(Base):

    __tablename__ = "challenges"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    title = Column(
        String(150),
        nullable=False
    )

    slug = Column(
        String(150),
        unique=True,
        nullable=False,
        index=True
    )

    description = Column(
        Text,
        nullable=False
    )

    category = Column(
        String(50),
        nullable=False
    )

    difficulty = Column(
        String(20),
        nullable=False
    )

    xp_reward = Column(
        Integer,
        default=100
    )

    estimated_minutes = Column(
        Integer,
        default=15
    )

    command_required = Column(
        String(100),
        nullable=True
    )

    is_active = Column(
        Boolean,
        default=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )