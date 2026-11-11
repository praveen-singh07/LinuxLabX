from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.challenge import Challenge, ChallengeAttempt
from app.models.lesson import Lesson
from app.models.lesson_completion import LessonCompletion
from app.models.practice import PracticeAttempt, PracticeExercise
from app.models.quiz import Quiz
from app.models.quiz_attempt import QuizAttempt
from app.schemas.activity import ActivityFeedItem, ActivityFeedResponse
from app.services.quiz_service import PASS_PERCENTAGE


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def get_activity_feed(
    db: Session, user_id: int, limit: int = 12, offset: int = 0
) -> ActivityFeedResponse:
    items: list[ActivityFeedItem] = []
    fetch_limit = offset + limit + 1

    lesson_rows = db.execute(
        select(LessonCompletion, Lesson.title)
        .join(Lesson, Lesson.id == LessonCompletion.lesson_id)
        .where(LessonCompletion.user_id == user_id)
        .order_by(LessonCompletion.completed_at.desc(), LessonCompletion.id.desc())
        .limit(fetch_limit)
    ).all()
    for completion, title in lesson_rows:
        items.append(
            ActivityFeedItem(
                activity_id=completion.lesson_id,
                activity_type="lesson",
                title=title,
                status="Completed",
                detail="Lesson finished",
                happened_at=_as_utc(completion.completed_at),
            )
        )

    quiz_rows = db.execute(
        select(QuizAttempt, Quiz.title)
        .join(Quiz, Quiz.id == QuizAttempt.quiz_id)
        .where(QuizAttempt.user_id == user_id)
        .order_by(QuizAttempt.submitted_at.desc(), QuizAttempt.id.desc())
        .limit(fetch_limit)
    ).all()
    for attempt, title in quiz_rows:
        items.append(
            ActivityFeedItem(
                activity_id=attempt.quiz_id,
                activity_type="quiz",
                title=title,
                status="Passed" if attempt.percentage >= PASS_PERCENTAGE else "Keep practicing",
                detail=f"{attempt.score}/{attempt.total_questions} correct · {attempt.percentage}%",
                happened_at=_as_utc(attempt.submitted_at),
            )
        )

    practice_rows = db.execute(
        select(PracticeAttempt, PracticeExercise.title)
        .join(PracticeExercise, PracticeExercise.id == PracticeAttempt.exercise_id)
        .where(PracticeAttempt.user_id == user_id)
        .order_by(PracticeAttempt.submitted_at.desc(), PracticeAttempt.id.desc())
        .limit(fetch_limit)
    ).all()
    for attempt, title in practice_rows:
        items.append(
            ActivityFeedItem(
                activity_id=attempt.exercise_id,
                activity_type="practice",
                title=title,
                status="Correct" if attempt.is_correct else "Retry",
                detail="Practice answer accepted" if attempt.is_correct else "Review the hint and try again",
                happened_at=_as_utc(attempt.submitted_at),
            )
        )

    challenge_rows = db.execute(
        select(ChallengeAttempt, Challenge.title)
        .join(Challenge, Challenge.id == ChallengeAttempt.challenge_id)
        .where(ChallengeAttempt.user_id == user_id)
        .order_by(ChallengeAttempt.submitted_at.desc(), ChallengeAttempt.id.desc())
        .limit(fetch_limit)
    ).all()
    for attempt, title in challenge_rows:
        items.append(
            ActivityFeedItem(
                activity_id=attempt.challenge_id,
                activity_type="challenge",
                title=title,
                status="Solved" if attempt.is_correct else "Retry",
                detail="Challenge completed" if attempt.is_correct else "Keep working on this scenario",
                happened_at=_as_utc(attempt.submitted_at),
            )
        )

    items.sort(
        key=lambda item: (item.happened_at, item.activity_type, item.activity_id),
        reverse=True,
    )
    page = items[offset : offset + limit]
    has_more = len(items) > offset + limit
    return ActivityFeedResponse(
        items=page,
        has_more=has_more,
        next_offset=offset + len(page) if has_more else None,
    )
