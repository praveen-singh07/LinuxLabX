from sqlalchemy.orm import Session
from typing import cast

from app.models.user import User


def calculate_level(xp: int) -> int:

    if xp < 100:
        return 1

    if xp < 300:
        return 2

    if xp < 600:
        return 3

    if xp < 1000:
        return 4

    if xp < 1500:
        return 5

    return (xp // 500) + 2


def award_xp(
    db: Session,
    user: User,
    xp_amount: int
) -> User:

    current_xp = cast(int, user.xp)
    current_level = cast(int, user.level)

    new_xp = current_xp + xp_amount
    new_level = calculate_level(new_xp)

    setattr(user, "xp", new_xp)
    setattr(user, "level", new_level)

    db.commit()
    db.refresh(user)

    return user