from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.practice import (
    PracticeAnswerSubmit,
    PracticeExercisePublic,
    PracticeHistoryItem,
    PracticeResult,
)
from app.services.practice_service import (
    get_published_exercise,
    list_published_exercises,
    list_user_practice_attempts,
    submit_practice_answer,
)

router = APIRouter(prefix="/practice", tags=["Practice"])


@router.get("", response_model=list[PracticeExercisePublic])
def practice_catalog(db: Session = Depends(get_db)):
    return list_published_exercises(db)


@router.get("/attempts/me", response_model=list[PracticeHistoryItem])
def my_practice_history(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return list_user_practice_attempts(db, current_user.id)


@router.get("/{exercise_id}", response_model=PracticeExercisePublic)
def practice_detail(exercise_id: int, db: Session = Depends(get_db)):
    exercise = get_published_exercise(db, exercise_id)
    if exercise is None:
        raise HTTPException(
            status_code=404, detail="Published practice exercise not found"
        )
    return exercise


@router.post("/{exercise_id}/attempts", response_model=PracticeResult)
def submit_answer(
    exercise_id: int,
    data: PracticeAnswerSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        attempt, xp_awarded, xp, progress = submit_practice_answer(
            db, current_user.id, exercise_id, data.answer
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from None
    return PracticeResult(
        attempt_id=attempt.id,
        exercise_id=exercise_id,
        is_correct=attempt.is_correct,
        feedback="Correct answer!"
        if attempt.is_correct
        else "Not quite. Review the instructions and try again.",
        xp_awarded=xp_awarded,
        total_xp=xp.total_xp,
        level=xp.level,
        practice_completed=progress.practice_completed,
        submitted_at=attempt.submitted_at,
    )
