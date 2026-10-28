from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.lesson import Lesson
from app.models.lesson_completion import LessonCompletion
from app.models.progress import UserProgress
from app.models.xp import UserXP
from app.services.progress_service import create_user_progress, get_user_progress
from app.services.xp_service import award_activity_xp, get_user_xp


def list_user_completions(db: Session, user_id: int) -> list[LessonCompletion]:
    statement = (
        select(LessonCompletion)
        .join(Lesson, Lesson.id == LessonCompletion.lesson_id)
        .where(LessonCompletion.user_id == user_id)
        .order_by(LessonCompletion.completed_at.desc(), LessonCompletion.id.desc())
    )
    return list(db.scalars(statement).all())


def complete_published_lesson(
    db: Session, user_id: int, lesson_id: int
) -> tuple[LessonCompletion, bool, int, UserProgress, UserXP]:
    """Complete a published lesson idempotently and commit all changes together."""
    lesson = db.scalar(
        select(Lesson).where(
            Lesson.id == lesson_id,
            Lesson.is_published.is_(True),
        )
    )
    if lesson is None:
        raise LookupError("Published lesson not found")

    existing = db.scalar(
        select(LessonCompletion).where(
            LessonCompletion.user_id == user_id,
            LessonCompletion.lesson_id == lesson_id,
        )
    )
    already_completed = existing is not None

    progress = get_user_progress(db, user_id)
    if progress is None:
        progress = create_user_progress(db, user_id)

    xp = get_user_xp(db, user_id)
    if xp is None:
        from app.services.xp_service import create_user_xp
        xp = create_user_xp(db, user_id)

    xp_awarded = 0
    if not already_completed:
        completion = LessonCompletion(user_id=user_id, lesson_id=lesson_id)
        db.add(completion)
        progress.lessons_completed += 1
        event = award_activity_xp(db, user_id, "lesson", lesson_id)
        xp_awarded = event.xp_amount
        progress.last_activity = f"Completed lesson: {lesson.title}"
        progress.last_activity_at = func.now()

    # Percentage uses currently published lessons; no schema change to UserProgress.
    total_published = db.scalar(
        select(func.count(Lesson.id)).where(Lesson.is_published.is_(True))
    ) or 0
    completed_published = db.scalar(
        select(func.count(LessonCompletion.id))
        .join(Lesson, Lesson.id == LessonCompletion.lesson_id)
        .where(
            LessonCompletion.user_id == user_id,
            Lesson.is_published.is_(True),
        )
    ) or 0
    progress.progress_percentage = (
        min(100, round(completed_published * 100 / total_published))
        if total_published
        else 0
    )

    db.commit()
    db.refresh(progress)
    db.refresh(xp)
    if already_completed:
        completion = existing
    else:
        db.refresh(completion)
    return completion, already_completed, xp_awarded, progress, xp
