from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.lesson import Lesson
from app.schemas.lesson_admin import LessonCreate


def list_all_lessons(db: Session) -> list[Lesson]:
    statement = select(Lesson).order_by(Lesson.display_order.asc(), Lesson.id.asc())
    return list(db.scalars(statement).all())


def get_lesson_for_admin(db: Session, lesson_id: int) -> Lesson | None:
    return db.get(Lesson, lesson_id)


def create_lesson(db: Session, data: LessonCreate) -> Lesson:
    lesson = Lesson(**data.model_dump())
    db.add(lesson)
    db.commit()
    db.refresh(lesson)
    return lesson


def replace_lesson(db: Session, lesson: Lesson, data: LessonCreate) -> Lesson:
    for field, value in data.model_dump().items():
        setattr(lesson, field, value)
    db.commit()
    db.refresh(lesson)
    return lesson


def set_lesson_published(db: Session, lesson: Lesson, is_published: bool) -> Lesson:
    lesson.is_published = is_published
    db.commit()
    db.refresh(lesson)
    return lesson


def delete_lesson(db: Session, lesson: Lesson) -> None:
    db.delete(lesson)
    db.commit()
