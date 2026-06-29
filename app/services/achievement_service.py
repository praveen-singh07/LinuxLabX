from sqlalchemy.orm import Session

from app.models.achievement import Achievement
from app.models.progress import Progress
from app.models.user import User


def check_achievements(
    db: Session,
    user: User
):

    completed_count = (
        db.query(Progress)
        .filter(
            Progress.user_id == user.id,
            Progress.completed == True
        )
        .count()
    )

    existing_titles = [
        achievement.title
        for achievement in (
            db.query(Achievement)
            .filter(
                Achievement.user_id == user.id
            )
            .all()
        )
    ]

    achievements_to_add = []

    if (
        completed_count >= 1 and
        "First Command" not in existing_titles
    ):
        achievements_to_add.append(
            {
                "title": "First Command",
                "description": "Completed first challenge",
                "badge_icon": "🏆"
            }
        )

    if (
        completed_count >= 5 and
        "Linux Explorer" not in existing_titles
    ):
        achievements_to_add.append(
            {
                "title": "Linux Explorer",
                "description": "Completed 5 challenges",
                "badge_icon": "🚀"
            }
        )

    if (
        user.xp >= 500 and
        "XP Hunter" not in existing_titles
    ):
        achievements_to_add.append(
            {
                "title": "XP Hunter",
                "description": "Reached 500 XP",
                "badge_icon": "⚡"
            }
        )

    for achievement_data in achievements_to_add:

        achievement = Achievement(
            user_id=user.id,
            title=achievement_data["title"],
            description=achievement_data["description"],
            badge_icon=achievement_data["badge_icon"]
        )

        db.add(achievement)

    db.commit()