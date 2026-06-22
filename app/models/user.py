from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Boolean
from sqlalchemy import DateTime

from datetime import datetime

from app.core.database import Base


class User(Base):

    __tablename__ = "users"


    id = Column(

        Integer,

        primary_key=True,

        index=True

    )


    username = Column(

        String(50),

        unique=True,

        nullable=False,

        index=True

    )


    email = Column(

        String(100),

        unique=True,

        nullable=False,

        index=True

    )


    hashed_password = Column(

        String(255),

        nullable=False

    )


    full_name = Column(

        String(100),

        nullable=True

    )


    avatar = Column(

        String(255),

        nullable=True,

        default="default.png"

    )


    bio = Column(

        String(500),

        nullable=True

    )


    xp = Column(

        Integer,

        default=0

    )


    level = Column(

        Integer,

        default=1

    )


    streak = Column(

        Integer,

        default=0

    )


    is_active = Column(

        Boolean,

        default=True

    )


    is_admin = Column(

        Boolean,

        default=False

    )


    created_at = Column(

        DateTime,

        default=datetime.utcnow

    )


    updated_at = Column(

        DateTime,

        default=datetime.utcnow,

        onupdate=datetime.utcnow

    )