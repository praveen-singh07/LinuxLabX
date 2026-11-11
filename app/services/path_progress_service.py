from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.lesson_completion import LessonCompletion
from app.schemas.path_progress import LearningPathProgress, TopicProgress
from app.services.learning_path_service import list_published_paths


def get_user_learning_path_progress(
    db: Session, user_id: int
) -> list[LearningPathProgress]:
    """Derive per-path progress from published content and existing completions."""
    completed_ids = set(db.scalars(
        select(LessonCompletion.lesson_id).where(LessonCompletion.user_id == user_id)
    ).all())
    results: list[LearningPathProgress] = []

    for path in list_published_paths(db):
        visible_topics = sorted(
            (topic for topic in path.topics if topic.is_published),
            key=lambda topic: (topic.display_order, topic.id),
        )
        ordered_lessons: list[tuple[object, object]] = []
        topic_results: list[TopicProgress] = []
        for topic in visible_topics:
            links = sorted(topic.lesson_links, key=lambda link: (link.display_order, link.id))
            lessons = [
                link.lesson for link in links
                if link.lesson is not None and link.lesson.is_published
            ]
            topic_ids = {lesson.id for lesson in lessons}
            topic_done = len(topic_ids & completed_ids)
            topic_results.append(TopicProgress(
                topic_id=topic.id,
                title=topic.title,
                total_lessons=len(topic_ids),
                completed_lessons=topic_done,
                progress_percent=round(topic_done * 100 / len(topic_ids)) if topic_ids else 0,
            ))
            ordered_lessons.extend((topic, lesson) for lesson in lessons)

        # A lesson linked more than once within a path counts once, in its first position.
        unique_lessons: list[tuple[object, object]] = []
        seen_ids: set[int] = set()
        for topic, lesson in ordered_lessons:
            if lesson.id not in seen_ids:
                unique_lessons.append((topic, lesson))
                seen_ids.add(lesson.id)

        done_count = len(seen_ids & completed_ids)
        next_item = next(
            ((topic, lesson) for topic, lesson in unique_lessons if lesson.id not in completed_ids),
            None,
        )
        results.append(LearningPathProgress(
            learning_path_id=path.id,
            title=path.title,
            total_lessons=len(unique_lessons),
            completed_lessons=done_count,
            progress_percent=round(done_count * 100 / len(unique_lessons)) if unique_lessons else 0,
            is_complete=bool(unique_lessons) and done_count == len(unique_lessons),
            next_lesson_id=next_item[1].id if next_item else None,
            next_lesson_title=next_item[1].title if next_item else None,
            next_topic_title=next_item[0].title if next_item else None,
            topics=topic_results,
        ))
    return results
