from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from core.texts import get_texts, DEFAULT_LANG
from core.config import templates

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def home(request: Request, lang: str = DEFAULT_LANG):
    ui, lang = get_texts(lang)
    return templates.TemplateResponse("home.html", {"request": request, "ui": ui, "lang": lang})
