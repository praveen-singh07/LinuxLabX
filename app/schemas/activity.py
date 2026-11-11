from datetime import datetime
from typing import Literal

from pydantic import BaseModel


ActivityType = Literal["lesson", "quiz", "practice", "challenge"]


class ActivityFeedItem(BaseModel):
    activity_id: int
    activity_type: ActivityType
    title: str
    status: str
    detail: str
    happened_at: datetime


class ActivityFeedResponse(BaseModel):
    items: list[ActivityFeedItem]
    has_more: bool = False
    next_offset: int | None = None
