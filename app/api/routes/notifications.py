from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.notification import NotificationItem, NotificationListResponse, ReminderResponse
from app.services.notification_service import (
    create_daily_goal_reminder, list_notifications, mark_all_notifications_read,
    mark_notification_read,
)

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/me", response_model=NotificationListResponse)
def read_my_notifications(
    limit: int = Query(default=10, ge=1, le=50),
    offset: int = Query(default=0, ge=0, le=500),
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
):
    return list_notifications(db, current_user.id, limit, offset)


@router.patch("/{notification_id}/read", response_model=NotificationItem)
def read_notification(
    notification_id: int, db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notification = mark_notification_read(db, current_user.id, notification_id)
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    return NotificationItem(
        id=notification.id, category=notification.category, title=notification.title,
        message=notification.message, action_url=notification.action_url,
        created_at=notification.created_at, is_read=notification.read_at is not None,
    )


@router.post("/read-all")
def read_all_notifications(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
):
    return {"updated_count": mark_all_notifications_read(db, current_user.id)}


@router.post("/daily-goal-reminder", response_model=ReminderResponse)
def create_goal_reminder(
    timezone: str = Query(default="UTC", min_length=1, max_length=64),
    utc_offset_minutes: int | None = Query(default=None, ge=-840, le=840),
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
):
    try:
        return create_daily_goal_reminder(db, current_user.id, timezone, utc_offset_minutes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None
