from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy import DateTime
from sqlalchemy import func

from app.core.database import Base


class Submission(Base):

    __tablename__ = "submissions"

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

    submitted_command = Column(
        String(255),
        nullable=False
    )

    status = Column(
        String(20),
        default="pending"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )