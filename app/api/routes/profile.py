from fastapi import APIRouter
from fastapi import Depends

from app.models.user import User

from app.schemas.user_schema import (
    UserProfileResponse
)

from app.api.dependencies.auth_dependencies import (
    get_current_user
)

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.models.achievement import Achievement

from app.schemas.achievement_schema import (
    AchievementResponse
)

router = APIRouter(
    prefix="/profile",
    tags=["Profile"]
)


@router.get(
    "/me",
    response_model=UserProfileResponse
)
def get_my_profile(
    current_user: User = Depends(
        get_current_user
    )
):

    return current_user



@router.get(
    "/achievements",
    response_model=list[AchievementResponse]
)
def get_my_achievements(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    achievements = (
        db.query(Achievement)
        .filter(
            Achievement.user_id == current_user.id
        )
        .all()
    )

    return achievements