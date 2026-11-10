from datetime import UTC

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.admin_audit import AdminAuditLog
from app.schemas.admin_audit import AdminAuditLogItem, AdminAuditLogList


def record_admin_action(
    db: Session,
    *,
    actor_user_id: int,
    actor_name: str,
    target_user_id: int,
    target_name: str,
    action: str,
    previous_value: str,
    new_value: str,
) -> AdminAuditLog:
    entry = AdminAuditLog(
        actor_user_id=actor_user_id,
        actor_name=actor_name,
        target_user_id=target_user_id,
        target_name=target_name,
        action=action,
        previous_value=previous_value,
        new_value=new_value,
    )
    db.add(entry)
    return entry


def list_admin_actions(
    db: Session,
    *,
    search: str | None,
    action: str,
    limit: int,
    offset: int,
) -> AdminAuditLogList:
    statement = select(AdminAuditLog)
    count_statement = select(func.count(AdminAuditLog.id))
    if search:
        pattern = f"%{search.strip().lower()}%"
        criterion = or_(
            func.lower(AdminAuditLog.actor_name).like(pattern),
            func.lower(AdminAuditLog.target_name).like(pattern),
        )
        statement = statement.where(criterion)
        count_statement = count_statement.where(criterion)
    if action != "all":
        statement = statement.where(AdminAuditLog.action == action)
        count_statement = count_statement.where(AdminAuditLog.action == action)

    entries = db.scalars(
        statement.order_by(AdminAuditLog.occurred_at.desc(), AdminAuditLog.id.desc())
        .offset(offset)
        .limit(limit)
    ).all()
    items = [
        AdminAuditLogItem(
            id=entry.id,
            actor_user_id=entry.actor_user_id,
            actor_name=entry.actor_name,
            target_user_id=entry.target_user_id,
            target_name=entry.target_name,
            action=entry.action,
            previous_value=entry.previous_value,
            new_value=entry.new_value,
            occurred_at=(
                entry.occurred_at.replace(tzinfo=UTC)
                if entry.occurred_at.tzinfo is None
                else entry.occurred_at
            ),
        )
        for entry in entries
    ]
    return AdminAuditLogList(
        items=items,
        total=db.scalar(count_statement) or 0,
        limit=limit,
        offset=offset,
    )
