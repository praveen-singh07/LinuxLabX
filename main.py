from fastapi import FastAPI
from app.core.database import engine, Base


app = FastAPI(
    title="LinuxLabX",
    description="Gamified Linux Learning Platform",
    version="1.0.0"
)


Base.metadata.create_all(bind=engine)


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