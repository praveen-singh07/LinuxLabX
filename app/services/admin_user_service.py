from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.challenge import Challenge
from app.models.learning_path import LearningPath
from app.models.lesson import Lesson
from app.models.practice import PracticeExercise
from app.models.quiz import Quiz
from app.models.user import User
from app.schemas.admin_users import AdminOverview, AdminUserList


def list_users(
    db: Session,
    *,
    search: str | None,
    status_filter: str,
    role_filter: str,
    limit: int,
    offset: int,
) -> AdminUserList:
    query = select(User)
    count_query = select(func.count(User.id))

    if search:
        pattern = f"%{search.strip().lower()}%"
        criterion = func.lower(User.name).like(pattern) | func.lower(User.email).like(pattern)
        query = query.where(criterion)
        count_query = count_query.where(criterion)
    if status_filter == "active":
        query = query.where(User.is_active.is_(True))
        count_query = count_query.where(User.is_active.is_(True))
    elif status_filter == "suspended":
        query = query.where(User.is_active.is_(False))
        count_query = count_query.where(User.is_active.is_(False))
    if role_filter != "all":
        query = query.where(User.role == role_filter)
        count_query = count_query.where(User.role == role_filter)

    users = list(
        db.scalars(query.order_by(User.id).offset(offset).limit(limit)).all()
    )
    return AdminUserList(
        items=users,
        total=db.scalar(count_query) or 0,
        limit=limit,
        offset=offset,
    )


def count_active_admins(db: Session) -> int:
    return db.scalar(
        select(func.count(User.id)).where(
            User.role == "admin", User.is_active.is_(True)
        )
    ) or 0


def get_overview(db: Session) -> AdminOverview:
    def count(model, *criteria):
        statement = select(func.count()).select_from(model)
        if criteria:
            statement = statement.where(*criteria)
        return db.scalar(statement) or 0

    return AdminOverview(
        users_total=count(User),
        users_active=count(User, User.is_active.is_(True)),
        users_suspended=count(User, User.is_active.is_(False)),
        learning_paths=count(LearningPath),
        lessons=count(Lesson),
        quizzes=count(Quiz),
        practice_exercises=count(PracticeExercise),
        challenges=count(Challenge),
    )
