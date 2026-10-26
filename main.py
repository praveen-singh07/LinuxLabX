from fastapi import FastAPI

from app.api.routes.admin_learning_paths import router as admin_learning_paths_router
from app.api.routes.admin_lessons import router as admin_lessons_router
from app.api.routes.auth import router as auth_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.learning_paths import router as learning_paths_router
from app.api.routes.lessons import router as lessons_router
from app.core.database import Base, engine
from app.models.learning_path import LearningPath  # noqa: F401
from app.models.topic import Topic, TopicLesson  # noqa: F401

app = FastAPI(
    title="LinuxLabX", description="Gamified Linux Learning Platform", version="1.0.0"
)


Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(lessons_router)
app.include_router(admin_lessons_router)
app.include_router(learning_paths_router)
app.include_router(admin_learning_paths_router)


@app.get("/")
def root():
    return {"message": "Welcome to LinuxLabX", "status": "running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
