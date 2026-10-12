from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.lesson import Lesson


def list_published_lessons(db: Session) -> list[Lesson]:
    statement = (
        select(Lesson)
        .where(Lesson.is_published.is_(True))
        .order_by(Lesson.display_order.asc(), Lesson.id.asc())
    )
    return list(db.scalars(statement).all())


def get_published_lesson(db: Session, lesson_id: int) -> Lesson | None:
    statement = select(Lesson).where(
        Lesson.id == lesson_id,
        Lesson.is_published.is_(True),
    )
    return db.scalar(statement)
