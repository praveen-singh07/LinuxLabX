from datetime import datetime
from typing import cast

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.models.challenge import Challenge
from app.models.progress import Progress
from app.models.user import User

from app.schemas.challenge_schema import (
    ChallengeCreate,
    ChallengeResponse
)

from app.services.challenge_service import (
    create_challenge,
    get_all_challenges,
    get_challenge_by_slug
)

from app.services.xp_service import award_xp

from app.api.dependencies.auth_dependencies import (
    get_current_user
)


router = APIRouter(
    prefix="/challenges",
    tags=["Challenges"]
)


@router.post(
    "/create",
    response_model=ChallengeResponse
)
def create_new_challenge(
    challenge_data: ChallengeCreate,
    db: Session = Depends(get_db)
):
    challenge = create_challenge(
        db,
        challenge_data
    )

    return challenge


@router.get(
    "/",
    response_model=list[ChallengeResponse]
)
def get_challenges(
    db: Session = Depends(get_db)
):
    return get_all_challenges(db)


@router.get(
    "/{slug}",
    response_model=ChallengeResponse
)
def get_single_challenge(
    slug: str,
    db: Session = Depends(get_db)
):
    challenge = get_challenge_by_slug(
        db,
        slug
    )

    if challenge is None:
        raise HTTPException(
            status_code=404,
            detail="Challenge not found"
        )

    return challenge


@router.post(
    "/complete/{challenge_id}"
)
def complete_challenge(
    challenge_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    challenge = (
        db.query(Challenge)
        .filter(
            Challenge.id == challenge_id
        )
        .first()
    )

    if challenge is None:
        raise HTTPException(
            status_code=404,
            detail="Challenge not found"
        )

    existing_progress = (
        db.query(Progress)
        .filter(
            Progress.user_id == current_user.id,
            Progress.challenge_id == challenge_id
        )
        .first()
    )

    if existing_progress:
        raise HTTPException(
            status_code=400,
            detail="Challenge already completed"
        )

    xp_reward = cast(int, challenge.xp_reward)
    challenge_db_id = cast(int, challenge.id)

    progress = Progress(
        user_id=current_user.id,
        challenge_id=challenge_db_id,
        completed=True,
        earned_xp=xp_reward,
        completed_at=datetime.utcnow()
    )

    db.add(progress)

    award_xp(
        db,
        current_user,
        xp_reward
    )

    db.commit()

    return {
        "message": "Challenge completed successfully",
        "xp_earned": xp_reward,
        "current_xp": int(current_user.xp),
        "current_level": int(current_user.level)
    }