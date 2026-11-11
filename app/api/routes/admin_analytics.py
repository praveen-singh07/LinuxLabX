from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_admin
from app.schemas.admin_analytics import AdminAnalyticsResponse
from app.services.admin_analytics_service import get_admin_analytics

router = APIRouter(
    prefix="/admin/analytics",
    tags=["Admin - Learning Analytics"],
    dependencies=[Depends(require_admin)],
)


@router.get("", response_model=AdminAnalyticsResponse)
def read_admin_analytics(
    days: int = Query(default=7, ge=7, le=30),
    db: Session = Depends(get_db),
):
    return get_admin_analytics(db, days)
