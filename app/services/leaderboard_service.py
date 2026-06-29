from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.user import User
from app.models.progress import Progress


def get_leaderboard(
    db: Session
):

    users = (
        db.query(User)
        .order_by(
            User.xp.desc(),
            User.level.desc()
        )
        .all()
    )

    leaderboard = []

    for index, user in enumerate(users, start=1):

        completed_challenges = (
            db.query(
                func.count(
                    Progress.id
                )
            )
            .filter(
                Progress.user_id == user.id,
                Progress.completed == True
            )
            .scalar()
        )

        leaderboard.append(
            {
                "rank": index,
                "username": user.username,
                "xp": user.xp,
                "level": user.level,
                "completed_challenges": completed_challenges
            }
        )

    return leaderboard