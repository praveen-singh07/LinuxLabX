from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.activity import ActivityFeedResponse
from app.services.activity_service import get_activity_feed

router = APIRouter(prefix="/activity", tags=["Learning Activity"])


@router.get("/me", response_model=ActivityFeedResponse)
def read_my_activity(
    limit: int = Query(default=12, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_activity_feed(db, current_user.id, limit)
