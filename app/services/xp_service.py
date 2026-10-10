from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.xp import UserXP
from app.models.xp_event import XPEvent

XP_REWARDS = {
    "lesson": 10,
    "practice": 15,
    "quiz": 20,
    "challenge": 30,
}


def get_user_xp(db: Session, user_id: int) -> UserXP | None:
    return db.scalar(select(UserXP).where(UserXP.user_id == user_id))


def create_user_xp(db: Session, user_id: int) -> UserXP:
    user_xp = UserXP(
        user_id=user_id,
        total_xp=0,
        level=1,
    )
    db.add(user_xp)
    db.flush()
    return user_xp


def get_xp_event(
    db: Session,
    user_id: int,
    activity_type: str,
    activity_id: int,
    event_type: str,
) -> XPEvent | None:
    return db.scalar(
        select(XPEvent).where(
            XPEvent.user_id == user_id,
            XPEvent.activity_type == activity_type,
            XPEvent.activity_id == activity_id,
            XPEvent.event_type == event_type,
        )
    )


def award_activity_xp(
    db: Session,
    user_id: int,
    activity_type: str,
    activity_id: int,
) -> XPEvent:
    xp_amount = XP_REWARDS.get(activity_type)

    if xp_amount is None:
        raise ValueError("Invalid activity type")

    event_type = "completion"

    existing_event = get_xp_event(db, user_id, activity_type, activity_id, event_type)

    if existing_event is not None:
        return existing_event

    user_xp = get_user_xp(db, user_id)

    if user_xp is None:
        user_xp = create_user_xp(db, user_id)

    xp_event = XPEvent(
        user_id=user_id,
        activity_type=activity_type,
        activity_id=activity_id,
        event_type=event_type,
        xp_amount=xp_amount,
    )

    # Try inserting the event in a savepoint.
    # If the unique constraint rejects it, the outer
    # transaction can remain usable.
    try:
        with db.begin_nested():
            db.add(xp_event)
            db.flush()
    except IntegrityError:
        existing_event = get_xp_event(
            db, user_id, activity_type, activity_id, event_type
        )

        if existing_event is not None:
            return existing_event

        # It may be a different database constraint failure.
        raise

    # Update the balance only after the event insert succeeds.
    user_xp.total_xp += xp_amount
    user_xp.level = (user_xp.total_xp // 100) + 1

    db.flush()
    return xp_event
