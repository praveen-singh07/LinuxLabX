from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.achievement import AchievementCollection
from app.services.achievement_service import get_user_achievement_collection

router = APIRouter(prefix="/achievements", tags=["Achievements"])


@router.get("/me", response_model=AchievementCollection)
def my_achievements(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    items = get_user_achievement_collection(db, current_user.id)
    return {
        "total": len(items),
        "unlocked_count": sum(item["unlocked"] for item in items),
        "achievements": items,
    }
