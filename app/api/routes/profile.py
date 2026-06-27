from fastapi import APIRouter
from fastapi import Depends

from app.models.user import User

from app.schemas.user_schema import (
    UserProfileResponse
)

from app.api.dependencies.auth_dependencies import (
    get_current_user
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