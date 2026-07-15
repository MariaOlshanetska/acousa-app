from pathlib import Path
import base64
import mimetypes
import wave
import numpy as np
from collections import defaultdict
from typing import Iterable
import math

from core.config import UPLOAD_DIR, RESULTS_DIR

# --- límites de retención (máx. "grabaciones"/grupos) ---
MAX_AUDIO_ITEMS = 100
MAX_TEXTGRID_ITEMS = 100

MIN_DURATION_SEC = 3.0
MIN_INTENSITY_RANGE_DB = 30.0

# --- extensiones que queremos considerar ---
AUDIO_EXTS = {".wav", ".mp3", ".ogg", ".webm", ".m4a", ".mp4"}
RESULT_EXTS = {".csv", ".png", ".TextGrid", ".txt", ".json", ".wav"}

def _group_key_for_upload(p: Path) -> str:
    # agrupa por el stem (uuid), así borra original+wav juntos
    return p.stem

def _group_key_for_results(p: Path) -> str:
    stem = p.stem
    for suffix in ("_analysis", "_normalitat", "_transcript", "_meta"):
        if stem.endswith(suffix):
            return stem[: -len(suffix)]
    return stem

def audio_duration_and_intensity_range_db(wav_path: Path, frame_ms: int = 20, hop_ms: int = 10):
    """
    Devuelve:
      - duration_sec: duración en segundos
      - range_db: (p95 - p5) del RMS en dBFS por ventanas (aprox. contraste voz–fondo)
    """
    with wave.open(str(wav_path), "rb") as wf:
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        sr = wf.getframerate()
        nframes = wf.getnframes()
        duration_sec = nframes / float(sr) if sr else 0.0
        raw = wf.readframes(nframes)

    if nframes == 0 or sr == 0:
        return duration_sec, 0.0

    # Decodificación según sample width típico
    if sampwidth == 2:
        x = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    elif sampwidth == 4:
        x = np.frombuffer(raw, dtype=np.int32).astype(np.float32) / 2147483648.0
    elif sampwidth == 1:
        # 8-bit suele ser unsigned
        x = (np.frombuffer(raw, dtype=np.uint8).astype(np.float32) - 128.0) / 128.0
    else:
        # formato raro → no bloqueamos por intensidad, solo por duración
        return duration_sec, 999.0

    if n_channels > 1:
        x = x.reshape(-1, n_channels).mean(axis=1)

    win = max(int(sr * frame_ms / 1000), 1)
    hop = max(int(sr * hop_ms / 1000), 1)

    eps = 1e-12
    rms_db = []
    for i in range(0, len(x) - win + 1, hop):
        chunk = x[i : i + win]
        rms = np.sqrt(np.mean(chunk * chunk) + eps)
        db = 20.0 * np.log10(rms + eps)  # dBFS
        rms_db.append(db)

    if not rms_db:
        return duration_sec, 0.0

    rms_db = np.array(rms_db, dtype=np.float32)
    rms_db = np.maximum(rms_db, -80.0)  # suelo para evitar -inf por silencios

    hi = float(np.percentile(rms_db, 95))
    lo = float(np.percentile(rms_db, 5))
    return duration_sec, max(0.0, hi - lo)

def prune_dir_by_groups(
    dir_path: Path,
    *,
    max_groups: int,
    exts: set[str],
    group_key_fn,
    delete_extra_patterns_fn=None,
):
    """
    Mantiene como máximo 'max_groups' grupos (grabaciones) en dir_path.
    Si se supera, borra el grupo más viejo (según mtime más reciente del grupo).
    """
    if max_groups <= 0 or not dir_path.exists():
        return

    files = [p for p in dir_path.iterdir() if p.is_file() and p.suffix.lower() in exts]
    if not files:
        return

    groups = defaultdict(list)
    for p in files:
        groups[group_key_fn(p)].append(p)

    # Ordenar grupos por "recencia": mtime máximo dentro de cada grupo
    def group_mtime(key: str) -> float:
        return max(x.stat().st_mtime for x in groups[key])

    keys_sorted = sorted(groups.keys(), key=group_mtime, reverse=True)

    # Mantener los N más recientes; borrar el resto
    to_delete_keys = keys_sorted[max_groups:]

    for key in to_delete_keys:
        for p in groups[key]:
            try:
                p.unlink(missing_ok=True)
            except Exception:
                pass

        # Por si quieres borrar también derivados con patrones extra
        if delete_extra_patterns_fn is not None:
            for p in delete_extra_patterns_fn(key):
                try:
                    p.unlink(missing_ok=True)
                except Exception:
                    pass


def prune_uploads():
    prune_dir_by_groups(
        UPLOAD_DIR,
        max_groups=MAX_AUDIO_ITEMS,
        exts=AUDIO_EXTS,
        group_key_fn=_group_key_for_upload,
    )


def prune_results():
    def extra_patterns(stem: str) -> Iterable[Path]:
        # Borra derivados típicos (por si algún sufijo no entra en RESULT_EXTS o cambia el nombre)
        yield RESULTS_DIR / f"{stem}_analysis.csv"
        yield RESULTS_DIR / f"{stem}_normalitat.png"
        yield RESULTS_DIR / f"{stem}_transcript.txt"
        yield RESULTS_DIR / f"{stem}_meta.json"

    prune_dir_by_groups(
        RESULTS_DIR,
        max_groups=MAX_TEXTGRID_ITEMS,
        exts=RESULT_EXTS,
        group_key_fn=_group_key_for_results,
        delete_extra_patterns_fn=extra_patterns,
    )


def safe_unlink(p: Path | None):
    if not p:
        return
    try:
        p.unlink(missing_ok=True)
    except Exception:
        pass

def png_to_data_uri(p: Path) -> str:
    b64 = base64.b64encode(p.read_bytes()).decode("utf-8")
    return f"data:image/png;base64,{b64}"

def file_to_data_uri(p: Path, mime_type: str | None = None) -> str:
    if mime_type is None:
        mime_type = mimetypes.guess_type(str(p))[0] or "application/octet-stream"
    b64 = base64.b64encode(p.read_bytes()).decode("utf-8")
    return f"data:{mime_type};base64,{b64}"

def csv_to_data_uri(p: Path) -> str:
    b64 = base64.b64encode(p.read_bytes()).decode("utf-8")
    return f"data:text/csv;charset=utf-8;base64,{b64}"

def clean_label(s: str) -> str:
    # arregla el “â€“” típico de encoding mal interpretado
    return (s or "").replace("â€“", "–").replace("â€”", "—")

def to_float(x):
    try:
        return float(str(x).replace(",", "."))
    except Exception:
        return None

import math

_NOTE_NAMES = {
    "es": ["Do", "Do#", "Re", "Re#", "Mi", "Fa", "Fa#", "Sol", "Sol#", "La", "La#", "Si"],
    "ca": ["Do", "Do#", "Re", "Re#", "Mi", "Fa", "Fa#", "Sol", "Sol#", "La", "La#", "Si"],
    "en": ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"],
}

def hz_to_note_label(f_hz: float, lang: str = "es") -> str:
    """
    Convierte frecuencia (Hz) a nota temperada (A4=440).
    Devuelve p.ej. "La3 (A3)" en es/ca, o "A3" en en.
    """
    if f_hz is None or f_hz <= 0:
        return ""

    midi = 69 + 12 * math.log2(f_hz / 440.0)
    midi_round = int(round(midi))

    note_idx = midi_round % 12
    octave = midi_round // 12 - 1

    names = _NOTE_NAMES.get(lang, _NOTE_NAMES["en"])
    name_local = names[note_idx]
    name_en = _NOTE_NAMES["en"][note_idx]

    if lang in ("es", "ca"):
        return f"{name_local}{octave} ({name_en}{octave})"
    return f"{name_local}{octave}"