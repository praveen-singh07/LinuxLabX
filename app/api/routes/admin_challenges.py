from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_admin
from app.models.user import User
from app.schemas.challenge import ChallengeAdmin, ChallengeCreate
from app.services.challenge_service import create_challenge, delete_challenge, get_challenge_for_admin, list_all_challenges, replace_challenge, set_challenge_published

router = APIRouter(prefix="/admin/challenges", tags=["Admin - Challenge Management"], dependencies=[Depends(require_admin)])


@router.get("", response_model=list[ChallengeAdmin])
def admin_list_challenges(db: Session = Depends(get_db)):
    return list_all_challenges(db)


@router.post("", response_model=ChallengeAdmin, status_code=status.HTTP_201_CREATED)
def admin_create_challenge(data: ChallengeCreate, db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    return create_challenge(db, data)


@router.put("/{challenge_id}", response_model=ChallengeAdmin)
def admin_update_challenge(challenge_id: int, data: ChallengeCreate, db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    challenge = get_challenge_for_admin(db, challenge_id)
    if challenge is None:
        raise HTTPException(status_code=404, detail="Challenge not found")
    return replace_challenge(db, challenge, data)


@router.patch("/{challenge_id}/publish", response_model=ChallengeAdmin)
def admin_publish_challenge(challenge_id: int, db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    challenge = get_challenge_for_admin(db, challenge_id)
    if challenge is None:
        raise HTTPException(status_code=404, detail="Challenge not found")
    return set_challenge_published(db, challenge, True)


@router.patch("/{challenge_id}/unpublish", response_model=ChallengeAdmin)
def admin_unpublish_challenge(challenge_id: int, db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    challenge = get_challenge_for_admin(db, challenge_id)
    if challenge is None:
        raise HTTPException(status_code=404, detail="Challenge not found")
    return set_challenge_published(db, challenge, False)


@router.delete("/{challenge_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_challenge(challenge_id: int, db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    challenge = get_challenge_for_admin(db, challenge_id)
    if challenge is None:
        raise HTTPException(status_code=404, detail="Challenge not found")
    try:
        delete_challenge(db, challenge)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from None
    return Response(status_code=status.HTTP_204_NO_CONTENT)
