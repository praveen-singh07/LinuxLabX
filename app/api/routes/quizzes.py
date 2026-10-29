from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.quiz import (
    QuizAttemptHistoryItem,
    QuizPublic,
    QuizResult,
    QuizSubmit,
    QuizSummary,
)
from app.services.quiz_service import (
    get_published_quiz,
    list_published_quizzes,
    list_user_attempts,
    submit_quiz,
)

router = APIRouter(prefix="/quizzes", tags=["Quizzes"])


@router.get("", response_model=list[QuizSummary])
def list_quizzes(db: Session = Depends(get_db)):
    quizzes = list_published_quizzes(db)
    return [
        QuizSummary(
            id=quiz.id,
            title=quiz.title,
            description=quiz.description,
            difficulty=quiz.difficulty,
            question_count=len(quiz.questions),
        )
        for quiz in quizzes
    ]


@router.get("/{quiz_id}", response_model=QuizPublic)
def quiz_detail(quiz_id: int, db: Session = Depends(get_db)):
    quiz = get_published_quiz(db, quiz_id)
    if quiz is None:
        raise HTTPException(status_code=404, detail="Published quiz not found")
    return quiz


@router.post("/{quiz_id}/attempts", response_model=QuizResult)
def attempt_quiz(
    quiz_id: int,
    data: QuizSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        attempt, passed, xp_awarded, user_xp, progress = submit_quiz(
            db, current_user.id, quiz_id, data.answers
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from None
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from None
    return QuizResult(
        attempt_id=attempt.id,
        quiz_id=attempt.quiz_id,
        score=attempt.score,
        total_questions=attempt.total_questions,
        percentage=attempt.percentage,
        passed=passed,
        xp_awarded=xp_awarded,
        total_xp=user_xp.total_xp,
        level=user_xp.level,
        quizzes_completed=progress.quizzes_completed if progress else 0,
        submitted_at=attempt.submitted_at,
    )


@router.get("/attempts/me", response_model=list[QuizAttemptHistoryItem])
def my_quiz_attempts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_user_attempts(db, current_user.id)
