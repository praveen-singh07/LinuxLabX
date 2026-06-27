from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.models.progress import Progress
from app.models.user import User

from app.api.dependencies.auth_dependencies import (
    get_current_user
)

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    completed_challenges = (
        db.query(Progress)
        .filter(
            Progress.user_id == current_user.id,
            Progress.completed == True
        )
        .count()
    )

    return {
        "username": current_user.username,
        "xp": current_user.xp,
        "level": current_user.level,
        "streak": current_user.streak,
        "completed_challenges": completed_challenges
    }