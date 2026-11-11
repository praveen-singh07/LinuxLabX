from datetime import UTC, datetime

from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.schemas.notification import NotificationItem, NotificationListResponse, ReminderResponse
from app.services.gamification_service import get_daily_learning_goal


def _to_item(notification: Notification) -> NotificationItem:
    return NotificationItem(
        id=notification.id,
        category=notification.category,
        title=notification.title,
        message=notification.message,
        action_url=notification.action_url,
        created_at=notification.created_at,
        is_read=notification.read_at is not None,
    )


def create_notification(
    db: Session,
    user_id: int,
    category: str,
    title: str,
    message: str,
    dedupe_key: str,
    action_url: str | None = None,
) -> tuple[Notification, bool]:
    existing = db.scalar(select(Notification).where(
        Notification.user_id == user_id, Notification.dedupe_key == dedupe_key
    ))
    if existing:
        return existing, False
    notification = Notification(
        user_id=user_id, category=category, title=title, message=message,
        dedupe_key=dedupe_key, action_url=action_url,
    )
    try:
        with db.begin_nested():
            db.add(notification)
            db.flush()
        return notification, True
    except IntegrityError:
        existing = db.scalar(select(Notification).where(
            Notification.user_id == user_id, Notification.dedupe_key == dedupe_key
        ))
        if existing is None:
            raise
        return existing, False


def create_badge_notifications(db: Session, user_id: int, badges: list[dict]) -> None:
    for badge in badges:
        create_notification(
            db, user_id, "achievement", f"Badge unlocked: {badge['title']}",
            badge["description"], f"badge-unlocked:{badge['code']}",
            "/app/dashboard#badge-collection-details",
        )


def list_notifications(db: Session, user_id: int, limit: int, offset: int) -> NotificationListResponse:
    rows = list(db.scalars(
        select(Notification).where(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc(), Notification.id.desc())
        .offset(offset).limit(limit + 1)
    ).all())
    has_more = len(rows) > limit
    rows = rows[:limit]
    unread = db.scalar(select(func.count(Notification.id)).where(
        Notification.user_id == user_id, Notification.read_at.is_(None)
    )) or 0
    return NotificationListResponse(
        items=[_to_item(row) for row in rows], unread_count=unread,
        has_more=has_more, next_offset=offset + len(rows) if has_more else None,
    )


def mark_notification_read(db: Session, user_id: int, notification_id: int) -> Notification | None:
    row = db.scalar(select(Notification).where(
        Notification.id == notification_id, Notification.user_id == user_id
    ))
    if row is None:
        return None
    if row.read_at is None:
        row.read_at = datetime.now(UTC).replace(tzinfo=None)
        db.commit()
        db.refresh(row)
    return row


def mark_all_notifications_read(db: Session, user_id: int) -> int:
    result = db.execute(update(Notification).where(
        Notification.user_id == user_id, Notification.read_at.is_(None)
    ).values(read_at=datetime.now(UTC).replace(tzinfo=None)))
    db.commit()
    return result.rowcount or 0


def create_daily_goal_reminder(
    db: Session, user_id: int, timezone_name: str, utc_offset_minutes: int | None
) -> ReminderResponse:
    goal = get_daily_learning_goal(db, user_id, timezone_name, utc_offset_minutes)
    if goal.is_complete:
        return ReminderResponse(status="goal_complete", message="You have already reached today's learning goal.")
    key = f"daily-goal:{goal.local_date.isoformat()}"
    notification, created = create_notification(
        db, user_id, "reminder", "Your daily Linux goal is waiting",
        f"You have {goal.remaining_xp} XP left to reach today's {goal.target_xp} XP goal. A short lesson or practice session will keep your streak moving.",
        key, "/app/dashboard#daily-goal-title",
    )
    db.commit()
    db.refresh(notification)
    return ReminderResponse(
        status="created" if created else "already_exists", notification=_to_item(notification),
        message="Reminder added to your notification center." if created else "Today's reminder is already in your notification center.",
    )
