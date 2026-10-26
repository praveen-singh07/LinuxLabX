from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.learning_path import LearningPath
from app.models.lesson import Lesson
from app.models.topic import Topic, TopicLesson
from app.schemas.learning_path import LearningPathWrite, TopicWrite


def list_published_paths(db: Session) -> list[LearningPath]:
    stmt = (
        select(LearningPath)
        .where(LearningPath.is_published.is_(True))
        .options(
            selectinload(LearningPath.topics)
            .selectinload(Topic.lesson_links)
            .selectinload(TopicLesson.lesson)
        )
        .order_by(LearningPath.display_order, LearningPath.id)
    )
    paths = list(db.scalars(stmt).all())
    # Do not mutate ORM relationship collections here: topics use delete-orphan cascade.
    # Public response serializers filter unpublished topics/lessons without changing DB state.
    return paths


def get_published_path(db: Session, path_id: int) -> LearningPath | None:
    stmt = (
        select(LearningPath)
        .where(LearningPath.id == path_id, LearningPath.is_published.is_(True))
        .options(
            selectinload(LearningPath.topics)
            .selectinload(Topic.lesson_links)
            .selectinload(TopicLesson.lesson)
        )
    )
    path = db.scalar(stmt)
    if path is None:
        return None
    # Do not mutate ORM relationship collections here: topics use delete-orphan cascade.
    # Public response serializers filter unpublished topics/lessons without changing DB state.
    return path


def list_all_paths(db: Session) -> list[LearningPath]:
    return list(
        db.scalars(
            select(LearningPath).order_by(LearningPath.display_order, LearningPath.id)
        ).all()
    )


def get_path(db: Session, path_id: int) -> LearningPath | None:
    return db.get(LearningPath, path_id)


def create_path(db: Session, data: LearningPathWrite) -> LearningPath:
    obj = LearningPath(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_path(
    db: Session, obj: LearningPath, data: LearningPathWrite
) -> LearningPath:
    for key, value in data.model_dump().items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete_path(db: Session, obj: LearningPath) -> None:
    db.delete(obj)
    db.commit()


def list_topics(db: Session, path_id: int) -> list[Topic]:
    stmt = (
        select(Topic)
        .where(Topic.learning_path_id == path_id)
        .order_by(Topic.display_order, Topic.id)
    )
    return list(db.scalars(stmt).all())


def get_topic(db: Session, topic_id: int) -> Topic | None:
    return db.get(Topic, topic_id)


def create_topic(db: Session, path_id: int, data: TopicWrite) -> Topic:
    obj = Topic(learning_path_id=path_id, **data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_topic(db: Session, obj: Topic, data: TopicWrite) -> Topic:
    for key, value in data.model_dump().items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete_topic(db: Session, obj: Topic) -> None:
    db.delete(obj)
    db.commit()


def link_lesson(
    db: Session, topic_id: int, lesson_id: int, display_order: int
) -> TopicLesson:
    if db.get(Topic, topic_id) is None:
        raise LookupError("Topic not found")
    if db.get(Lesson, lesson_id) is None:
        raise ValueError("Lesson not found")
    existing = db.scalar(
        select(TopicLesson).where(
            TopicLesson.topic_id == topic_id, TopicLesson.lesson_id == lesson_id
        )
    )
    if existing:
        existing.display_order = display_order
        db.commit()
        db.refresh(existing)
        return existing
    obj = TopicLesson(
        topic_id=topic_id, lesson_id=lesson_id, display_order=display_order
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def unlink_lesson(db: Session, topic_id: int, lesson_id: int) -> bool:
    obj = db.scalar(
        select(TopicLesson).where(
            TopicLesson.topic_id == topic_id, TopicLesson.lesson_id == lesson_id
        )
    )
    if obj is None:
        return False
    db.delete(obj)
    db.commit()
    return True
