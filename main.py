from fastapi import FastAPI

app = FastAPI(
    title="LinuxLabX",
    description="Gamified Linux Learning Platform",
    version="1.0.0"
)


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