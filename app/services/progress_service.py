
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.progress import UserProgress


def get_user_progress(
    db: Session,
    user_id: int,
) -> UserProgress | None:
    return db.scalar(
        select(UserProgress).where(
            UserProgress.user_id == user_id
        )
    )


def create_user_progress(
    db: Session,
    user_id: int,
) -> UserProgress:
    progress = UserProgress(
        user_id=user_id,
        lessons_completed=0,
        practice_completed=0,
        quizzes_completed=0,
        challenges_completed=0,
        progress_percentage=0,
        last_activity=None,
        last_activity_at=None,
    )

    db.add(progress)
    db.flush()

    return progress
