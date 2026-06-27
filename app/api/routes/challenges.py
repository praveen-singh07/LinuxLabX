from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.schemas.challenge_schema import (
    ChallengeCreate,
    ChallengeResponse
)

from app.services.challenge_service import (
    create_challenge,
    get_all_challenges,
    get_challenge_by_slug
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
    "",
    response_model=list[ChallengeResponse]
)
def get_challenges(
    db: Session = Depends(get_db)
):

    return get_all_challenges(
        db
    )


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