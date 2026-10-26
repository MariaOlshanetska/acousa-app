from pathlib import Path
import os
import sys
import shutil

from fastapi import HTTPException
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles


def cmd(default_name: str, env_var: str) -> str:
    v = os.getenv(env_var)
    if v:
        return v
    which = shutil.which(default_name)
    if which:
        return which
    return default_name


PRAAT_CMD = cmd("praat", "PRAAT_CMD")
RSCRIPT_CMD = cmd("Rscript", "RSCRIPT_CMD")
FFMPEG_CMD = cmd("ffmpeg", "FFMPEG_CMD")
MFA_CMD = os.getenv("MFA_CMD", "/srv/labfon/conda_envs/mfa/bin/mfa")
PYTHON_CMD = sys.executable

BASE_DIR = Path(__file__).resolve().parent.parent  # project root
UPLOAD_DIR = BASE_DIR / "uploads"
RESULTS_DIR = BASE_DIR / "results"
SCRIPTS_DIR = BASE_DIR / "scripts"

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def init_app(app):
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

    # Abans aquí hi havia un muntatge estàtic de /results que servia QUALSEVOL fitxer per URL
    # directa, inclosos els .wav. Això feia inútil el token: qualsevol tercer amb l'enllaç podia
    # obrir /results/<stem>.wav i baixar-se l'àudio biomètric. Ara servim /results amb una ruta
    # pròpia que deixa passar CSV, TextGrid i .txt però BLOQUEJA els .wav; l'àudio només surt per
    # la ruta protegida d'un sol ús (/clinica/results/{rid}/audio).
    results_root = RESULTS_DIR.resolve()

    @app.get("/results/{file_path:path}", name="results")
    async def results_file(file_path: str):
        target = (RESULTS_DIR / file_path).resolve()

        # Protecció contra path traversal: el fitxer demanat ha d'estar dins de RESULTS_DIR.
        # Motiu de seguretat: evitem que algú surti del directori (p. ex. ../core/config.py).
        if not target.is_relative_to(results_root):
            raise HTTPException(status_code=404)

        # Mai servim .wav per aquesta via: l'àudio biomètric només és accessible amb el token
        # d'un sol ús. Qualsevol intent d'obtenir un .wav directament retorna 404.
        if target.suffix.lower() == ".wav":
            raise HTTPException(status_code=404)

        if not target.is_file():
            raise HTTPException(status_code=404)

        # CSV, TextGrid i .txt segueixen baixant-se exactament com abans.
        return FileResponse(str(target))

    app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
