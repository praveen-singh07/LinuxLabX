from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes.achievements import router as achievements_router
from app.api.routes.admin_challenges import router as admin_challenges_router
from app.api.routes.admin_learning_paths import router as admin_learning_paths_router
from app.api.routes.admin_lessons import router as admin_lessons_router
from app.api.routes.admin_practice import router as admin_practice_router
from app.api.routes.admin_quizzes import router as admin_quizzes_router
from app.api.routes.admin_users import router as admin_users_router
from app.api.routes.auth import router as auth_router
from app.api.routes.challenges import router as challenges_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.gamification import router as gamification_router
from app.api.routes.learning_paths import router as learning_paths_router
from app.api.routes.lesson_completion import router as lesson_completion_router
from app.api.routes.lessons import router as lessons_router
from app.api.routes.practice import router as practice_router
from app.api.routes.quizzes import router as quizzes_router
from app.core.database import Base, engine
from app.models.challenge import Challenge, ChallengeAttempt  # noqa: F401
from app.models.achievement import Achievement, UserAchievement  # noqa: F401
from app.models.learning_path import LearningPath  # noqa: F401
from app.models.lesson_completion import LessonCompletion  # noqa: F401
from app.models.practice import PracticeAttempt, PracticeExercise  # noqa: F401
from app.models.quiz import Quiz, QuizQuestion  # noqa: F401
from app.models.quiz_attempt import QuizAttempt  # noqa: F401
from app.models.topic import Topic, TopicLesson  # noqa: F401

app = FastAPI(
    title="LinuxLabX", description="Gamified Linux Learning Platform", version="1.0.0"
)

APP_DIR = Path(__file__).resolve().parent / "app"
STATIC_DIR = APP_DIR / "static"
TEMPLATE_DIR = APP_DIR / "templates"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(achievements_router)
app.include_router(dashboard_router)
app.include_router(gamification_router)
app.include_router(lessons_router)
app.include_router(admin_lessons_router)
app.include_router(learning_paths_router)
app.include_router(admin_learning_paths_router)
app.include_router(lesson_completion_router)
app.include_router(quizzes_router)
app.include_router(admin_quizzes_router)
app.include_router(admin_users_router)
app.include_router(practice_router)
app.include_router(admin_practice_router)
app.include_router(challenges_router)
app.include_router(admin_challenges_router)


@app.get("/")
def root():
    return {"message": "Welcome to LinuxLabX", "status": "running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/app/achievements", include_in_schema=False)
def achievements_page():
    return FileResponse(TEMPLATE_DIR / "dashboard.html")


@app.get("/app/dashboard", include_in_schema=False)
def student_dashboard_page():
    return FileResponse(TEMPLATE_DIR / "dashboard.html")


@app.get("/app/admin", include_in_schema=False)
def admin_content_page():
    return FileResponse(TEMPLATE_DIR / "admin.html")
