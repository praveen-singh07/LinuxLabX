from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_admin
from app.models.user import User
from app.schemas.practice import PracticeExerciseAdmin, PracticeExerciseCreate
from app.services.practice_service import (
    create_exercise,
    delete_exercise,
    get_exercise_for_admin,
    list_all_exercises,
    replace_exercise,
    set_exercise_published,
)

router = APIRouter(
    prefix="/admin/practice",
    tags=["Admin - Practice Management"],
    dependencies=[Depends(require_admin)],
)


@router.get("", response_model=list[PracticeExerciseAdmin])
def admin_list_practice(db: Session = Depends(get_db)):
    return list_all_exercises(db)


@router.post(
    "", response_model=PracticeExerciseAdmin, status_code=status.HTTP_201_CREATED
)
def admin_create_practice(
    data: PracticeExerciseCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    return create_exercise(db, data)


@router.put("/{exercise_id}", response_model=PracticeExerciseAdmin)
def admin_update_practice(
    exercise_id: int,
    data: PracticeExerciseCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    exercise = get_exercise_for_admin(db, exercise_id)
    if exercise is None:
        raise HTTPException(status_code=404, detail="Practice exercise not found")
    return replace_exercise(db, exercise, data)


@router.patch("/{exercise_id}/publish", response_model=PracticeExerciseAdmin)
def admin_publish_practice(
    exercise_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    exercise = get_exercise_for_admin(db, exercise_id)
    if exercise is None:
        raise HTTPException(status_code=404, detail="Practice exercise not found")
    return set_exercise_published(db, exercise, True)


@router.patch("/{exercise_id}/unpublish", response_model=PracticeExerciseAdmin)
def admin_unpublish_practice(
    exercise_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    exercise = get_exercise_for_admin(db, exercise_id)
    if exercise is None:
        raise HTTPException(status_code=404, detail="Practice exercise not found")
    return set_exercise_published(db, exercise, False)


@router.delete("/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_practice(
    exercise_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    exercise = get_exercise_for_admin(db, exercise_id)
    if exercise is None:
        raise HTTPException(status_code=404, detail="Practice exercise not found")
    try:
        delete_exercise(db, exercise)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from None
    return Response(status_code=status.HTTP_204_NO_CONTENT)
