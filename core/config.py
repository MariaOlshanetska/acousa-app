from pathlib import Path
import os
import sys
import shutil

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

BASE_DIR = Path(__file__).resolve().parent.parent  # raíz del proyecto
UPLOAD_DIR = BASE_DIR / "uploads"
RESULTS_DIR = BASE_DIR / "results"
SCRIPTS_DIR = BASE_DIR / "scripts"

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def init_app(app):
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
    app.mount("/results", StaticFiles(directory=str(RESULTS_DIR)), name="results")
    app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
