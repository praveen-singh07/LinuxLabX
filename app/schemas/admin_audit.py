from datetime import datetime

from pydantic import BaseModel


class AdminAuditLogItem(BaseModel):
    id: int
    actor_user_id: int
    actor_name: str
    target_user_id: int
    target_name: str
    action: str
    previous_value: str
    new_value: str
    occurred_at: datetime


class AdminAuditLogList(BaseModel):
    items: list[AdminAuditLogItem]
    total: int
    limit: int
    offset: int
