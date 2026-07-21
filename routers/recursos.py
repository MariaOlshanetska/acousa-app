from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from core.texts import get_texts, DEFAULT_LANG
from core.config import templates

router = APIRouter()

RESOURCES = [
    {
        "title": {"es": "Apps", "ca": "Apps", "en": "Apps"},
        "items": [
            {
            "label":"Rhythm analysis",
            "url":"https://parlab.ub.edu/rhythm_analysis/",
            "open_new_tab": True,
            "icon": "icons/rhythm.svg",
            "desc": {"es":"Métricas de ritmo desde TextGrids.", "ca":"Mètriques de ritme des de TextGrids.", "en":"Rhythm metrics from TextGrids."}
            },
            {
            "label":"Plot vowels",
            "url":"https://parlab.ub.edu/plot_vowels/",
            "open_new_tab": True,
            "icon": "icons/vowel.svg",
            "desc": {"es":"Formantes y visualización de vocales.", "ca":"Formants i visualització de vocals.", "en":"Formants & vowel visualization."}
            },
            {
            "label": "Corrector de TextGrids",
            "url": "/textgrid_corrector/",
            "open_new_tab": True,
            "icon": "icons/textgrid.svg",
            "desc": {
                "es": "Compara archivos TextGrid con un modelo y evalúa la transcripción y la segmentación.",
                "ca": "Compara fitxers TextGrid amb un model i avalua la transcripció i la segmentació.",
                "en": "Compares TextGrid files with a reference model and evaluates transcription and segmentation.",
                },
            },
        ],
    },
    {
        "title": {"es": "Enlaces", "ca": "Enllaços", "en": "Links"},
        "items": [
            {
                "label": "Gràdia – Evolució del llatí a l'espanyol",
                "url": "https://www.ub.edu/gradia/index.php",
                "icon": "icons/evolution.svg",
                "desc": {
                    "es": "Evolución del llatín al español",
                    "ca": "Evolució del llatí a l'espanyol",
                    "en": "Latin to Spanish evolution."
                }
            },
            {
                "label": "TRaFo – Traductor fonològic multidialectal de l'espanyol",
                "url": "https://stel2.ub.edu/trafo/",
                "icon": "icons/dialecte.svg",
                "desc": {
                    "es": "Traductor fonológico multidialectal del español.",
                    "ca": "Traductor fonològic multidialectal de l'espanyol.",
                    "en": "Multidialectal phonological translator for Spanish."
                }
            },
        ],
    },
]

@router.get("/recursos", response_class=HTMLResponse)
async def recursos(request: Request, lang: str = DEFAULT_LANG):
    ui, lang = get_texts(lang)

    sections = []
    for s in RESOURCES:
        items = []
        for it in s["items"]:
            is_soon = (it.get("url") == "pronto")

            raw_icon = (it.get("icon", "") or "").lstrip("/")  # quita "/" inicial
            if raw_icon.startswith("static/"):
                raw_icon = raw_icon[len("static/"):]           # quita "static/"
            icon = raw_icon

            items.append({
                "label": it.get("label", ""),
                "url": None if is_soon else it.get("url"),
                "open_new_tab": (False if is_soon else bool(it.get("open_new_tab", True))),
                "desc": (it.get("desc") or {}).get(lang, ""),
                "icon": icon,   # ✅ usa el icon normalizado
            })
        sections.append({"title": s["title"][lang], "items": items})

    return templates.TemplateResponse(
        "resources.html",
        {"request": request, "ui": ui, "lang": lang, "sections": sections},
    )