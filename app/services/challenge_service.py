import re

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.challenge import Challenge, ChallengeAttempt
from app.models.progress import UserProgress
from app.services.progress_service import create_user_progress, get_user_progress
from app.services.xp_service import award_activity_xp, create_user_xp, get_user_xp
from app.services.achievement_service import evaluate_user_achievements


def normalize_answer(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip()).casefold()


def list_published_challenges(db: Session):
    return list(db.scalars(select(Challenge).where(Challenge.is_published.is_(True)).order_by(Challenge.display_order, Challenge.id)).all())


def get_published_challenge(db: Session, challenge_id: int):
    return db.scalar(select(Challenge).where(Challenge.id == challenge_id, Challenge.is_published.is_(True)))


def list_all_challenges(db: Session):
    return list(db.scalars(select(Challenge).order_by(Challenge.display_order, Challenge.id)).all())


def get_challenge_for_admin(db: Session, challenge_id: int):
    return db.get(Challenge, challenge_id)


def create_challenge(db: Session, data):
    challenge = Challenge(**data.model_dump())
    db.add(challenge)
    db.commit()
    db.refresh(challenge)
    return challenge


def replace_challenge(db: Session, challenge, data):
    for field, value in data.model_dump().items():
        setattr(challenge, field, value)
    db.commit()
    db.refresh(challenge)
    return challenge


def set_challenge_published(db: Session, challenge, published: bool):
    challenge.is_published = published
    db.commit()
    db.refresh(challenge)
    return challenge


def delete_challenge(db: Session, challenge):
    if db.scalar(select(ChallengeAttempt.id).where(ChallengeAttempt.challenge_id == challenge.id).limit(1)) is not None:
        raise ValueError("Challenge has submissions and cannot be deleted; unpublish it instead")
    db.delete(challenge)
    db.commit()


def submit_challenge_answer(db: Session, user_id: int, challenge_id: int, answer: str):
    challenge = get_published_challenge(db, challenge_id)
    if challenge is None:
        raise LookupError("Published challenge not found")

    normalized = normalize_answer(answer)
    correct = any(normalized == normalize_answer(expected) for expected in challenge.expected_answers)

    progress = get_user_progress(db, user_id)
    if progress is None:
        progress = create_user_progress(db, user_id)
    xp = get_user_xp(db, user_id)
    if xp is None:
        xp = create_user_xp(db, user_id)

    already_completed = db.scalar(select(ChallengeAttempt.id).where(
        ChallengeAttempt.user_id == user_id,
        ChallengeAttempt.challenge_id == challenge_id,
        ChallengeAttempt.is_correct.is_(True),
    ).limit(1)) is not None

    attempt = ChallengeAttempt(user_id=user_id, challenge_id=challenge_id, submitted_answer=answer.strip(), is_correct=correct)
    db.add(attempt)
    xp_awarded = 0
    if correct and not already_completed:
        event = award_activity_xp(db, user_id, "challenge", challenge_id)
        xp_awarded = event.xp_amount
        progress.challenges_completed += 1
        progress.last_activity = f"Completed challenge: {challenge.title}"
        progress.last_activity_at = func.now()

    newly_unlocked = evaluate_user_achievements(db, user_id)

    db.commit()
    db.refresh(attempt)
    db.refresh(xp)
    db.refresh(progress)
    return attempt, xp_awarded, xp, progress, newly_unlocked


def list_user_challenge_attempts(db: Session, user_id: int):
    return list(db.scalars(select(ChallengeAttempt).where(ChallengeAttempt.user_id == user_id).order_by(ChallengeAttempt.submitted_at.desc(), ChallengeAttempt.id.desc())).all())
