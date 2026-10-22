from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse

from core.config import templates
from core.texts import DEFAULT_LANG, get_texts

router = APIRouter()

RESOURCES = [
    {
        "title": {"es": "Apps", "ca": "Apps", "en": "Apps"},
        "items": [
            {
            "label": {"es": "Análisis del ritmo", "ca": "Anàlisi del ritme", "en": "Rhythm analysis"},
            "url":"https://parlab.ub.edu/rhythm_analysis/",
            "open_new_tab": True,
            "icon": "icons/rhythm.svg",
            "desc": {"es":"Métricas de ritmo desde TextGrids.", "ca":"Mètriques de ritme des de TextGrids.", "en":"Rhythm metrics from TextGrids."}
            },
            {
            "label": {"es": "Gráfico de vocales", "ca": "Gràfic de vocals", "en": "Plot vowels"},
            "url":"https://parlab.ub.edu/plot_vowels/",
            "open_new_tab": True,
            "icon": "icons/vowel.svg",
            "desc": {"es":"Formantes y visualización de vocales.", "ca":"Formants i visualització de vocals.", "en":"Formants & vowel visualization."}
            },
            {
            "label": {"es": "Corrector de TextGrids", "ca": "Corrector de TextGrids", "en": "TextGrid corrector"},
            "url": "https://parlab.ub.edu/textgrid_corrector/",
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

COMPARE_TEXT = {
    "ca": {
        "title": "Comparativa d'anàlisis",
        "intro": "Puja entre 2 i 5 CSV generats per la mateixa tasca per veure l'evolució de les mesures.",
        "submit": "Generar comparativa",
        "back": "Tornar als recursos",
        "open": "Obrir la comparativa",
        "card_title": "Comparar resultats CSV",
        "card_desc": "Compara fins a cinc anàlisis de la mateixa tasca i visualitza els canvis en el temps.",
        "plot_title": "Evolució temporal",
        "file": "Fitxer",
        "error_count": "Selecciona entre 2 i 5 fitxers CSV.",
        "error_csv": "No s'ha pogut llegir un dels CSV.",
        "error_empty": "Un dels CSV no conté mesures numèriques comparables.",
        "error_mixed": "Els CSV no contenen les mateixes mesures. Puja fitxers generats per la mateixa tasca; sembla que hi ha tasques barrejades.",
        "error_task": "Els CSV indiquen tasques diferents. Puja fitxers de la mateixa tasca.",
        "upload_label": "Ordre temporal dels fitxers",
        "upload_help": "Puja els fitxers en ordre cronològic. El fitxer 1 és el més antic i l'últim fitxer seleccionat és el més recent. Els fitxers 1 i 2 són obligatoris.",
        "file_1": "Fitxer 1 · més antic",
        "file_2": "Fitxer 2",
        "file_3": "Fitxer 3 · opcional",
        "file_4": "Fitxer 4 · opcional",
        "file_5": "Fitxer 5 · opcional",
        "files_title": "Ordre temporal",
        "error_gap": "Puja els fitxers en ordre i no deixis cap finestra buida entre dos fitxers.",
    },
    "es": {
        "title": "Comparativa de análisis",
        "intro": "Sube entre 2 y 5 CSV generados por la misma tarea para ver la evolución de las medidas.",
        "submit": "Generar comparativa",
        "back": "Volver a recursos",
        "open": "Abrir la comparativa",
        "card_title": "Comparar resultados CSV",
        "card_desc": "Compara hasta cinco análisis de la misma tarea y visualiza los cambios en el tiempo.",
        "plot_title": "Evolución temporal",
        "file": "Archivo",
        "error_count": "Selecciona entre 2 y 5 archivos CSV.",
        "error_csv": "No se ha podido leer uno de los CSV.",
        "error_empty": "Uno de los CSV no contiene medidas numéricas comparables.",
        "error_mixed": "Los CSV no contienen las mismas medidas. Sube archivos generados por la misma tarea; parece que hay tareas mezcladas.",
        "error_task": "Los CSV indican tareas diferentes. Sube archivos de la misma tarea.",
        "upload_label": "Orden temporal de los archivos",
        "upload_help": "Sube los archivos en orden cronológico. El archivo 1 es el más antiguo y el último archivo seleccionado es el más reciente. Los archivos 1 y 2 son obligatorios.",
        "file_1": "Archivo 1 · más antiguo",
        "file_2": "Archivo 2",
        "file_3": "Archivo 3 · opcional",
        "file_4": "Archivo 4 · opcional",
        "file_5": "Archivo 5 · opcional",
        "files_title": "Orden temporal",
        "error_gap": "Sube los archivos en orden y no dejes ninguna ventana vacía entre dos archivos.",
    },
    "en": {
        "title": "Analysis comparison",
        "intro": "Upload between 2 and 5 CSV files generated by the same task to view how the measures change over time.",
        "submit": "Generate comparison",
        "back": "Back to resources",
        "open": "Open comparison",
        "card_title": "Compare CSV results",
        "card_desc": "Compare up to five analyses from the same task and visualise changes over time.",
        "plot_title": "Change over time",
        "file": "File",
        "error_count": "Select between 2 and 5 CSV files.",
        "error_csv": "One of the CSV files could not be read.",
        "error_empty": "One of the CSV files does not contain comparable numeric measures.",
        "error_mixed": "The CSV files do not contain the same measures. Upload files generated by the same task; different tasks appear to be mixed.",
        "error_task": "The CSV files identify different tasks. Upload files from the same task.",
        "upload_label": "Temporal file order",
        "upload_help": "Upload the files in chronological order. File 1 is the oldest and the last selected file is the most recent. Files 1 and 2 are required.",
        "file_1": "File 1 · oldest",
        "file_2": "File 2",
        "file_3": "File 3 · optional",
        "file_4": "File 4 · optional",
        "file_5": "File 5 · optional",
        "files_title": "Temporal order",
        "error_gap": "Upload the files in order without leaving an empty slot between two files.",
    },
}

# Columns that may appear in the CSV but are not acoustic measures.
METADATA_COLUMNS = {
    "task", "tarea", "tasca",
    "analysis_datetime", "analysis_date", "datetime", "timestamp", "date", "fecha", "data",
    "filename", "file", "archivo", "fitxer",
    "age", "edad", "edat", "gender", "genero", "gènere", "sex",
    "subject", "participant", "participant_id", "session", "session_id",
}


TASK_COLUMNS = ("task", "tarea", "tasca")
MEASURE_COLUMNS = ("measure", "metric", "variable", "medida", "mesura")
VALUE_COLUMNS = ("value", "valor")


def _normalise_name(value: str | None) -> str:
    return (value or "").strip().lower()


def _parse_number(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip().replace("\u00a0", "")
    if not text or text.lower() in {"na", "nan", "null", "none", "-"}:
        return None

    # Accepts both 12.34 and 12,34. Thousands separators are not expected here.
    if "," in text and "." not in text:
        text = text.replace(",", ".")

    try:
        return float(text)
    except ValueError:
        return None


def _decode_csv(raw: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError("encoding")


def _read_rows(raw: bytes) -> tuple[list[str], list[dict[str, str]]]:
    text = _decode_csv(raw)
    sample = text[:8192]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
    except csv.Error:
        dialect = csv.excel

    reader = csv.DictReader(io.StringIO(text), dialect=dialect)
    if not reader.fieldnames:
        raise ValueError("headers")

    fieldnames = [(name or "").strip() for name in reader.fieldnames]
    rows: list[dict[str, str]] = []
    for raw_row in reader:
        clean_row = {
            (key or "").strip(): (value or "").strip()
            for key, value in raw_row.items()
            if key is not None
        }
        if any(value != "" for value in clean_row.values()):
            rows.append(clean_row)

    if not rows:
        raise ValueError("rows")
    return fieldnames, rows


def _find_actual_column(fieldnames: list[str], candidates: tuple[str, ...]) -> str | None:
    lookup = {_normalise_name(name): name for name in fieldnames}
    for candidate in candidates:
        if candidate in lookup:
            return lookup[candidate]
    return None


def _extract_task(fieldnames: list[str], rows: list[dict[str, str]]) -> str | None:
    task_col = _find_actual_column(fieldnames, TASK_COLUMNS)
    if not task_col:
        return None
    for row in rows:
        value = row.get(task_col, "").strip()
        if value:
            return value.lower()
    return None

    date_col = _find_actual_column(fieldnames, DATE_COLUMNS)
    if not date_col:
        return None
    for row in rows:
        value = row.get(date_col, "").strip()
        if value:
            return value
    return None


def _extract_measures(fieldnames: list[str], rows: list[dict[str, str]]) -> dict[str, float]:
    """Supports both wide CSV (one row, one column per measure) and long (measure/value)."""
    measure_col = _find_actual_column(fieldnames, MEASURE_COLUMNS)
    value_col = _find_actual_column(fieldnames, VALUE_COLUMNS)

    if measure_col and value_col:
        measures: dict[str, float] = {}
        for row in rows:
            name = row.get(measure_col, "").strip()
            number = _parse_number(row.get(value_col))
            if name and number is not None:
                measures[name] = number
        return measures

    # Current AcousA format: a single row where each measure is a column.
    first_row = rows[0]
    measures = {}
    for column in fieldnames:
        if _normalise_name(column) in METADATA_COLUMNS:
            continue
        number = _parse_number(first_row.get(column))
        if number is not None:
            measures[column] = number
    return measures


def _comparison_context(request: Request, lang: str, **extra: Any) -> dict[str, Any]:
    ui, lang = get_texts(lang)
    context = {
        "request": request,
        "ui": ui,
        "lang": lang,
        "cmp": COMPARE_TEXT[lang],
        "error_message": None,
        "plot_data_json": None,
        "analyses": [],
    }
    context.update(extra)
    return context


@router.get("/recursos", response_class=HTMLResponse)
async def recursos(request: Request, lang: str = DEFAULT_LANG):
    ui, lang = get_texts(lang)

    sections = []
    for s in RESOURCES:
        items = []
        for it in s["items"]:
            is_soon = (it.get("url") == "pronto")

            raw_icon = (it.get("icon", "") or "").lstrip("/")  # strip leading "/"
            if raw_icon.startswith("static/"):
                raw_icon = raw_icon[len("static/"):]           # strip "static/"
            icon = raw_icon

            raw_label = it.get("label", "")
            label = raw_label.get(lang, raw_label.get("en", "")) if isinstance(raw_label, dict) else raw_label

            items.append({
                "label": label,
                "url": None if is_soon else it.get("url"),
                "open_new_tab": (False if is_soon else bool(it.get("open_new_tab", True))),
                "desc": (it.get("desc") or {}).get(lang, ""),
                "icon": icon,   # ✅ use the normalized icon
            })
        sections.append({"title": s["title"][lang], "items": items})

    return templates.TemplateResponse(
        "resources.html",
        {"request": request, "ui": ui, "lang": lang, "sections": sections},
    )


@router.get("/recursos/comparativa", response_class=HTMLResponse)
async def comparativa_form(request: Request, lang: str = DEFAULT_LANG):
    return templates.TemplateResponse(
        "comparison.html",
        _comparison_context(request, lang),
    )


@router.post("/recursos/comparativa", response_class=HTMLResponse)
async def comparativa_csv(
    request: Request,
    file_1: UploadFile = File(...),
    file_2: UploadFile = File(...),
    file_3: UploadFile | None = File(None),
    file_4: UploadFile | None = File(None),
    file_5: UploadFile | None = File(None),
    lang: str = Form(DEFAULT_LANG),
):
    context = _comparison_context(request, lang)
    cmp = context["cmp"]

    upload_slots = [file_1, file_2, file_3, file_4, file_5]

    # Files must occupy consecutive slots:
    # uploading file 4 while leaving file 3 empty is not allowed.
    seen_empty_slot = False
    files: list[UploadFile] = []

    for upload in upload_slots:
        has_file = upload is not None and bool(upload.filename)

        if not has_file:
            seen_empty_slot = True
            continue

        if seen_empty_slot:
            context["error_message"] = cmp["error_gap"]
            return templates.TemplateResponse(
                "comparison.html",
                context,
                status_code=400,
            )

        files.append(upload)

    if not 2 <= len(files) <= 5:
        context["error_message"] = cmp["error_count"]
        return templates.TemplateResponse(
            "comparison.html",
            context,
            status_code=400,
        )

    analyses: list[dict[str, Any]] = []

    # The temporal order is exactly the order of the slots.
    for index, upload in enumerate(files):
        filename = Path(
            upload.filename or f"analysis_{index + 1}.csv"
        ).name

        if Path(filename).suffix.lower() != ".csv":
            context["error_message"] = (
                f"{cmp['error_csv']} ({filename})"
            )
            return templates.TemplateResponse(
                "comparison.html",
                context,
                status_code=400,
            )

        try:
            raw = await upload.read()
            fieldnames, rows = _read_rows(raw)
            measures = _extract_measures(fieldnames, rows)

        except (ValueError, csv.Error, UnicodeError):
            context["error_message"] = (
                f"{cmp['error_csv']} ({filename})"
            )
            return templates.TemplateResponse(
                "comparison.html",
                context,
                status_code=400,
            )

        if not measures:
            context["error_message"] = (
                f"{cmp['error_empty']} ({filename})"
            )
            return templates.TemplateResponse(
                "comparison.html",
                context,
                status_code=400,
            )

        analyses.append(
            {
                "filename": filename,
                "task": _extract_task(fieldnames, rows),
                "measures": measures,
                "upload_index": index,
            }
        )

    # If the CSV files explicitly include the task,
    # we check that it is the same.
    explicit_tasks = {
        item["task"]
        for item in analyses
        if item["task"]
    }

    if len(explicit_tasks) > 1:
        context["error_message"] = cmp["error_task"]
        return templates.TemplateResponse(
            "comparison.html",
            context,
            status_code=400,
        )

    # All CSV files must have exactly the same measures.
    reference_measures = set(analyses[0]["measures"])

    if any(
        set(item["measures"]) != reference_measures
        for item in analyses[1:]
    ):
        context["error_message"] = cmp["error_mixed"]
        return templates.TemplateResponse(
            "comparison.html",
            context,
            status_code=400,
        )

    # Not sorted by date: the slot order is preserved.
    labels: list[str] = []

    for position, item in enumerate(analyses, start=1):
        item["position"] = position
        labels.append(str(position))

    metric_payload = []

    for metric in sorted(reference_measures, key=str.casefold):
        values = [
            item["measures"][metric]
            for item in analyses
        ]

        delta_labels = ["—"]

        for previous, current in zip(values, values[1:]):
            delta = current - previous
            delta_labels.append(f"{delta:+.4g}")

        metric_payload.append(
            {
                "name": metric,
                "values": values,
                "delta_labels": delta_labels,
            }
        )

    plot_data = {
        "labels": labels,
        "filenames": [
            item["filename"]
            for item in analyses
        ],
        "metrics": metric_payload,
        "title": cmp["plot_title"],
    }

    context.update(
        {
            "analyses": analyses,
            "plot_data_json": json.dumps(
                plot_data,
                ensure_ascii=False,
                allow_nan=False,
            ),
        }
    )

    return templates.TemplateResponse(
        "comparison.html",
        context,
    )