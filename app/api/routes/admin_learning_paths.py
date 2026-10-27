from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_admin
from app.models.user import User
from app.schemas.learning_path import (
    LearningPathAdminResponse,
    LearningPathWrite,
    LessonLinkWrite,
    TopicAdminResponse,
    TopicWrite,
)
from app.services.learning_path_service import (
    create_path,
    create_topic,
    delete_path,
    delete_topic,
    get_path,
    get_topic,
    link_lesson,
    list_all_paths,
    list_topics,
    unlink_lesson,
    update_path,
    update_topic,
)

router = APIRouter(
    prefix="/admin/learning-paths",
    tags=["Admin - Learning Paths"],
    dependencies=[Depends(require_admin)],
)


@router.get("", response_model=list[LearningPathAdminResponse])
def admin_list_paths(db: Session = Depends(get_db)):
    return list_all_paths(db)


@router.post(
    "", response_model=LearningPathAdminResponse, status_code=status.HTTP_201_CREATED
)
def admin_create_path(
    data: LearningPathWrite,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    return create_path(db, data)


@router.put("/{path_id}", response_model=LearningPathAdminResponse)
def admin_update_path(
    path_id: int,
    data: LearningPathWrite,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    obj = get_path(db, path_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Learning path not found")
    return update_path(db, obj, data)


@router.delete("/{path_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_path(
    path_id: int, db: Session = Depends(get_db), _admin: User = Depends(require_admin)
) -> Response:
    obj = get_path(db, path_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Learning path not found")
    delete_path(db, obj)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{path_id}/topics", response_model=list[TopicAdminResponse])
def admin_list_topics(
    path_id: int, db: Session = Depends(get_db), _admin: User = Depends(require_admin)
):
    if get_path(db, path_id) is None:
        raise HTTPException(status_code=404, detail="Learning path not found")
    return list_topics(db, path_id)


@router.post(
    "/{path_id}/topics",
    response_model=TopicAdminResponse,
    status_code=status.HTTP_201_CREATED,
)
def admin_create_topic(
    path_id: int,
    data: TopicWrite,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    if get_path(db, path_id) is None:
        raise HTTPException(status_code=404, detail="Learning path not found")
    return create_topic(db, path_id, data)


@router.put("/topics/{topic_id}", response_model=TopicAdminResponse)
def admin_update_topic(
    topic_id: int,
    data: TopicWrite,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    obj = get_topic(db, topic_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    return update_topic(db, obj, data)


@router.delete("/topics/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_topic(
    topic_id: int, db: Session = Depends(get_db), _admin: User = Depends(require_admin)
) -> Response:
    obj = get_topic(db, topic_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    delete_topic(db, obj)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/topics/{topic_id}/lessons", status_code=status.HTTP_200_OK)
def admin_link_lesson(
    topic_id: int,
    data: LessonLinkWrite,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    try:
        link_lesson(db, topic_id, data.lesson_id, data.display_order)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {
        "detail": "Lesson linked to topic",
        "topic_id": topic_id,
        "lesson_id": data.lesson_id,
    }


@router.delete(
    "/topics/{topic_id}/lessons/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT
)
def admin_unlink_lesson(
    topic_id: int,
    lesson_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> Response:
    if get_topic(db, topic_id) is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    if not unlink_lesson(db, topic_id, lesson_id):
        raise HTTPException(status_code=404, detail="Lesson link not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
