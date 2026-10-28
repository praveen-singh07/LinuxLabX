from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.lesson_completion import (
    LessonCompletionItem,
    LessonCompletionResponse,
)
from app.services.lesson_completion_service import (
    complete_published_lesson,
    list_user_completions,
)

router = APIRouter(prefix="/lessons", tags=["Lesson Completion"])


@router.post(
    "/{lesson_id}/complete",
    response_model=LessonCompletionResponse,
    status_code=status.HTTP_200_OK,
)
def complete_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LessonCompletionResponse:
    try:
        completion, already_completed, xp_awarded, progress, xp = (
            complete_published_lesson(db, current_user.id, lesson_id)
        )
    except LookupError:
        raise HTTPException(status_code=404, detail="Published lesson not found") from None
    return LessonCompletionResponse(
        lesson_id=completion.lesson_id,
        completed=True,
        already_completed=already_completed,
        completed_at=completion.completed_at,
        xp_awarded=xp_awarded,
        total_xp=xp.total_xp,
        level=xp.level,
        lessons_completed=progress.lessons_completed,
        progress_percentage=progress.progress_percentage,
    )


@router.get("/completed/me", response_model=list[LessonCompletionItem])
def my_completed_lessons(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[LessonCompletionItem]:
    completions = list_user_completions(db, current_user.id)
    return [
        LessonCompletionItem(
            lesson_id=item.lesson_id,
            title=item.lesson.title,
            completed_at=item.completed_at,
        )
        for item in completions
    ]
