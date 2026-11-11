from datetime import datetime
from typing import Literal

from pydantic import BaseModel


NotificationCategory = Literal["learning", "achievement", "reminder"]


class NotificationItem(BaseModel):
    id: int
    category: NotificationCategory
    title: str
    message: str
    action_url: str | None
    created_at: datetime
    is_read: bool


class NotificationListResponse(BaseModel):
    items: list[NotificationItem]
    unread_count: int
    has_more: bool
    next_offset: int | None


class ReminderResponse(BaseModel):
    status: Literal["created", "already_exists", "goal_complete"]
    notification: NotificationItem | None = None
    message: str
