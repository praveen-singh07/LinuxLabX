from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class UserXP(Base):
    __tablename__ = "user_xp"

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

    total_xp: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    level: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False
    )