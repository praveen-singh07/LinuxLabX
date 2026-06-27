from fastapi import FastAPI
from fastapi import Request

from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.api_router import router
from app.api.routes.auth import router as auth_router

from app.core.database import Base
from app.core.database import engine

from app.models.user import User

from app.api.routes.profile import (
    router as profile_router
)

from app.api.routes.challenges import (
    router as challenge_router
)



app = FastAPI(
    title="LinuxLabX",
    version="1.0.0"
)

Base.metadata.create_all(bind=engine)
app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(challenge_router)

app.include_router(router)

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static"
)

templates = Jinja2Templates(
    directory="app/templates"
)


@app.get(
    "/",
    response_class=HTMLResponse
)
async def home(
    request: Request
):

    return templates.TemplateResponse(
        "public/index.html",
        {
            "request": request
        }
    )



    # Temporary rountes adds
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(
        "dashboard/dashboard.html",
        {"request": request}
    )


@app.get("/profile", response_class=HTMLResponse)
async def profile(request: Request):
    return templates.TemplateResponse(
        "dashboard/profile.html",
        {"request": request}
    )


@app.get("/analytics", response_class=HTMLResponse)
async def analytics(request: Request):
    return templates.TemplateResponse(
        "dashboard/analytics.html",
        {"request": request}
    )


@app.get("/settings", response_class=HTMLResponse)
async def settings(request: Request):
    return templates.TemplateResponse(
        "dashboard/settings.html",
        {"request": request}
    )


@app.get("/terminal", response_class=HTMLResponse)
async def terminal(request: Request):
    return templates.TemplateResponse(
        "terminal/terminal.html",
        {"request": request}
    )


@app.get("/challenges", response_class=HTMLResponse)
async def challenges(request: Request):
    return templates.TemplateResponse(
        "challenges/challenges.html",
        {"request": request}
    )


@app.get("/challenge-details", response_class=HTMLResponse)
async def challenge_details(request: Request):
    return templates.TemplateResponse(
        "challenges/challenge_details.html",
        {"request": request}
    )


@app.get("/leaderboard", response_class=HTMLResponse)
async def leaderboard(request: Request):
    return templates.TemplateResponse(
        "challenges/leaderboard.html",
        {"request": request}
    )


@app.get("/achievements", response_class=HTMLResponse)
async def achievements(request: Request):
    return templates.TemplateResponse(
        "dashboard/achievements.html",
        {"request": request}
    )