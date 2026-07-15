from fastapi import APIRouter, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from core.texts import get_texts, DEFAULT_LANG
from core.config import templates
from pathlib import Path
from functools import lru_cache
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED
from email.message import EmailMessage
from email.policy import SMTP
import pandas as pd
import requests
import re
import unicodedata
import uuid
import shutil
from datetime import datetime, timedelta


router = APIRouter(prefix="/recursos/tfg-mails")


# ---------- utilidades ----------

REQUIRED_COLUMNS = {"Nom", "Correu", "Tutor"}

TEMP_TFG_DIR = Path("tmp_tfg_mails")
TEMP_TFG_DIR.mkdir(exist_ok=True)


def cleanup_old_temp_files(hours: int = 12):
    cutoff = datetime.now() - timedelta(hours=hours)
    for p in TEMP_TFG_DIR.glob("*"):
        try:
            if p.is_file():
                mtime = datetime.fromtimestamp(p.stat().st_mtime)
                if mtime < cutoff:
                    p.unlink(missing_ok=True)
        except Exception:
            pass


def save_uploaded_excel_tmp(upload_file: UploadFile) -> tuple[str, Path]:
    cleanup_old_temp_files()

    upload_id = uuid.uuid4().hex
    original_name = Path(upload_file.filename or "input.xlsx").name
    suffix = Path(original_name).suffix or ".xlsx"
    temp_path = TEMP_TFG_DIR / f"{upload_id}{suffix}"

    with temp_path.open("wb") as f:
        shutil.copyfileobj(upload_file.file, f)

    return upload_id, temp_path


def get_temp_excel_path(upload_id: str) -> Path | None:
    for p in TEMP_TFG_DIR.glob(f"{upload_id}.*"):
        if p.is_file():
            return p
    return None


def normalize_spaces(s: str) -> str:
    return re.sub(r"\s+", " ", str(s or "").strip())


def strip_accents(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in s if not unicodedata.combining(ch))


def first_name_from_full_name(full_name: str) -> str:
    full_name = normalize_spaces(full_name)
    if not full_name:
        return ""
    # cogemos el primer token
    return full_name.split(" ")[0]


def safe_filename(value: str) -> str:
    value = strip_accents(normalize_spaces(value))
    value = re.sub(r"[^A-Za-z0-9._-]+", "_", value)
    return value.strip("._-") or "mail"


@lru_cache(maxsize=3000)
def infer_name_gender(first_name: str, country_id: str = "ES") -> dict:
    """
    Usa Genderize como estimación estadística.
    Devuelve mode = female / male / neutral
    """
    first_name = normalize_spaces(first_name)
    if not first_name:
        return {
            "gender": None,
            "probability": None,
            "count": None,
            "mode": "neutral",
        }

    params = {"name": first_name}
    if country_id:
        params["country_id"] = country_id

    try:
        r = requests.get("https://api.genderize.io", params=params, timeout=5)
        r.raise_for_status()
        data = r.json()
    except Exception:
        return {
            "gender": None,
            "probability": None,
            "count": None,
            "mode": "neutral",
        }

    gender = data.get("gender")
    probability = data.get("probability")
    count = data.get("count")

    try:
        probability = float(probability) if probability is not None else None
    except Exception:
        probability = None

    try:
        count = int(count) if count is not None else None
    except Exception:
        count = None

    # regla prudente: solo asumimos si hay suficiente confianza
    if gender in {"female", "male"} and probability is not None and count is not None:
        if probability >= 0.85 and count >= 20:
            mode = gender
        else:
            mode = "neutral"
    else:
        mode = "neutral"

    return {
        "gender": gender,
        "probability": probability,
        "count": count,
        "mode": mode,
    }


def build_salutation(mode: str, nom: str) -> str:
    if mode == "female":
        return f"Benvolguda {nom},"
    if mode == "male":
        return f"Benvolgut {nom},"
    return f"Benvolguda/Benvolgut {nom},"


def default_template_ca() -> str:
    return """{salutacio}

Et confirmo que qui supervisarà el teu TFG és {Tutor}.
En començar el segon quadrimestre, es posarà en contacte amb tu per iniciar el procés de tutorització.

Aprofito per desitjar-te un molt bon segon quadrimestre.

Ben cordialment,

{coordinadora}
"""


def create_email_body(row: dict, coordinadora: str, template: str, country_id: str = "ES") -> tuple[str, dict]:
    nom = normalize_spaces(row.get("Nom", ""))
    tutor = normalize_spaces(row.get("Tutor", ""))
    first_name = first_name_from_full_name(nom)

    g = infer_name_gender(first_name, country_id=country_id)
    salutacio = build_salutation(g["mode"], nom)

    values = dict(row)
    values["Nom"] = nom
    values["Tutor"] = tutor
    values["coordinadora"] = coordinadora
    values["salutacio"] = salutacio
    values["tractament_mode"] = g["mode"]

    body = template.format(**values)
    return body, g


def build_eml_bytes(from_name: str, from_email: str, to_email: str, subject: str, body: str) -> bytes:
    msg = EmailMessage(policy=SMTP)
    msg["From"] = f"{from_name} <{from_email}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)
    return msg.as_bytes()


# ---------- rutas ----------

@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def tfg_mails_form(request: Request, lang: str = DEFAULT_LANG):
    ui, lang = get_texts(lang)
    return templates.TemplateResponse(
        "tfg_mails.html",
        {
            "request": request,
            "ui": ui,
            "lang": lang,
            "rows": [],
            "error_message": None,
            "status_message": None,
            "coordinadora": "Wendy",
            "remitent_email": "wendy@universitat.cat",
            "assumpte": "Assignació de tutor/a del TFG",
            "template_text": default_template_ca(),
            "country_id": "ES",
            "preview_ready": False,
            "upload_id": None,
        },
    )


@router.post("/preview", response_class=HTMLResponse)
async def tfg_mails_preview(
    request: Request,
    excel: UploadFile = File(...),
    coordinadora: str = Form(...),
    remitent_email: str = Form(...),
    assumpte: str = Form("Assignació de tutor/a del TFG"),
    template_text: str = Form(...),
    country_id: str = Form("ES"),
    lang: str = Form(DEFAULT_LANG),
):
    ui, lang = get_texts(lang)

    rows = []
    error_message = None
    status_message = None
    upload_id = None

    try:
        upload_id, temp_path = save_uploaded_excel_tmp(excel)

        df = pd.read_excel(temp_path)
        missing = REQUIRED_COLUMNS - set(df.columns)
        if missing:
            raise ValueError("L'Excel ha de tenir les columnes: Nom, Correu i Tutor")

        df = df.fillna("")

        for _, r in df.iterrows():
            row = {k: str(v) for k, v in r.to_dict().items()}
            body, g = create_email_body(
                row=row,
                coordinadora=coordinadora,
                template=template_text,
                country_id=country_id.strip().upper() or "ES",
            )

            rows.append(
                {
                    "Nom": normalize_spaces(row.get("Nom", "")),
                    "Correu": normalize_spaces(row.get("Correu", "")),
                    "Tutor": normalize_spaces(row.get("Tutor", "")),
                    "salutacio": body.splitlines()[0] if body else "",
                    "tractament_mode": g["mode"],
                    "gender": g["gender"],
                    "probability": g["probability"],
                    "count": g["count"],
                    "cos_correu": body,
                }
            )

        status_message = f"S'han preparat {len(rows)} correus."
    except Exception as e:
        error_message = str(e)

    return templates.TemplateResponse(
        "tfg_mails.html",
        {
            "request": request,
            "ui": ui,
            "lang": lang,
            "rows": rows,
            "error_message": error_message,
            "status_message": status_message,
            "coordinadora": coordinadora,
            "remitent_email": remitent_email,
            "assumpte": assumpte,
            "template_text": template_text,
            "country_id": country_id,
            "preview_ready": bool(rows),
            "upload_id": upload_id,
        },
    )


@router.post("/download-zip")
async def tfg_mails_download_zip(
    upload_id: str = Form(...),
    coordinadora: str = Form(...),
    remitent_email: str = Form(...),
    assumpte: str = Form("Assignació de tutor/a del TFG"),
    template_text: str = Form(...),
    country_id: str = Form("ES"),
):
    temp_path = get_temp_excel_path(upload_id)
    if not temp_path or not temp_path.exists():
        raise ValueError("L'arxiu temporal no existeix o ha caducat. Torna a previsualitzar.")

    df = pd.read_excel(temp_path)
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError("L'Excel ha de tenir les columnes: Nom, Correu i Tutor")

    df = df.fillna("")

    zip_buffer = BytesIO()
    with ZipFile(zip_buffer, "w", ZIP_DEFLATED) as zf:
        for i, (_, r) in enumerate(df.iterrows(), start=1):
            row = {k: str(v) for k, v in r.to_dict().items()}
            body, g = create_email_body(
                row=row,
                coordinadora=coordinadora,
                template=template_text,
                country_id=country_id.strip().upper() or "ES",
            )

            eml_bytes = build_eml_bytes(
                from_name=coordinadora,
                from_email=remitent_email,
                to_email=normalize_spaces(row.get("Correu", "")),
                subject=assumpte,
                body=body,
            )

            nom = safe_filename(row.get("Nom", f"persona_{i}"))
            mode = g["mode"]
            filename = f"{i:03d}_{nom}_{mode}.eml"
            zf.writestr(filename, eml_bytes)

    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": 'attachment; filename="correus_eml.zip"'},
    )


@router.post("/download-excel")
async def tfg_mails_download_excel(
    upload_id: str = Form(...),
    coordinadora: str = Form(...),
    remitent_email: str = Form(...),
    assumpte: str = Form("Assignació de tutor/a del TFG"),
    template_text: str = Form(...),
    country_id: str = Form("ES"),
):
    temp_path = get_temp_excel_path(upload_id)
    if not temp_path or not temp_path.exists():
        raise ValueError("L'arxiu temporal no existeix o ha caducat. Torna a previsualitzar.")

    df = pd.read_excel(temp_path)
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError("L'Excel ha de tenir les columnes: Nom, Correu i Tutor")

    df = df.fillna("")

    out_rows = []
    for _, r in df.iterrows():
        row = {k: str(v) for k, v in r.to_dict().items()}
        body, g = create_email_body(
            row=row,
            coordinadora=coordinadora,
            template=template_text,
            country_id=country_id.strip().upper() or "ES",
        )

        out_rows.append(
            {
                "Nom": normalize_spaces(row.get("Nom", "")),
                "Correu": normalize_spaces(row.get("Correu", "")),
                "Tutor": normalize_spaces(row.get("Tutor", "")),
                "assumpte": assumpte,
                "salutacio": body.splitlines()[0] if body else "",
                "tractament_mode": g["mode"],
                "genderize_gender": g["gender"],
                "genderize_probability": g["probability"],
                "genderize_count": g["count"],
                "cos_correu": body,
            }
        )

    out_df = pd.DataFrame(out_rows)
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        out_df.to_excel(writer, index=False, sheet_name="correus")
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="correus_generats.xlsx"'},
    )