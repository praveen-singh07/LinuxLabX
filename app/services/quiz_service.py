from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.progress import UserProgress
from app.models.quiz import Quiz, QuizQuestion
from app.models.quiz_attempt import QuizAttempt
from app.models.xp_event import XPEvent
from app.services.xp_service import award_activity_xp, get_user_xp

PASS_PERCENTAGE = 60


def list_published_quizzes(db: Session) -> list[Quiz]:
    quizzes = db.scalars(
        select(Quiz)
        .where(Quiz.is_published.is_(True))
        .options(selectinload(Quiz.questions))
        .order_by(Quiz.id)
    ).all()
    return list(quizzes)


def get_published_quiz(db: Session, quiz_id: int) -> Quiz | None:
    return db.scalar(
        select(Quiz)
        .where(Quiz.id == quiz_id, Quiz.is_published.is_(True))
        .options(selectinload(Quiz.questions))
    )


def get_quiz_for_admin(db: Session, quiz_id: int) -> Quiz | None:
    return db.scalar(
        select(Quiz).where(Quiz.id == quiz_id).options(selectinload(Quiz.questions))
    )


def list_all_quizzes(db: Session) -> list[Quiz]:
    return list(
        db.scalars(
            select(Quiz).options(selectinload(Quiz.questions)).order_by(Quiz.id)
        ).all()
    )


def create_quiz(db: Session, data) -> Quiz:
    quiz = Quiz(
        title=data.title,
        description=data.description,
        difficulty=data.difficulty,
        is_published=data.is_published,
        questions=[
            QuizQuestion(
                prompt=q.prompt,
                options=q.options,
                correct_option_index=q.correct_option_index,
                explanation=q.explanation,
                display_order=q.display_order,
            )
            for q in data.questions
        ],
    )
    db.add(quiz)
    db.commit()
    result = get_quiz_for_admin(db, quiz.id)
    if result is None:
        raise RuntimeError("Created quiz could not be retrieved")
    return result


def replace_quiz(db: Session, quiz: Quiz, data) -> Quiz:
    quiz.title = data.title
    quiz.description = data.description
    quiz.difficulty = data.difficulty
    quiz.is_published = data.is_published
    quiz.questions.clear()
    quiz.questions.extend(
        QuizQuestion(
            prompt=q.prompt,
            options=q.options,
            correct_option_index=q.correct_option_index,
            explanation=q.explanation,
            display_order=q.display_order,
        )
        for q in data.questions
    )
    db.commit()
    result = get_quiz_for_admin(db, quiz.id)
    if result is None:
        raise RuntimeError("Created quiz could not be retrieved")
    return result


def set_quiz_published(db: Session, quiz: Quiz, published: bool) -> Quiz:
    quiz.is_published = published
    db.commit()
    result = get_quiz_for_admin(db, quiz.id)
    if result is None:
        raise RuntimeError("Created quiz could not be retrieved")
    return result


def delete_quiz(db: Session, quiz: Quiz) -> None:
    db.delete(quiz)
    db.commit()


def submit_quiz(db: Session, user_id: int, quiz_id: int, submitted_answers):
    quiz = get_published_quiz(db, quiz_id)
    if quiz is None:
        raise LookupError("Published quiz not found")
    if not quiz.questions:
        raise ValueError("This quiz has no questions")

    questions_by_id = {question.id: question for question in quiz.questions}
    answer_map = {}
    for answer in submitted_answers:
        if answer.question_id in answer_map:
            raise ValueError("Duplicate answer for a question")
        question = questions_by_id.get(answer.question_id)
        if question is None:
            raise ValueError("An answer refers to a question outside this quiz")
        if answer.selected_option_index >= len(question.options):
            raise ValueError("Selected option does not exist")
        answer_map[answer.question_id] = answer.selected_option_index

    if len(answer_map) != len(questions_by_id):
        raise ValueError("Submit exactly one answer for every quiz question")

    score = sum(
        1
        for question_id, selected in answer_map.items()
        if questions_by_id[question_id].correct_option_index == selected
    )
    total_questions = len(questions_by_id)
    percentage = round(score * 100 / total_questions)
    passed = percentage >= PASS_PERCENTAGE

    attempt = QuizAttempt(
        user_id=user_id,
        quiz_id=quiz.id,
        score=score,
        total_questions=total_questions,
        percentage=percentage,
        answers=[
            {"question_id": question_id, "selected_option_index": selected}
            for question_id, selected in sorted(answer_map.items())
        ],
    )
    db.add(attempt)

    existing_event = db.scalar(
        select(XPEvent).where(
            XPEvent.user_id == user_id,
            XPEvent.activity_type == "quiz",
            XPEvent.activity_id == quiz.id,
            XPEvent.event_type == "completion",
        )
    )

    xp_awarded = 0
    if existing_event is None:
        event = award_activity_xp(db, user_id, "quiz", quiz.id)
        # XP is awarded once on first submission, even if the score is below pass threshold.
        xp_awarded = event.xp_amount if event.xp_amount else 0

        progress = db.scalar(
            select(UserProgress).where(UserProgress.user_id == user_id)
        )
        if progress is None:
            progress = UserProgress(user_id=user_id)
            db.add(progress)
            db.flush()
        progress.quizzes_completed += 1
        progress.last_activity = f"Quiz completed: {quiz.title}"
        progress.last_activity_at = func.now()

    user_xp = get_user_xp(db, user_id)
    if user_xp is None:
        # award_activity_xp normally creates this row, but handle legacy accounts safely.
        from app.services.xp_service import create_user_xp

        user_xp = create_user_xp(db, user_id)

    db.commit()
    db.refresh(attempt)
    db.refresh(user_xp)
    progress = db.scalar(select(UserProgress).where(UserProgress.user_id == user_id))
    return attempt, passed, xp_awarded, user_xp, progress


def list_user_attempts(db: Session, user_id: int) -> list[QuizAttempt]:
    return list(
        db.scalars(
            select(QuizAttempt)
            .where(QuizAttempt.user_id == user_id)
            .order_by(QuizAttempt.submitted_at.desc(), QuizAttempt.id.desc())
        ).all()
    )
