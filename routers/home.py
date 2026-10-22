from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from core.texts import get_texts, DEFAULT_LANG
from core.config import templates

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # The home page is always shown in Catalan. Language selection happens
    # inside the "clinica" app, not on the landing page.
    ui, lang = get_texts("ca")
    return templates.TemplateResponse("home.html", {"request": request, "ui": ui, "lang": lang})
