from sqlalchemy import distinct, func, select
from sqlalchemy.orm import Session

from app.models.achievement import Achievement, UserAchievement
from app.models.challenge import ChallengeAttempt
from app.models.lesson_completion import LessonCompletion
from app.models.practice import PracticeAttempt
from app.models.quiz_attempt import QuizAttempt
from app.models.xp import UserXP


# SVG artwork lives in static/badges. Conditions use existing LinuxLabX activity data.
ACHIEVEMENT_CATALOG = (
    ("first_steps", "First Steps", "Your Linux learning journey begins.", "beginner", "Complete your first lesson.", "first_steps.svg", "lessons", 1),
    ("linux_explorer", "Linux Explorer", "Explore five lessons and build your foundation.", "beginner", "Complete 5 lessons.", "linux_explorer.svg", "lessons", 5),
    ("lesson_starter", "Lesson Starter", "Ten lessons completed, one strong habit formed.", "beginner", "Complete 10 lessons.", "lesson_starter.svg", "lessons", 10),
    ("command_learner", "Command Learner", "Your first command practice is correct.", "skill", "Correctly complete 1 practice exercise.", "command_learner.svg", "practice", 1),
    ("quiz_master", "Quiz Master", "Submit your first LinuxLabX quiz.", "skill", "Complete 1 quiz attempt.", "quiz_master.svg", "quizzes", 1),
    ("practice_pro", "Practice Pro", "Five different exercises solved correctly.", "skill", "Correctly complete 5 different practice exercises.", "practice_pro.svg", "practice", 5),
    ("challenge_solver", "Challenge Solver", "Solve your first Linux challenge.", "skill", "Correctly complete 1 challenge.", "challenge_solver.svg", "challenges", 1),
    ("xp_100", "100 XP Club", "Earn your first hundred experience points.", "milestone", "Reach 100 total XP.", "xp_100.svg", "xp", 100),
    ("xp_500", "500 XP Club", "Your learning is building real momentum.", "milestone", "Reach 500 total XP.", "xp_500.svg", "xp", 500),
    ("xp_1000", "1000 XP Club", "A thousand XP earned through learning.", "milestone", "Reach 1,000 total XP.", "xp_1000.svg", "xp", 1000),
    ("perfect_score", "Perfect Score", "A flawless result on a Linux quiz.", "special", "Score 100% on any quiz.", "perfect_score.svg", "perfect_quiz", 1),
    ("challenge_champion", "Challenge Champion", "Five different challenges solved correctly.", "special", "Correctly complete 5 different challenges.", "challenge_champion.svg", "challenges", 5),
)


def ensure_achievement_catalog(db: Session) -> list[Achievement]:
    """Insert missing catalog entries without replacing existing records."""
    existing = {item.code for item in db.scalars(select(Achievement)).all()}
    for order, row in enumerate(ACHIEVEMENT_CATALOG, start=1):
        code, title, description, category, criteria, filename, rule_type, threshold = row
        if code not in existing:
            db.add(
                Achievement(
                    code=code,
                    title=title,
                    description=description,
                    category=category,
                    criteria=criteria,
                    icon_path=f"/static/badges/{filename}",
                    rule_type=rule_type,
                    threshold=threshold,
                    display_order=order,
                )
            )
    db.flush()
    return list(db.scalars(select(Achievement).order_by(Achievement.display_order)).all())


def _count(db: Session, statement) -> int:
    return int(db.scalar(statement) or 0)


def _user_stats(db: Session, user_id: int) -> dict[str, int]:
    return {
        "lessons": _count(
            db,
            select(func.count(LessonCompletion.id)).where(
                LessonCompletion.user_id == user_id
            ),
        ),
        "practice": _count(
            db,
            select(func.count(distinct(PracticeAttempt.exercise_id))).where(
                PracticeAttempt.user_id == user_id,
                PracticeAttempt.is_correct.is_(True),
            ),
        ),
        "quizzes": _count(
            db, select(func.count(QuizAttempt.id)).where(QuizAttempt.user_id == user_id)
        ),
        "challenges": _count(
            db,
            select(func.count(distinct(ChallengeAttempt.challenge_id))).where(
                ChallengeAttempt.user_id == user_id,
                ChallengeAttempt.is_correct.is_(True),
            ),
        ),
        "xp": _count(db, select(UserXP.total_xp).where(UserXP.user_id == user_id)),
        "perfect_quiz": _count(
            db,
            select(func.count(QuizAttempt.id)).where(
                QuizAttempt.user_id == user_id, QuizAttempt.percentage == 100
            ),
        ),
    }


def _state(achievement: Achievement, record: UserAchievement | None) -> dict:
    return {
        "id": achievement.id,
        "code": achievement.code,
        "title": achievement.title,
        "description": achievement.description,
        "category": achievement.category,
        "criteria": achievement.criteria,
        "icon_path": achievement.icon_path,
        "unlocked": record is not None,
        "unlocked_at": record.unlocked_at if record else None,
    }


def get_user_achievement_collection(db: Session, user_id: int) -> list[dict]:
    catalog = ensure_achievement_catalog(db)
    # Catalog bootstrap is a small write; keep it available across requests.
    db.commit()
    records = db.scalars(
        select(UserAchievement).where(UserAchievement.user_id == user_id)
    ).all()
    by_id = {record.achievement_id: record for record in records}
    return [_state(item, by_id.get(item.id)) for item in catalog]


def evaluate_user_achievements(db: Session, user_id: int) -> list[dict]:
    """Unlock all newly met criteria inside the caller's activity transaction."""
    db.flush()
    catalog = ensure_achievement_catalog(db)
    records = db.scalars(
        select(UserAchievement).where(UserAchievement.user_id == user_id)
    ).all()
    unlocked_ids = {record.achievement_id for record in records}
    stats = _user_stats(db, user_id)
    newly_unlocked = []
    for achievement in catalog:
        if achievement.id in unlocked_ids:
            continue
        value = stats.get(achievement.rule_type, 0)
        if value < achievement.threshold:
            continue
        record = UserAchievement(user_id=user_id, achievement_id=achievement.id)
        db.add(record)
        db.flush()
        newly_unlocked.append(_state(achievement, record))
    return newly_unlocked
