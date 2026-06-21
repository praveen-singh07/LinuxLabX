from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(
    directory="app/templates"
)


@router.get(
    "/login",
    response_class=HTMLResponse
)
async def login_page(
    request: Request
):

    return templates.TemplateResponse(
        "auth/login.html",
        {
            "request": request
        }
    )


@router.get(
    "/register",
    response_class=HTMLResponse
)
async def register_page(
    request: Request
):

    return templates.TemplateResponse(
        "auth/register.html",
        {
            "request": request
        }
    )