import re

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.practice import PracticeAttempt, PracticeExercise
from app.services.progress_service import create_user_progress, get_user_progress
from app.services.xp_service import award_activity_xp, create_user_xp, get_user_xp


def normalize_answer(value: str) -> str:
    return re.sub(r"\\s+", " ", value.strip()).casefold()


def list_published_exercises(db: Session):
    return list(
        db.scalars(
            select(PracticeExercise)
            .where(PracticeExercise.is_published.is_(True))
            .order_by(PracticeExercise.display_order, PracticeExercise.id)
        ).all()
    )


def get_published_exercise(db: Session, exercise_id: int):
    return db.scalar(
        select(PracticeExercise).where(
            PracticeExercise.id == exercise_id, PracticeExercise.is_published.is_(True)
        )
    )


def list_all_exercises(db: Session):
    return list(
        db.scalars(
            select(PracticeExercise).order_by(
                PracticeExercise.display_order, PracticeExercise.id
            )
        ).all()
    )


def get_exercise_for_admin(db: Session, exercise_id: int):
    return db.get(PracticeExercise, exercise_id)


def create_exercise(db: Session, data):
    exercise = PracticeExercise(**data.model_dump())
    db.add(exercise)
    db.commit()
    db.refresh(exercise)
    return exercise


def replace_exercise(db: Session, exercise, data):
    for field, value in data.model_dump().items():
        setattr(exercise, field, value)
    db.commit()
    db.refresh(exercise)
    return exercise


def set_exercise_published(db: Session, exercise, published: bool):
    exercise.is_published = published
    db.commit()
    db.refresh(exercise)
    return exercise


def delete_exercise(db: Session, exercise):
    if (
        db.scalar(
            select(PracticeAttempt.id)
            .where(PracticeAttempt.exercise_id == exercise.id)
            .limit(1)
        )
        is not None
    ):
        raise ValueError(
            "Exercise has submissions and cannot be deleted; unpublish it instead"
        )
    db.delete(exercise)
    db.commit()


def submit_practice_answer(db: Session, user_id: int, exercise_id: int, answer: str):
    exercise = get_published_exercise(db, exercise_id)
    if exercise is None:
        raise LookupError("Published practice exercise not found")

    normalized = normalize_answer(answer)
    correct = any(
        normalized == normalize_answer(expected)
        for expected in exercise.expected_answers
    )

    progress = get_user_progress(db, user_id)
    if progress is None:
        progress = create_user_progress(db, user_id)
    xp = get_user_xp(db, user_id)
    if xp is None:
        xp = create_user_xp(db, user_id)

    already_completed = (
        db.scalar(
            select(PracticeAttempt.id)
            .where(
                PracticeAttempt.user_id == user_id,
                PracticeAttempt.exercise_id == exercise_id,
                PracticeAttempt.is_correct.is_(True),
            )
            .limit(1)
        )
        is not None
    )

    attempt = PracticeAttempt(
        user_id=user_id,
        exercise_id=exercise_id,
        submitted_answer=answer.strip(),
        is_correct=correct,
    )
    db.add(attempt)
    xp_awarded = 0
    if correct and not already_completed:
        event = award_activity_xp(db, user_id, "practice", exercise_id)
        xp_awarded = event.xp_amount
        progress.practice_completed += 1
        progress.last_activity = f"Completed practice: {exercise.title}"
        progress.last_activity_at = func.now()

    db.commit()
    db.refresh(attempt)
    db.refresh(xp)
    db.refresh(progress)
    return attempt, xp_awarded, xp, progress


def list_user_practice_attempts(db: Session, user_id: int):
    return list(
        db.scalars(
            select(PracticeAttempt)
            .where(PracticeAttempt.user_id == user_id)
            .order_by(PracticeAttempt.submitted_at.desc(), PracticeAttempt.id.desc())
        ).all()
    )
