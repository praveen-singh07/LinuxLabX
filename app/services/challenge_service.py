from sqlalchemy.orm import Session

from app.models.challenge import Challenge
from app.schemas.challenge_schema import ChallengeCreate


def create_challenge(
    db: Session,
    challenge_data: ChallengeCreate
):

    challenge = Challenge(
        title=challenge_data.title,
        slug=challenge_data.slug,
        description=challenge_data.description,
        category=challenge_data.category,
        difficulty=challenge_data.difficulty,
        xp_reward=challenge_data.xp_reward,
        estimated_minutes=challenge_data.estimated_minutes,
        command_required=challenge_data.command_required
    )

    db.add(challenge)

    db.commit()

    db.refresh(challenge)

    return challenge


def get_all_challenges(
    db: Session
):

    return (
        db.query(Challenge)
        .filter(
            Challenge.is_active == True
        )
        .all()
    )


def get_challenge_by_slug(
    db: Session,
    slug: str
):

    return (
        db.query(Challenge)
        .filter(
            Challenge.slug == slug
        )
        .first()
    )