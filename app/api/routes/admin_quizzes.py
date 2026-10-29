from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_admin
from app.models.user import User
from app.schemas.quiz import QuizAdminResponse, QuizCreate
from app.services.quiz_service import (
    create_quiz,
    delete_quiz,
    get_quiz_for_admin,
    list_all_quizzes,
    replace_quiz,
    set_quiz_published,
)

router = APIRouter(
    prefix="/admin/quizzes",
    tags=["Admin - Quiz Management"],
    dependencies=[Depends(require_admin)],
)


@router.get("", response_model=list[QuizAdminResponse])
def admin_list_quizzes(db: Session = Depends(get_db)):
    return list_all_quizzes(db)


@router.post("", response_model=QuizAdminResponse, status_code=status.HTTP_201_CREATED)
def admin_create_quiz(
    data: QuizCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    return create_quiz(db, data)


@router.put("/{quiz_id}", response_model=QuizAdminResponse)
def admin_replace_quiz(
    quiz_id: int,
    data: QuizCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    quiz = get_quiz_for_admin(db, quiz_id)
    if quiz is None:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return replace_quiz(db, quiz, data)


@router.patch("/{quiz_id}/publish", response_model=QuizAdminResponse)
def admin_publish_quiz(
    quiz_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    quiz = get_quiz_for_admin(db, quiz_id)
    if quiz is None:
        raise HTTPException(status_code=404, detail="Quiz not found")
    if not quiz.questions:
        raise HTTPException(
            status_code=400, detail="A quiz must have at least one question"
        )
    return set_quiz_published(db, quiz, True)


@router.patch("/{quiz_id}/unpublish", response_model=QuizAdminResponse)
def admin_unpublish_quiz(
    quiz_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    quiz = get_quiz_for_admin(db, quiz_id)
    if quiz is None:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return set_quiz_published(db, quiz, False)


@router.delete("/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_quiz(
    quiz_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> Response:
    quiz = get_quiz_for_admin(db, quiz_id)
    if quiz is None:
        raise HTTPException(status_code=404, detail="Quiz not found")
    delete_quiz(db, quiz)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
