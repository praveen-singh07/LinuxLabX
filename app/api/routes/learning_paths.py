from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.learning_path import LearningPath
from app.schemas.learning_path import (
    LearningPathDetail,
    LearningPathSummary,
    LessonInTopic,
    TopicSummary,
)
from app.services.learning_path_service import get_published_path, list_published_paths

router = APIRouter(prefix="/learning-paths", tags=["Learning Paths"])


def _detail(path: LearningPath) -> LearningPathDetail:
    topics = []
    for topic in path.topics:
        if not topic.is_published:
            continue
        lessons = [
            LessonInTopic(
                id=link.lesson.id,
                title=link.lesson.title,
                description=link.lesson.description,
                command=link.lesson.command,
                difficulty=link.lesson.difficulty,
                display_order=link.display_order,
            )
            for link in sorted(
                topic.lesson_links, key=lambda x: (x.display_order, x.id)
            )
            if link.lesson is not None and link.lesson.is_published
        ]
        topics.append(
            TopicSummary(
                id=topic.id,
                learning_path_id=topic.learning_path_id,
                title=topic.title,
                description=topic.description,
                display_order=topic.display_order,
                is_published=topic.is_published,
                lessons=lessons,
            )
        )
    return LearningPathDetail(
        id=path.id,
        title=path.title,
        description=path.description,
        display_order=path.display_order,
        topics_count=len(topics),
        topics=topics,
    )


@router.get("", response_model=list[LearningPathSummary])
def list_learning_paths(db: Session = Depends(get_db)):
    return [
        LearningPathSummary(
            id=p.id,
            title=p.title,
            description=p.description,
            display_order=p.display_order,
            topics_count=sum(t.is_published for t in p.topics),
        )
        for p in list_published_paths(db)
    ]


@router.get("/{path_id}", response_model=LearningPathDetail)
def learning_path_detail(path_id: int, db: Session = Depends(get_db)):
    path = get_published_path(db, path_id)
    if path is None:
        raise HTTPException(status_code=404, detail="Learning path not found")
    return _detail(path)
