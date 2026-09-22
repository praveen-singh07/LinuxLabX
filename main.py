from fastapi import FastAPI

from app.core.database import engine, Base
from app.models.user import User
from app.api.routes.auth import router as auth_router


app = FastAPI(
    title="LinuxLabX",
    description="Gamified Linux Learning Platform",
    version="1.0.0"
)


Base.metadata.create_all(bind=engine)

app.include_router(auth_router)


@app.get("/")
def root():
    return {
        "message": "Welcome to LinuxLabX",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }