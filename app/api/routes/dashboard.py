from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.dashboard import DashboardResponse
from app.schemas.progress import ProgressResponse
from app.schemas.xp import XPResponse
from app.services.progress_service import get_user_progress
from app.services.xp_service import get_user_xp

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardResponse)
def get_dashboard(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    progress = get_user_progress(db, current_user.id)

    xp = get_user_xp(db, current_user.id)

    if xp is None:
        raise HTTPException(status_code=404, detail="User XP not found")

    if progress is None:
        raise HTTPException(status_code=404, detail="User progress not found")

    return DashboardResponse(
        user_id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        progress=ProgressResponse.model_validate(progress),
        xp=XPResponse.model_validate(xp),
    )
