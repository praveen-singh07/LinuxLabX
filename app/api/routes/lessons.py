from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.lesson import Lesson
from app.schemas.lesson import LessonDetail, LessonSummary
from app.services.lesson_service import (
    get_published_lesson,
    list_published_lessons,
)

router = APIRouter(prefix="/lessons", tags=["Lessons"])


@router.get("", response_model=list[LessonSummary])
def list_lessons(db: Session = Depends(get_db)) -> list[Lesson]:
    """Public, read-only catalogue; an empty catalogue returns []."""
    return list_published_lessons(db)


@router.get("/{lesson_id}", response_model=LessonDetail)
def lesson_detail(
    lesson_id: int,
    db: Session = Depends(get_db),
) -> Lesson:
    """Public, read-only lesson detail."""
    lesson = get_published_lesson(db, lesson_id)

    if lesson is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found",
        )

    return lesson