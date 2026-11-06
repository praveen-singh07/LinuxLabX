from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.challenge import ChallengeAnswerSubmit, ChallengeHistoryItem, ChallengePublic, ChallengeResult
from app.services.challenge_service import get_published_challenge, list_published_challenges, list_user_challenge_attempts, submit_challenge_answer

router = APIRouter(prefix="/challenges", tags=["Challenges"])


@router.get("", response_model=list[ChallengePublic])
def challenge_catalog(db: Session = Depends(get_db)):
    return list_published_challenges(db)


@router.get("/attempts/me", response_model=list[ChallengeHistoryItem])
def my_challenge_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return list_user_challenge_attempts(db, current_user.id)


@router.get("/{challenge_id}", response_model=ChallengePublic)
def challenge_detail(challenge_id: int, db: Session = Depends(get_db)):
    challenge = get_published_challenge(db, challenge_id)
    if challenge is None:
        raise HTTPException(status_code=404, detail="Published challenge not found")
    return challenge


@router.post("/{challenge_id}/attempts", response_model=ChallengeResult)
def submit_answer(challenge_id: int, data: ChallengeAnswerSubmit, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        attempt, xp_awarded, xp, progress, newly_unlocked = submit_challenge_answer(db, current_user.id, challenge_id, data.answer)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from None
    return ChallengeResult(
        attempt_id=attempt.id, challenge_id=challenge_id, is_correct=attempt.is_correct,
        feedback="Challenge completed!" if attempt.is_correct else "Not quite. Review the scenario and hints, then try again.",
        xp_awarded=xp_awarded, total_xp=xp.total_xp, level=xp.level,
        challenges_completed=progress.challenges_completed, submitted_at=attempt.submitted_at,
        newly_unlocked=newly_unlocked,
    )
