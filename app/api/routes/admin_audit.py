from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_admin
from app.schemas.admin_audit import AdminAuditLogList
from app.services.admin_audit_service import list_admin_actions

router = APIRouter(
    prefix="/admin/audit-logs",
    tags=["Admin - Audit Log"],
    dependencies=[Depends(require_admin)],
)


@router.get("", response_model=AdminAuditLogList)
def admin_audit_logs(
    search: str | None = Query(default=None, max_length=100),
    action: Literal["all", "account.status", "account.role"] = "all",
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    return list_admin_actions(
        db, search=search, action=action, limit=limit, offset=offset
    )
