from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_admin
from app.models.user import User
from app.schemas.lesson_admin import LessonAdminResponse, LessonCreate
from app.services.lesson_admin_service import (
    create_lesson,
    delete_lesson,
    get_lesson_for_admin,
    list_all_lessons,
    replace_lesson,
    set_lesson_published,
)

router = APIRouter(
    prefix="/admin/lessons",
    tags=["Admin - Lesson Management"],
    dependencies=[Depends(require_admin)],
)


@router.get("", response_model=list[LessonAdminResponse])
def admin_list_lessons(db: Session = Depends(get_db)) -> list:
    """List all lessons, including unpublished drafts (admin only)."""
    return list_all_lessons(db)


@router.post(
    "", response_model=LessonAdminResponse, status_code=status.HTTP_201_CREATED
)
def admin_create_lesson(
    data: LessonCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    return create_lesson(db, data)


@router.put("/{lesson_id}", response_model=LessonAdminResponse)
def admin_replace_lesson(
    lesson_id: int,
    data: LessonCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    lesson = get_lesson_for_admin(db, lesson_id)
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return replace_lesson(db, lesson, data)


@router.patch("/{lesson_id}/publish", response_model=LessonAdminResponse)
def admin_publish_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    lesson = get_lesson_for_admin(db, lesson_id)
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return set_lesson_published(db, lesson, True)


@router.patch("/{lesson_id}/unpublish", response_model=LessonAdminResponse)
def admin_unpublish_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    lesson = get_lesson_for_admin(db, lesson_id)
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return set_lesson_published(db, lesson, False)


@router.delete("/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> Response:
    lesson = get_lesson_for_admin(db, lesson_id)
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    delete_lesson(db, lesson)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
