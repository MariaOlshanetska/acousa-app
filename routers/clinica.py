
from __future__ import annotations

import base64
import csv
import json
import re
import shutil
import subprocess
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse

from core.config import (
    FFMPEG_CMD,
    MFA_CMD,
    PRAAT_CMD,
    PYTHON_CMD,
    RESULTS_DIR,
    RSCRIPT_CMD,
    SCRIPTS_DIR,
    UPLOAD_DIR,
    templates,
)
from core.tasks import TASKS
from core.texts import DEFAULT_LANG, get_texts
from core.utils import (
    MIN_DURATION_SEC,
    MIN_INTENSITY_RANGE_DB,
    audio_duration_and_intensity_range_db,
    prune_results,
    prune_uploads,
    safe_unlink,
)



router = APIRouter(prefix="/clinica")

# 1) Añade este import arriba, junto a los imports de core:
from core.consent import get_consent_page


# 2) Añade esta ruta en routers/clinica.py, después de `router = APIRouter(prefix="/clinica")`
#    y antes de la ruta index si quieres tenerlo ordenado:
@router.get("/consent", response_class=HTMLResponse)
async def consent_page(request: Request, lang: str = DEFAULT_LANG, mode: str = "science"):
    consent, lang, mode = get_consent_page(lang, mode)
    return templates.TemplateResponse(
        "consent.html",
        {
            "request": request,
            "lang": lang,
            "mode": mode,
            "consent": consent,
        },
    )

PATAKA_TARGET_VARS = [
    "delta_c",
    "delta_v",
    "npvi_c",
    "npvi_v",
    "percentage_v",
    "rpvi_c",
    "rpvi_v",
    "speech_rate",
    "varco_c",
    "varco_v",
    "vdist_cent_mean",
    "vdist_cent_sd",
]

PATAKA_LABELS = {
    "delta_c": "ΔC",
    "delta_v": "ΔV",
    "npvi_c": "nPVI-C",
    "npvi_v": "nPVI-V",
    "percentage_v": "%V",
    "rpvi_c": "rPVI-C",
    "rpvi_v": "rPVI-V",
    "speech_rate": "Speech rate",
    "varco_c": "VarcoC",
    "varco_v": "VarcoV",
    "vdist_cent_mean": "Mean V-to-V",
    "vdist_cent_sd": "SD V-to-V",
}

PATAKA_ORDER = [
    "speech_rate",
    "percentage_v",
    "delta_v",
    "delta_c",
    "varco_v",
    "varco_c",
    "rpvi_v",
    "rpvi_c",
    "npvi_v",
    "npvi_c",
    "vdist_cent_mean",
    "vdist_cent_sd",
]

RESULTS_META_DIR = RESULTS_DIR / "_meta"
RESULTS_META_DIR.mkdir(parents=True, exist_ok=True)

HABLA_LIBRE_NORMS_FILENAMES = (
    "habla_libre_norms_norms.csv",
    "centres_sd_robustos_habla_libre_norms.csv",
)

LECTURA_NORMS_FILENAMES = (
    "lectura_norms_universal.csv",
)

HABLA_LIBRE_RESULT_GROUPS = [
    {
        "id": "fluencia",
        "title_key": "hl_group_fluencia",
        "measures": [
            "speech_duration",
            "articulation_duration",
            "speech_rate",
            "articulation_rate",
            "pause_count",
            "mean_pause_duration",
            "pause_percentage",
            "long_pauses",
            "sentence_count",
            "mean_sentence_length_words",
            "sound_count",
        ],
    },
    {
        "id": "complejidad_lexica",
        "title_key": "hl_group_complejidad_lexica",
        "measures": [
            "unique_lexical_lemmas",
            "lexical_density",
            "lexical_ttr",
            "lexical_richness_score_1_5",
            "lexical_complexity_rare_percent",
            "mean_datamuse_frequency_per_million",
        ],
    },
    {
        "id": "complejidad_sintactica",
        "title_key": "hl_group_complejidad_sintactica",
        "measures": [
            "subordinate_clause_count",
            "subordinates_per_sentence",
        ],
    },
    {
        "id": "intonation",
        "title_key": "hl_group_intonation",
        "measures": [
            "f0_mean",
            "f0_sd",
            "f0_range",
        ],
    },
]

HABLA_LIBRE_MEASURE_TO_GROUP = {
    measure: group["id"]
    for group in HABLA_LIBRE_RESULT_GROUPS
    for measure in group["measures"]
}

HABLA_LIBRE_MEASURE_ORDER = [
    measure
    for group in HABLA_LIBRE_RESULT_GROUPS
    for measure in group["measures"]
]

HABLA_LIBRE_GROUP_TITLE_KEYS = {
    group["id"]: group["title_key"]
    for group in HABLA_LIBRE_RESULT_GROUPS
}

HABLA_LIBRE_LABEL_KEYS = {
    "speech_duration": "hl_label_speech_duration",
    "sound_count": "hl_label_sound_count",
    "articulation_duration": "hl_label_articulation_duration",
    "speech_rate": "hl_label_speech_rate",
    "articulation_rate": "hl_label_articulation_rate",
    "pause_count": "hl_label_pause_count",
    "mean_pause_duration": "hl_label_mean_pause_duration",
    "pause_percentage": "hl_label_pause_percentage",
    "long_pauses": "hl_label_long_pauses",
    "f0_mean": "hl_label_f0_mean",
    "f0_sd": "hl_label_f0_sd",
    "f0_range": "hl_label_f0_range",
    "sentence_count": "hl_label_sentence_count",
    "mean_sentence_length_words": "hl_label_mean_sentence_length_words",
    "subordinate_clause_count": "hl_label_subordinate_clause_count",
    "subordinates_per_sentence": "hl_label_subordinates_per_sentence",
    "unique_lexical_lemmas": "hl_label_unique_lexical_lemmas",
    "lexical_density": "hl_label_lexical_density",
    "lexical_ttr": "hl_label_lexical_ttr",
    "lexical_richness_score_1_5": "hl_label_lexical_richness_score_1_5",
    "lexical_complexity_rare_percent": "hl_label_lexical_complexity_rare_percent",
    "mean_datamuse_frequency_per_million": "hl_label_mean_datamuse_frequency_per_million",
}

HABLA_LIBRE_HELP_KEYS = {
    "speech_duration": "hl_help_speech_duration",
    "articulation_duration": "hl_help_articulation_duration",
    "sound_count": "hl_help_sound_count",
    "speech_rate": "hl_help_speech_rate",
    "articulation_rate": "hl_help_articulation_rate",
    "pause_count": "hl_help_pause_count",
    "mean_pause_duration": "hl_help_mean_pause_duration",
    "pause_percentage": "hl_help_pause_percentage",
    "long_pauses": "hl_help_long_pauses",
    "f0_mean": "hl_help_f0_mean",
    "f0_sd": "hl_help_f0_sd",
    "f0_range": "hl_help_f0_range",
    "sentence_count": "hl_help_sentence_count",
    "mean_sentence_length_words": "hl_help_mean_sentence_length_words",
    "subordinate_clause_count": "hl_help_subordinate_clause_count",
    "subordinates_per_sentence": "hl_help_subordinates_per_sentence",
    "unique_lexical_lemmas": "hl_help_unique_lexical_lemmas",
    "lexical_density": "hl_help_lexical_density",
    "lexical_ttr": "hl_help_lexical_ttr",
    "lexical_richness_score_1_5": "hl_help_lexical_richness_score_1_5",
    "lexical_complexity_rare_percent": "hl_help_lexical_complexity_rare_percent",
    "mean_datamuse_frequency_per_million": "hl_help_mean_datamuse_frequency_per_million",
}


def _ui_text(ui: dict[str, Any] | None, key: str, default: str = "") -> str:
    if isinstance(ui, dict):
        return str(ui.get(key, default))
    return default


def _hl_group_title(ui: dict[str, Any] | None, group_id: str) -> str:
    key = HABLA_LIBRE_GROUP_TITLE_KEYS.get(group_id, "")
    return _ui_text(ui, key, group_id.replace("_", " ").title())


def _hl_label(ui: dict[str, Any] | None, measure: str) -> str:
    key = HABLA_LIBRE_LABEL_KEYS.get(measure, "")
    return _ui_text(ui, key, _clean_label(measure))


def _hl_help(ui: dict[str, Any] | None, measure: str) -> str:
    key = HABLA_LIBRE_HELP_KEYS.get(measure, "")
    return _ui_text(ui, key, "")


def _build_row_groups(
    rows: list[dict[str, Any]],
    group_defs: list[dict[str, Any]],
    ui: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Agrupa filas ya calculadas para que results.html pueda pintar un bloque por sección."""
    out: list[dict[str, Any]] = []
    by_var = {r.get("variable"): r for r in rows}

    for group in group_defs:
        group_rows = [by_var[m] for m in group["measures"] if m in by_var]
        if group_rows:
            out.append(
                {
                    "id": group["id"],
                    "title": _hl_group_title(ui, group["id"]),
                    "rows": group_rows,
                }
            )

    return out


def _lectura_norms_candidate_paths() -> list[Path]:
    """
    Posibles ubicaciones de la tabla normativa global de lectura.

    Recomendado en producción:
        scripts/lectura_norms_universal.csv

    También acepta:
        results/lectura_norms_universal.csv
        data/lectura_norms_universal.csv
        norms/lectura_norms_universal.csv
        lectura_norms_universal.csv en la raíz del proyecto
    """
    base_dir = SCRIPTS_DIR.parent
    folders = [
        SCRIPTS_DIR,
        RESULTS_DIR,
        base_dir / "data",
        base_dir / "norms",
        base_dir,
    ]
    return [folder / filename for folder in folders for filename in LECTURA_NORMS_FILENAMES]


def _load_lectura_norms() -> tuple[pd.DataFrame | None, Path | None]:
    """
    Carga una tabla normativa global de lectura con, como mínimo:
    measure, lower, upper.

    El CSV generado por build_lectura_norms.py incluye además:
    n, mean, sd, median, robust_sd, q05, q95, method.
    """
    for path in _lectura_norms_candidate_paths():
        if not path.exists():
            continue

        try:
            df = pd.read_csv(path, sep=None, engine="python")
        except Exception:
            continue

        required = {"measure", "lower", "upper"}
        if not required.issubset(df.columns):
            continue

        df = df.copy()
        df["measure"] = df["measure"].astype(str).str.strip()
        if "task" in df.columns:
            df = df[df["task"].astype(str).str.strip().eq("lectura")].copy()

        return df, path

    return None, None


def _select_lectura_norm(
    norms: pd.DataFrame | None,
    *,
    measure: str,
) -> tuple[pd.Series | None, str]:
    """Devuelve la referencia global disponible para una métrica de lectura."""
    if norms is None or norms.empty:
        return None, "missing_norms_file"

    sub = norms.loc[norms["measure"].eq(measure)].copy()
    if sub.empty:
        return None, "missing_measure"

    # Si en el futuro hay varias referencias, preferimos la más estable.
    if "n" in sub.columns:
        sub["_n_sort"] = pd.to_numeric(sub["n"], errors="coerce").fillna(-1)
        sub = sub.sort_values("_n_sort", ascending=False)

    return sub.iloc[0], "global"

def _lectura_hover_msg(
    *,
    ui: dict[str, Any] | None,
    value: float,
    unit: str,
    normal_min: float | None,
    normal_max: float | None,
    match_type: str,
    n: float | None,
    norms_table_name: str,
) -> str:
    """Text breu per al hover de les barres de lectura."""
    if normal_min is None or normal_max is None:
        if match_type == "missing_norms_file":
            return _ui_text(ui, "lectura_norm_missing_file", "No s'ha trobat la taula de normalitat de lectura.")
        if match_type == "missing_measure":
            return _ui_text(ui, "lectura_norm_missing_measure", "No hi ha rang de normalitat per a aquesta mesura de lectura.")
        return _ui_text(ui, "lectura_norm_missing_generic", "No hi ha cap referència disponible per a aquesta mesura.")

    unit_txt = f" {unit}" if unit else ""

    if value < normal_min:
        status = _ui_text(ui, "lectura_status_below", "per sota del rang provisional")
    elif value > normal_max:
        status = _ui_text(ui, "lectura_status_above", "per sobre del rang provisional")
    else:
        status = _ui_text(ui, "lectura_status_inside", "dins del rang provisional")

    msg = _ui_text(
        ui,
        "lectura_hover_message",
        "Referència global provisional: {normal_min}–{normal_max}{unit_txt}. El teu valor està {status}.",
    ).format(
        normal_min=f"{normal_min:.4g}",
        normal_max=f"{normal_max:.4g}",
        unit_txt=unit_txt,
        status=status,
    )

    if n is not None:
        msg += _ui_text(ui, "lectura_norm_n", " n={n}.").format(n=int(n))

    if norms_table_name:
        msg += _ui_text(ui, "lectura_table_note", " Taula normativa: {filename}.").format(
            filename=norms_table_name
        )

    msg += _ui_text(ui, "lectura_not_stratified", " Referència no estratificada per edat ni gènere.")

    return msg


def _global_lectura_interpretation(
    rows: list[dict[str, Any]],
    norms_table_name: str = "",
    ui: dict[str, Any] | None = None,
) -> tuple[str, str]:
    comparable = [
        r for r in rows
        if r.get("normal_min") is not None and r.get("normal_max") is not None
    ]
    altered = [r for r in comparable if r.get("severity") in {"mild", "marked"}]

    table_note = (
        _ui_text(ui, "lectura_table_note", " Taula normativa: {filename}.").format(
            filename=norms_table_name
        )
        if norms_table_name
        else ""
    )

    if not comparable:
        return (
            _ui_text(ui, "lectura_global_completed_title", "Anàlisi de lectura completada."),
            _ui_text(
                ui,
                "lectura_global_no_comparison_body",
                "No s'ha pogut comparar amb la normalitat perquè no s'ha trobat cap referència per a les mesures de lectura.",
            ),
        )

    if not altered:
        return (
            _ui_text(ui, "lectura_global_normal_title", "Perfil de lectura dins del rang provisional."),
            _ui_text(
                ui,
                "lectura_global_normal_body",
                "Les mesures comparables se situen dins de la referència global disponible. "
                "Aquests rangs són provisionals i no estan estratificats per edat ni gènere.{table_note}",
            ).format(table_note=table_note),
        )

    labels = ", ".join(r["label"] for r in altered[:5])

    return (
        _ui_text(ui, "lectura_global_altered_title", "Algunes mesures de lectura s'allunyen del rang provisional."),
        _ui_text(
            ui,
            "lectura_global_altered_body",
            "Les mesures que més s'aparten de la referència global disponible són: {labels}. "
            "Interpreta-ho com a cribratge descriptiu, no com a diagnòstic clínic tancat. "
            "Aquests rangs són provisionals i no estan estratificats per edat ni gènere.{table_note}",
        ).format(labels=labels, table_note=table_note),
    )


def _habla_libre_norms_candidate_paths() -> list[Path]:
    """
    Posibles ubicaciones de la tabla normativa de habla espontánea.

    Recomendado en producción:
        scripts/habla_libre_norms_norms.csv

    También acepta:
        scripts/centres_sd_robustos_habla_libre_norms.csv
        results/habla_libre_norms_norms.csv
        data/habla_libre_norms_norms.csv
    """
    base_dir = SCRIPTS_DIR.parent
    folders = [
        SCRIPTS_DIR,
        RESULTS_DIR,
        base_dir / "data",
        base_dir,
    ]
    return [folder / filename for folder in folders for filename in HABLA_LIBRE_NORMS_FILENAMES]


def _age_group_10(age: int | str | None) -> str:
    """Convierte 70 en '70-79', 63 en '60-69', etc."""
    try:
        a = int(age)
    except Exception:
        return "unknown"

    if a < 0:
        return "unknown"

    low = (a // 10) * 10
    high = low + 9
    return f"{low}-{high}"


def _norm_gender_token(gender_value: str | None) -> str:
    """
    Normaliza el sexo/género del formulario para que coincida con el CSV normativo.
    El CSV generado desde los nombres de archivo usa tokens como:
    home, dona, no_binari, etc.
    """
    g = _safe_filename_token(gender_value, "unknown")

    aliases = {
        "hombre": "home",
        "male": "home",
        "man": "home",
        "masculino": "home",
        "m": "home",
        "mujer": "dona",
        "female": "dona",
        "woman": "dona",
        "femenino": "dona",
        "f": "dona",
        "no_binario": "no_binari",
        "non_binary": "no_binari",
        "nonbinary": "no_binari",
        "nb": "no_binari",
    }
    return aliases.get(g, g)


def _load_habla_libre_norms() -> tuple[pd.DataFrame | None, Path | None]:
    """
    Carga la tabla normativa larga:
    age_group, gender, measure, normal_low, normal_high, median, mad_sd...
    """
    for path in _habla_libre_norms_candidate_paths():
        if not path.exists():
            continue

        try:
            df = pd.read_csv(path, sep=None, engine="python")
        except Exception:
            continue

        required = {"age_group", "gender", "measure", "normal_low", "normal_high"}
        if not required.issubset(df.columns):
            continue

        df = df.copy()
        df["age_group"] = df["age_group"].astype(str).str.strip()
        df["gender"] = df["gender"].astype(str).map(lambda x: _safe_filename_token(x, "unknown"))
        df["measure"] = df["measure"].astype(str).str.strip()
        return df, path

    return None, None


def _select_habla_libre_norm(
    norms: pd.DataFrame | None,
    *,
    measure: str,
    age: int | str | None,
    gender_value: str | None,
) -> tuple[pd.Series | None, str, str, str]:
    """
    Devuelve la fila normativa para una medida. 
    
    Prioridad:
      1) mismo grupo de edad + mismo género
      2) mismo grupo de edad + género agregado ('all', si existe)
      3) edad agregada ('all') + mismo género, si existe
      4) edad agregada + género agregado, si existe
      5) cualquier referencia disponible para esa medida

    El punto 5 es importante ahora mismo porque la tabla normativa disponible
    contiene solo un grupo. Así las barras se muestran para todos los usuarios,
    pero el hover avisa de que se usa la referencia provisional disponible.
    """
    age_group = _age_group_10(age)
    gender_token = _norm_gender_token(gender_value)

    if norms is None or norms.empty:
        return None, age_group, gender_token, "missing_norms_file"

    m = norms["measure"].eq(measure)
    all_age = norms["age_group"].isin(["all", "todos", "tots", "total"])
    all_gender = norms["gender"].isin(["all", "todos", "tots", "total"])

    candidates = [
        (m & norms["age_group"].eq(age_group) & norms["gender"].eq(gender_token), "exact"),
        (m & norms["age_group"].eq(age_group) & all_gender, "age_only"),
        (m & all_age & norms["gender"].eq(gender_token), "gender_only"),
        (m & all_age & all_gender, "global"),
    ]

    for mask, match_type in candidates:
        sub = norms.loc[mask]
        if not sub.empty:
            return sub.iloc[0], age_group, gender_token, match_type

    # Fallback: usa la referencia que exista para esa medida, aunque sea de otro grupo.
    # Ordenamos por n descendente para preferir la referencia más estable si en el futuro
    # hay varias filas disponibles.
    sub = norms.loc[m].copy()
    if not sub.empty:
        if "n" in sub.columns:
            sub["_n_sort"] = pd.to_numeric(sub["n"], errors="coerce").fillna(-1)
            sub = sub.sort_values("_n_sort", ascending=False)
        return sub.iloc[0], age_group, gender_token, "available_reference"

    return None, age_group, gender_token, "missing_measure"


def _severity_from_range_and_z(value: float | None, normal_min: float | None, normal_max: float | None, z: float | None) -> str:
    if value is None or normal_min is None or normal_max is None:
        return "missing"

    if normal_min <= value <= normal_max:
        return "normal"

    if z is not None:
        return _severity_from_z(z)

    return "mild"


def _habla_libre_hover_msg(
    *,
    ui: dict[str, Any] | None,
    help_text: str,
    value: float,
    unit: str,
    normal_min: float | None,
    normal_max: float | None,
    age_group: str,
    gender_token: str,
    match_type: str,
    n: float | None,
    warning: str | None,
) -> str:
    if normal_min is None or normal_max is None:
        if match_type == "missing_norms_file":
            return _ui_text(ui, "hl_norm_missing_file", "{help_text}").format(help_text=help_text)
        if match_type == "missing_measure":
            return _ui_text(ui, "hl_norm_missing_measure", "{help_text}").format(help_text=help_text)
        return _ui_text(
            ui,
            "hl_norm_missing_group",
            "No hay referencia para el grupo {age_group} / {gender_token}. {help_text}",
        ).format(age_group=age_group, gender_token=gender_token, help_text=help_text)

    ref_txt = _ui_text(ui, "hl_ref_exact", "Referencia {age_group} / {gender_token}").format(
        age_group=age_group,
        gender_token=gender_token,
    )
    if match_type == "age_only":
        ref_txt = _ui_text(ui, "hl_ref_age_only", "Referencia {age_group}, género agregado").format(
            age_group=age_group
        )
    elif match_type == "gender_only":
        ref_txt = _ui_text(ui, "hl_ref_gender_only", "Referencia género {gender_token}, edad agregada").format(
            gender_token=gender_token
        )
    elif match_type == "global":
        ref_txt = _ui_text(ui, "hl_ref_global", "Referencia global")
    elif match_type == "available_reference":
        ref_txt = _ui_text(ui, "hl_ref_available", "Referencia provisional disponible")

    unit_txt = f" {unit}" if unit else ""
    if value < normal_min:
        status = _ui_text(ui, "hl_status_below", "por debajo del rango provisional")
    elif value > normal_max:
        status = _ui_text(ui, "hl_status_above", "por encima del rango provisional")
    else:
        status = _ui_text(ui, "hl_status_inside", "dentro del rango provisional")

    msg = _ui_text(
        ui,
        "hl_norm_message",
        "{ref_txt}: {normal_min}–{normal_max}{unit_txt}. Tu valor está {status}.",
    ).format(
        ref_txt=ref_txt,
        normal_min=f"{normal_min:.4g}",
        normal_max=f"{normal_max:.4g}",
        unit_txt=unit_txt,
        status=status,
    )

    if n is not None:
        msg += _ui_text(ui, "hl_norm_n", " n={n}.").format(n=int(n))

    if warning:
        msg += _ui_text(ui, "hl_norm_warning", " Referencia provisional: conviene ampliarla con más controles.")

    return msg


def _global_habla_libre_interpretation(
    rows: list[dict[str, Any]],
    age: int | str | None,
    gender_value: str | None,
    ui: dict[str, Any] | None = None,
) -> tuple[str, str]:
    comparable = [r for r in rows if r.get("normal_min") is not None and r.get("normal_max") is not None]
    altered = [r for r in comparable if r.get("severity") in {"mild", "marked"}]

    age_group = _age_group_10(age)
    gender_token = _norm_gender_token(gender_value)

    uses_fallback = any(r.get("norm_match_type") == "available_reference" for r in comparable)

    if uses_fallback:
        ref_note = _ui_text(
            ui,
            "hl_ref_note_fallback",
            "Se ha usado la referencia provisional disponible para cada medida. "
            "La tabla normativa actual no contiene una referencia específica para {age_group} / {gender_token}.",
        ).format(age_group=age_group, gender_token=gender_token)
    else:
        ref_note = _ui_text(
            ui,
            "hl_ref_note_group",
            "Se ha usado la referencia disponible para el grupo {age_group} / {gender_token}.",
        ).format(age_group=age_group, gender_token=gender_token)

    if not comparable:
        return (
            _ui_text(ui, "hl_global_completed_title", "Análisis de habla espontánea completado."),
            _ui_text(
                ui,
                "hl_global_no_comparison_body",
                "No se ha podido comparar con normalidad porque no hay referencia disponible para el grupo {age_group} / {gender_token}.",
            ).format(age_group=age_group, gender_token=gender_token),
        )

    if not altered:
        return (
            _ui_text(ui, "hl_global_normal_title", "Perfil de habla espontánea dentro del rango provisional."),
            _ui_text(
                ui,
                "hl_global_normal_body",
                "Las medidas comparables se sitúan dentro del rango de referencia. {ref_note} "
                "Estos valores son descriptivos y provisionales si el grupo normativo aún tiene pocos controles.",
            ).format(ref_note=ref_note),
        )

    labels = ", ".join(r["label"] for r in altered[:5])
    return (
        _ui_text(ui, "hl_global_altered_title", "Algunas medidas se alejan del rango provisional."),
        _ui_text(
            ui,
            "hl_global_altered_body",
            "Las medidas que más se apartan de la referencia disponible son: {labels}. {ref_note} "
            "Interprétalo como cribado descriptivo, no como diagnóstico clínico cerrado.",
        ).format(labels=labels, ref_note=ref_note),
    )

def _safe_float(x: Any) -> float | None:
    try:
        if x is None:
            return None
        if isinstance(x, str):
            x = x.strip().replace(",", ".")
            if x == "":
                return None
        v = float(x)
        if np.isnan(v):
            return None
        return v
    except Exception:
        return None

def _build_lectura_rows(
    csv_path: Path,
    ui: dict[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], str, str]:
    df = pd.read_csv(csv_path, sep=None, engine="python")
    if df.empty:
        return [], "", ""

    row0 = df.iloc[0].to_dict()

    norms, norms_path = _load_lectura_norms()
    norms_table_name = norms_path.name if norms_path is not None else ""

    hidden_metrics = {
        # Columnas técnicas o auxiliares que no queremos pintar como resultados clínicos.
        "syllable_nuclei_estimated",
        "speech_intervals",
        "voice_start",
        "voice_end",
    }

    label_map = ui.get("lectura_measure_labels", {}) if isinstance(ui, dict) else {}

    rows = []
    for measure, raw_val in row0.items():
        if measure in hidden_metrics:
            continue

        val = _safe_float(raw_val)
        if val is None:
            continue

        unit = _infer_unit(measure)
        norm_row, match_type = _select_lectura_norm(norms, measure=measure)

        normal_min = _safe_float(norm_row.get("lower")) if norm_row is not None else None
        normal_max = _safe_float(norm_row.get("upper")) if norm_row is not None else None
        center = _safe_float(norm_row.get("median")) if norm_row is not None else None
        if center is None and norm_row is not None:
            center = _safe_float(norm_row.get("mean"))

        sd = _safe_float(norm_row.get("robust_sd")) if norm_row is not None else None
        if sd in (None, 0) and norm_row is not None:
            sd = _safe_float(norm_row.get("sd"))

        n_ref = _safe_float(norm_row.get("n")) if norm_row is not None else None

        z = None
        if val is not None and center is not None and sd not in (None, 0):
            z = (val - center) / sd

        if measure in {"speech_rate", "articulation_rate"}:
            unit = _ui_text(ui, "hl_unit_sounds_per_second", unit)
        elif measure == "mean_sentence_length_words":
            unit = _ui_text(ui, "hl_unit_words", unit)

        hover_msg = _lectura_hover_msg(
            ui=ui,
            value=val,
            unit=unit,
            normal_min=normal_min,
            normal_max=normal_max,
            match_type=match_type,
            n=n_ref,
            norms_table_name=norms_table_name,
        )


        rows.append(
            {
                "variable": measure,
                "label": label_map.get(measure, _clean_label(measure)),
                "value": round(val, 4),
                "z": round(z, 2) if z is not None else None,
                "hover_msg": hover_msg,
                "severity": _severity_from_range_and_z(val, normal_min, normal_max, z),
                "unit": unit,
                "normal_min": round(normal_min, 4) if normal_min is not None else None,
                "normal_max": round(normal_max, 4) if normal_max is not None else None,
                "norm_match_type": match_type,
                "n_ref": int(n_ref) if n_ref is not None else None,
                **_range_payload(val, normal_min, normal_max),
            }
        )

    interpretation_global, interpretation_comment = _global_lectura_interpretation(
        rows,
        norms_table_name,
        ui,
    )
    return rows, interpretation_global, interpretation_comment

def _build_habla_libre_rows(
    csv_path: Path,
    age: int | str | None = None,
    gender_value: str | None = None,
    ui: dict[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], str, str, str]:
    df = pd.read_csv(csv_path, sep=None, engine="python")
    if df.empty:
        return [], "", "", ""

    row0 = df.iloc[0].to_dict()
    norms, norms_path = _load_habla_libre_norms()

    hidden_metrics = {
        "total_duration",
        "transcription",
        "mfa_textgrid",
        "lemmas_json_txt",
        "word_count",
        "syllable_count_estimated",
        "speech_intervals",
        "voice_start",
        "voice_end",
        "lexical_complexity_index",
        "lexical_complexity_rarity_score",
        "lexical_mean_category_score_1_5",
        "total_tokens_stanza",
        "lexical_tokens",
        "rate_unit",
    }

    rows = []
    for measure in HABLA_LIBRE_MEASURE_ORDER:
        if measure in hidden_metrics or measure not in row0:
            continue

        raw_val = row0.get(measure)

        val = _safe_float(raw_val)
        if val is None:
            continue

        unit = _infer_unit(measure)
        if measure in {"speech_rate", "articulation_rate"}:
            unit = _ui_text(ui, "hl_unit_sounds_per_second", "sonidos/s")
        elif measure == "mean_sentence_length_words":
            unit = _ui_text(ui, "hl_unit_words", unit)

        norm_row, age_group, gender_token, match_type = _select_habla_libre_norm(
            norms,
            measure=measure,
            age=age,
            gender_value=gender_value,
        )

        normal_min = _safe_float(norm_row.get("normal_low")) if norm_row is not None else None
        normal_max = _safe_float(norm_row.get("normal_high")) if norm_row is not None else None
        center = _safe_float(norm_row.get("median")) if norm_row is not None else None
        sd = _safe_float(norm_row.get("mad_sd")) if norm_row is not None else None
        n_ref = _safe_float(norm_row.get("n")) if norm_row is not None else None
        warning_raw = norm_row.get("warning", "") if norm_row is not None else ""
        warning = "" if pd.isna(warning_raw) else str(warning_raw).strip()

        z = None
        if val is not None and center is not None and sd not in (None, 0):
            z = (val - center) / sd

        help_text = _hl_help(ui, measure)
        hover_msg = _habla_libre_hover_msg(
            ui=ui,
            help_text=help_text,
            value=val,
            unit=unit,
            normal_min=normal_min,
            normal_max=normal_max,
            age_group=age_group,
            gender_token=gender_token,
            match_type=match_type,
            n=n_ref,
            warning=warning,
        )
        group_id = HABLA_LIBRE_MEASURE_TO_GROUP.get(measure, "")

        row = {
            "variable": measure,
            "label": _hl_label(ui, measure),
            "group_id": group_id,
            "group_title": _hl_group_title(ui, group_id),
            "norm_match_type": match_type,
            "age_group": age_group,
            "gender_token": gender_token,
            "n_ref": int(n_ref) if n_ref is not None else None,
            "norm_warning": warning,
            "value": round(val, 4),
            "z": round(z, 2) if z is not None else None,
            "hover_msg": hover_msg,
            "help_text": help_text,
            "severity": _severity_from_range_and_z(val, normal_min, normal_max, z),
            "unit": unit,
            "normal_min": round(normal_min, 4) if normal_min is not None else None,
            "normal_max": round(normal_max, 4) if normal_max is not None else None,
            **_range_payload(val, normal_min, normal_max),
        }

        # El índice RLE debe verse claramente en escala 1–5.
        if measure == "lexical_richness_score_1_5":
            score = max(1.0, min(5.0, val))
            normal_min_score = max(1.0, min(5.0, normal_min)) if normal_min is not None else None
            normal_max_score = max(1.0, min(5.0, normal_max)) if normal_max is not None else None

            row.update(
                {
                    "value": round(score, 2),
                    "unit": "/5",
                    "display_min": 1,
                    "display_max": 5,
                    "value_rel": (score - 1.0) / 4.0,
                    "normal_min": round(normal_min_score, 4) if normal_min_score is not None else None,
                    "normal_max": round(normal_max_score, 4) if normal_max_score is not None else None,
                    "normal_min_rel": (normal_min_score - 1.0) / 4.0 if normal_min_score is not None else None,
                    "normal_max_rel": (normal_max_score - 1.0) / 4.0 if normal_max_score is not None else None,
                }
            )

        rows.append(row)
    
    order_index = {measure: i for i, measure in enumerate(HABLA_LIBRE_MEASURE_ORDER)}
    rows.sort(key=lambda r: order_index.get(r.get("variable"), 999))

    interpretation_global, interpretation_comment = _global_habla_libre_interpretation(rows, age, gender_value, ui)

    norms_table_name = norms_path.name if norms_path is not None else ""
    if norms_table_name and rows:
        interpretation_comment += " " + _ui_text(ui, "hl_table_normative", "Tabla normativa: {filename}.").format(
            filename=norms_table_name
        )

    return rows, interpretation_global, interpretation_comment, norms_table_name

def _localize_habla_libre_payload(payload: dict[str, Any], ui: dict[str, Any]) -> dict[str, Any]:
    """Retraduce filas guardadas en _meta cuando se cambia el idioma en la página de resultados."""
    if payload.get("task") != "habla_libre":
        return payload

    rows = payload.get("rows") or []
    age = payload.get("age")
    gender_value = payload.get("gender_value")

    for row in rows:
        measure = row.get("variable", "")
        group_id = HABLA_LIBRE_MEASURE_TO_GROUP.get(measure, "")

        row["label"] = _hl_label(ui, measure)
        row["help_text"] = _hl_help(ui, measure)
        row["group_id"] = group_id
        row["group_title"] = _hl_group_title(ui, group_id)

        unit = row.get("unit") or _infer_unit(measure)
        if measure in {"speech_rate", "articulation_rate"}:
            unit = _ui_text(ui, "hl_unit_sounds_per_second", unit or "sonidos/s")
        elif measure == "mean_sentence_length_words":
            unit = _ui_text(ui, "hl_unit_words", unit)
        row["unit"] = unit

        value = _safe_float(row.get("value"))
        normal_min = _safe_float(row.get("normal_min"))
        normal_max = _safe_float(row.get("normal_max"))
        age_group = row.get("age_group") or _age_group_10(age)
        gender_token = row.get("gender_token") or _norm_gender_token(gender_value)
        match_type = row.get("norm_match_type") or "missing_group"
        n_ref = _safe_float(row.get("n_ref"))
        warning = row.get("norm_warning") or ""

        if value is not None:
            row["hover_msg"] = _habla_libre_hover_msg(
                ui=ui,
                help_text=row.get("help_text", ""),
                value=value,
                unit=unit,
                normal_min=normal_min,
                normal_max=normal_max,
                age_group=age_group,
                gender_token=gender_token,
                match_type=match_type,
                n=n_ref,
                warning=warning,
            )

    payload["rows"] = rows
    payload["row_groups"] = _build_row_groups(rows, HABLA_LIBRE_RESULT_GROUPS, ui)

    interpretation_global, interpretation_comment = _global_habla_libre_interpretation(rows, age, gender_value, ui)
    norms_table_name = payload.get("hl_norms_table_name") or ""
    if norms_table_name and rows:
        interpretation_comment += " " + _ui_text(ui, "hl_table_normative", "Tabla normativa: {filename}.").format(
            filename=norms_table_name
        )

    payload["interpretation_global"] = interpretation_global
    payload["interpretation_comment"] = interpretation_comment
    return payload

def _norm_key(k: str) -> str:
    return k.strip().lower().replace(" ", "").replace("-", "_")


def _safe_filename_token(value: Any, default: str = "unknown") -> str:
    """
    Convierte cualquier metadato en un fragmento seguro para nombre de archivo.
    Ej.: "Dona" -> "dona", "Windows / Chrome" -> "windows_chrome".
    """
    if value is None:
        return default

    token = str(value).strip().lower()
    token = token.replace("à", "a").replace("á", "a").replace("ä", "a")
    token = token.replace("è", "e").replace("é", "e").replace("ë", "e")
    token = token.replace("ì", "i").replace("í", "i").replace("ï", "i")
    token = token.replace("ò", "o").replace("ó", "o").replace("ö", "o")
    token = token.replace("ù", "u").replace("ú", "u").replace("ü", "u")
    token = token.replace("ñ", "n").replace("ç", "c")
    token = re.sub(r"[^a-z0-9]+", "_", token)
    token = re.sub(r"_+", "_", token).strip("_")
    return token or default


def _final_gender_value(gender: str | None, gender_specify: str | None) -> str:
    g = (gender or "").strip()
    if _safe_filename_token(g) in {"altre", "altres", "otro", "otros", "other"} and (gender_specify or "").strip():
        return (gender_specify or "").strip()
    return g or "unknown"


def _browser_metadata_token(browser_metadata_json: str | None) -> str:
    """
    Devuelve el sufijo de contexto de grabación:
    windows_chrome, iphone_safari, android_chrome, etc.
    """
    if not browser_metadata_json:
        return "unknown_browser"

    try:
        meta = json.loads(browser_metadata_json)
        if not isinstance(meta, dict):
            return "unknown_browser"
    except Exception:
        return "unknown_browser"

    device = _safe_filename_token(meta.get("device_family"), "device")
    browser = _safe_filename_token(meta.get("browser_family"), "browser")
    return f"{device}_{browser}"


def _clean_label(name: str) -> str:
    x = str(name).replace("_", " ").strip()
    if not x:
        return ""
    return x[0].upper() + x[1:]


def _file_to_data_uri(path: Path, mime: str) -> str:
    raw = path.read_bytes()
    b64 = base64.b64encode(raw).decode("utf-8")
    return f"data:{mime};base64,{b64}"


def _csv_to_data_uri(path: Path) -> str:
    return _file_to_data_uri(path, "text/csv")


def _resolve_task_language(ui_lang: str) -> str:
    ui_lang = (ui_lang or "").strip().lower()
    if ui_lang == "es":
        return "es"
    return "ca"


def _infer_pipeline(task: str, task_cfg: dict[str, Any]) -> str:
    if task_cfg.get("pipeline"):
        return task_cfg["pipeline"]
    if task == "asos":
        return "python_r"
    if task == "lectura":
        return "acoustic_lectura"
    return "praat_r"


def _task_python_script(task_cfg: dict[str, Any], default_name: str | None = None) -> Path | None:
    name = task_cfg.get("python_script", default_name)
    if not name:
        return None
    return SCRIPTS_DIR / name


def _task_r_script(task_cfg: dict[str, Any], default_name: str | None = None) -> Path | None:
    name = task_cfg.get("r_script", default_name)
    if not name:
        return None
    return SCRIPTS_DIR / name


def _severity_from_z(z: float | None) -> str:
    if z is None:
        return "missing"
    az = abs(z)
    if az < 2:
        return "normal"
    if az < 3:
        return "mild"
    return "marked"


def _range_payload(value: float | None, normal_min: float | None, normal_max: float | None) -> dict[str, Any]:
    candidates = [x for x in [value, normal_min, normal_max] if x is not None]
    if not candidates:
        return {
            "display_min": 0.0,
            "display_max": 1.0,
            "value_rel": None,
            "normal_min_rel": None,
            "normal_max_rel": None,
        }

    lo = min(candidates)
    hi = max(candidates)
    span = hi - lo
    if span <= 0:
        span = abs(hi) * 0.2 if hi != 0 else 1.0
    pad = span * 0.20
    display_min = lo - pad
    display_max = hi + pad

    if normal_min is not None and normal_min >= 0 and display_min < 0:
        display_min = 0.0

    denom = display_max - display_min if display_max != display_min else 1.0

    def rel(x: float | None):
        if x is None:
            return None
        return (x - display_min) / denom

    return {
        "display_min": round(display_min, 4),
        "display_max": round(display_max, 4),
        "value_rel": rel(value),
        "normal_min_rel": rel(normal_min),
        "normal_max_rel": rel(normal_max),
    }


def _infer_unit(varname: str) -> str:
    key = _norm_key(varname)
    unit_map = {
        "mpt": "s",
        "f0_mean_hz": "Hz",
        "jitter_pct": "%",
        "shimmer_pct": "%",
        "hnr_db": "dB",
        "voice_breaks_percent": "%",
        "locally_unvoiced_percent": "%",
        "h1_h2": "dB",
        "h1_a1": "dB",
        "speech_rate": "sonidos/s",
        "articulation_rate": "sonidos/s",
        "pause_count": "",
        "mean_pause_duration": "s",
        "pause_percentage": "%",
        "long_pauses": "",
        "disfluencies": "",
        "f0_mean": "Hz",
        "f0_sd": "Hz",
        "f0_range": "Hz",
        "percentage_v": "%",
        "delta_v": "ms",
        "delta_c": "ms",
        "varco_v": "",
        "varco_c": "",
        "rpvi_v": "ms",
        "rpvi_c": "ms",
        "npvi_v": "",
        "npvi_c": "",
        "vdist_cent_mean": "ms",
        "vdist_cent_sd": "ms",
        "total_duration": "s",
        "total_duration_sec": "s",
        "sentence_count": "",
        "mean_sentence_length_words": "palabras",
        "subordinate_clause_count": "",
        "subordinates_per_sentence": "",
        "unique_lexical_lemmas": "",
        "lexical_density": "%",
        "lexical_ttr": "",
        "lexical_complexity_rare_percent": "%",
        "mean_datamuse_frequency_per_million": "pmw",
        "lexical_richness_score_1_5": "/5",
    }
    return unit_map.get(key, "")

NOTE_NAMES = ["C", "C♯", "D", "D♯", "E", "F", "F♯", "G", "G♯", "A", "A♯", "B"]

def _hz_to_note_label(freq_hz: float | None) -> str | None:
    if freq_hz is None or freq_hz <= 0:
        return None

    midi = round(69 + 12 * np.log2(freq_hz / 440.0))
    note_name = NOTE_NAMES[midi % 12]
    octave = (midi // 12) - 1
    return f"{note_name}{octave}"


def _pataka_display_value(varname: str, value: float | None) -> float | None:
    if value is None:
        return None
    if varname == "percentage_v":
        return value * 100.0
    if varname in {"delta_v", "delta_c", "vdist_cent_mean", "vdist_cent_sd", "rpvi_v", "rpvi_c"}:
        return value * 1000.0
    return value


def _pataka_display_center_sd(varname: str, center: float | None, sd: float | None) -> tuple[float | None, float | None]:
    if center is None or sd is None:
        return center, sd
    if varname == "percentage_v":
        return center * 100.0, sd * 100.0
    if varname in {"delta_v", "delta_c", "vdist_cent_mean", "vdist_cent_sd", "rpvi_v", "rpvi_c"}:
        return center * 1000.0, sd * 1000.0
    return center, sd


def _pataka_comment_for_var(var: str, z: float | None) -> str:
    if z is None:
        return ""
    az = abs(z)
    if var == "speech_rate":
        if z >= 2:
            return "Speech rate elevada respecto a la referencia."
        if z <= -2:
            return "Speech rate reducida respecto a la referencia."
        return ""
    if var == "percentage_v":
        if az < 2:
            return ""
        return "Porcentaje vocálico fuera de lo esperado."
    if az < 2:
        return ""
    return "Variabilidad temporal fuera de lo esperado."


def _global_pataka_interpretation(rows: list[dict[str, Any]]) -> tuple[str, str]:
    altered = [r for r in rows if r.get("severity") in {"mild", "marked"}]
    marked = [r for r in altered if r.get("severity") == "marked"]

    if not rows:
        return "", ""
    if not altered:
        return "Perfil global dentro del rango esperado.", "No se observan desviaciones relevantes en los parámetros rítmicos comparables."
    if marked:
        labels = ", ".join(r["label"] for r in marked[:4])
        return "Se observan alteraciones marcadas.", f"Las variables más alejadas del rango esperado son: {labels}."
    labels = ", ".join(r["label"] for r in altered[:5])
    return "Se observan alteraciones leves.", f"Las variables con mayor desviación son: {labels}."


def _build_pataka_rows(csv_path: Path, robust_xlsx: Path) -> tuple[list[dict[str, Any]], str, str]:
    df_audio = pd.read_csv(csv_path, sep=None, engine="python")
    robust = pd.read_excel(robust_xlsx)

    available_vars = [v for v in PATAKA_TARGET_VARS if v in df_audio.columns]
    robust = robust[robust["variable"].isin(available_vars)].copy()

    rows: list[dict[str, Any]] = []
    for var in PATAKA_ORDER:
        if var not in available_vars:
            continue

        raw_val = _safe_float(df_audio.iloc[0][var])
        ref = robust[robust["variable"] == var]

        raw_center = _safe_float(ref.iloc[0]["center_robust"]) if not ref.empty else None
        raw_sd = _safe_float(ref.iloc[0]["sd_robust"]) if not ref.empty else None

        val = _pataka_display_value(var, raw_val)
        center, sd = _pataka_display_center_sd(var, raw_center, raw_sd)

        z = None
        if val is not None and center is not None and sd not in (None, 0):
            z = (val - center) / sd

        normal_min = center - 2 * sd if center is not None and sd is not None else None
        normal_max = center + 2 * sd if center is not None and sd is not None else None

        rows.append(
            {
                "variable": var,
                "label": PATAKA_LABELS.get(var, var),
                "value": round(val, 4) if val is not None else None,
                "z": round(z, 2) if z is not None else None,
                "hover_msg": _pataka_comment_for_var(var, z),
                "severity": _severity_from_z(z),
                "unit": _infer_unit(var),
                "normal_min": round(normal_min, 4) if normal_min is not None else None,
                "normal_max": round(normal_max, 4) if normal_max is not None else None,
                **_range_payload(val, normal_min, normal_max),
            }
        )

    title, comment = _global_pataka_interpretation(rows)
    return rows, title, comment


def _gender_bucket(gender_value: str | None) -> str | None:
    if not gender_value:
        return None
    g = _norm_key(gender_value)
    if any(x in g for x in ("female", "femen", "mujer", "dona")) or g in {"f", "woman"}:
        return "f"
    if any(x in g for x in ("male", "masc", "hombre", "home")) or g in {"m", "man"}:
        return "m"
    return None


def _clinical_hover(
    varname: str,
    value: float | None,
    gender_value: str | None = None,
    ui: dict | None = None,
) -> str:
    if value is None:
        return ""

    key = _norm_key(varname)
    hover_texts = ui or {}

    def txt(text_key: str) -> str:
        return str(hover_texts.get(text_key, ""))

    if key == "mpt":
        if value >= 15:
            return ""
        return txt("mpt_reduced") if value < 10 else txt("mpt_slightly_reduced")

    if key == "f0_mean_hz":
        gb = _gender_bucket(gender_value)

        if gb == "f":
            lo, hi = 180.0, 300.0
        elif gb == "m":
            lo, hi = 95.0, 180.0
        else:
            lo, hi = 95.0, 300.0

        if lo <= value <= hi:
            return ""

        return txt("f0_high_tense") if value > hi else txt("f0_low_weak")

    if key == "jitter_pct":
        return "" if value <= 0.4 else txt("jitter_irregular")

    if key == "shimmer_pct":
        return "" if value <= 5.33 else txt("shimmer_instability")

    if key == "hnr_db":
        return "" if value >= 20 else txt("hnr_noise")

    if key == "voice_breaks_percent":
        return "" if value <= 0.37 else txt("voice_breaks")

    if key == "locally_unvoiced_percent":
        return "" if value <= 5.03 else txt("locally_unvoiced")

    if key == "h1_h2":
        if -4.05 <= value <= 15.48:
            return ""
        return txt("h1_h2_breathy") if value > 15.48 else txt("h1_h2_tense_hoarse")

    if key == "h1_a1":
        if value > 5.0:
            return txt("h1_a1_breathy_air_leak")
        return txt("h1_a1_nasality")

    return ""


def _build_asos_rows(csv_path: Path, gender_value: str | None, ui) -> tuple[list[dict[str, Any]], str, str, str]:
    df = pd.read_csv(csv_path, sep=None, engine="python")
    row0 = df.iloc[0].to_dict() if not df.empty else {}

    label_map = ui.get("clinical_measure_labels", {}) if isinstance(ui, dict) else {}

    norms: dict[str, tuple[float, float, str]] = {
        "mpt": (15.0, 30.0, "s"),
        "jitter_pct": (0.0, 0.4, "%"),
        "shimmer_pct": (0.0, 5.33, "%"),
        "hnr_db": (20.0, 35.0, "dB"),
        "voice_breaks_percent": (0.0, 0.37, "%"),
        "locally_unvoiced_percent": (0.0, 5.03, "%"),
        "h1_h2": (-4.05, 15.48, "dB"),
        "h1_a1": (-20.0, 5.0, "dB"),
    }

    rows: list[dict[str, Any]] = []

    for measure, raw_val in row0.items():
        val = _safe_float(raw_val)
        if val is None:
            continue

        normal_min = normal_max = None
        unit = _infer_unit(measure)

        if measure == "f0_mean_hz":
            gb = _gender_bucket(gender_value)
            if gb == "f":
                normal_min, normal_max = 180.0, 300.0
            elif gb == "m":
                normal_min, normal_max = 95.0, 180.0
            else:
                normal_min, normal_max = 95.0, 300.0
            unit = "Hz"

        elif measure in norms:
            normal_min, normal_max, unit = norms[measure]

        center = (
            (normal_min + normal_max) / 2.0
            if normal_min is not None and normal_max is not None
            else None
        )

        sd = (
            (normal_max - normal_min) / 4.0
            if normal_min is not None
            and normal_max is not None
            and normal_max > normal_min
            else None
        )

        z = (val - center) / sd if center is not None and sd not in (None, 0) else None

        rows.append(
            {
                "variable": measure,
                "label": label_map.get(measure, _clean_label(measure)),
                "value": round(val, 4),
                "z": round(z, 2) if z is not None else None,
                "hover_msg": _clinical_hover(measure, val, gender_value, ui),
                "severity": _severity_from_z(z),
                "unit": unit,
                "normal_min": round(normal_min, 4) if normal_min is not None else None,
                "normal_max": round(normal_max, 4) if normal_max is not None else None,
                **_range_payload(val, normal_min, normal_max),
            }
        )

    summary_texts = ui or {}

    def summary_txt(key: str, fallback: str = "", **kwargs) -> str:
        template = summary_texts.get(key, fallback)
        return template.format(**kwargs)

    alteration_comments = [
        r["hover_msg"]
        for r in rows
        if r.get("hover_msg") and r.get("severity") in {"mild", "marked"}
    ]

    h1_h2 = _safe_float(row0.get("h1_h2"))
    h1_a1 = _safe_float(row0.get("h1_a1"))
    hnr = _safe_float(row0.get("hnr_db"))

    breathy_pattern = (
        h1_h2 is not None and h1_h2 > 15.48
        and h1_a1 is not None and h1_a1 > 5.0
        and hnr is not None and hnr < 20.0
    )

    if breathy_pattern:
        alteration_comments.append(
            summary_txt(
                "asos_breathy_pattern_body",
                "La combinació d’H1–H2 i H1–A1 elevats amb un HNR baix pot ser compatible amb una veu més aviat airejada, però no és un criteri determinant per si sol.",
            )
        )

    if len(alteration_comments) >= 3:
        interpretation_global = summary_txt(
            "many_flags",
            "O bé l’enregistrament no és correcte, o bé la qualitat de la teva veu no és idònia.",
        )
    else:
        interpretation_global = summary_txt(
            "optimal",
            "La qualitat de la teva veu és òptima.",
        )

    if alteration_comments:
        interpretation_comment = summary_txt(
            "asos_global_comment_with_findings",
            (
                "En conjunt, aquests paràmetres descriuen diferents aspectes de la qualitat vocal. "
                "En aquest enregistrament destaquen aquests punts: {findings} "
                "La lectura és orientativa i no constitueix un diagnòstic tancat."
            ),
            findings=" ".join(dict.fromkeys(alteration_comments)),
        )
    else:
        interpretation_comment = summary_txt(
            "asos_global_comment_no_findings",
            (
                "En conjunt, les mesures comparables no mostren desviacions rellevants. "
                "La interpretació continua sent orientativa i depèn de la qualitat de l’enregistrament."
            ),
        )

    f0 = _safe_float(row0.get("f0_mean_hz"))
    note_label = _hz_to_note_label(f0)

    if f0 is not None and note_label:
        f0_summary_text = summary_txt(
            "f0_mean_with_note",
            "La teva freqüència mitjana és de {hz} Hz, cosa que equival a {note}.",
            hz=round(f0, 1),
            note=note_label,
        )
    elif f0 is not None:
        f0_summary_text = summary_txt(
            "f0_mean",
            "La teva freqüència mitjana és de {hz} Hz.",
            hz=round(f0, 1),
        )
    else:
        f0_summary_text = ""

    return rows, interpretation_global, interpretation_comment, f0_summary_text


def _build_generic_rows(csv_path: Path) -> tuple[list[dict[str, Any]], str, str]:
    df = pd.read_csv(csv_path, sep=None, engine="python")
    if df.empty:
        return [], "", ""
    row0 = df.iloc[0].to_dict()
    rows: list[dict[str, Any]] = []
    for measure, raw_val in row0.items():
        val = _safe_float(raw_val)
        if val is None:
            continue
        rows.append(
            {
                "variable": measure,
                "label": _clean_label(measure),
                "value": round(val, 4),
                "z": None,
                "hover_msg": "",
                "severity": "missing",
                "unit": _infer_unit(measure),
                "normal_min": None,
                "normal_max": None,
                **_range_payload(val, None, None),
            }
        )
    return rows, "", ""


def _read_csv_rows_for_template(csv_path: Path) -> list[dict[str, str]]:
    out = []
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            clean = {((k or "").lstrip("\ufeff").strip()): (v.strip() if isinstance(v, str) else v) for k, v in row.items()}
            out.append(clean)
    return out


def _prepare_downloads(
    store_data: bool,
    file_stem: str,
    task: str,
    csv_path: Path,
    wav_path: Path | None,
) -> tuple[str | None, str | None, str | None, str | None]:

    csv_name = f"{file_stem}_analysis.csv"
    audio_name = f"{file_stem}.wav"

    if store_data:
        csv_copy = RESULTS_DIR / csv_name
        if csv_path.resolve() != csv_copy.resolve():
            shutil.copy2(csv_path, csv_copy)
        csv_href = f"/results/{csv_copy.name}"

        if wav_path and wav_path.exists():
            wav_copy = RESULTS_DIR / audio_name
            if wav_path.resolve() != wav_copy.resolve():
                shutil.copy2(wav_path, wav_copy)
            audio_href = f"/results/{wav_copy.name}"
        else:
            audio_href = None
            audio_name = None

        return csv_href, csv_name, audio_href, audio_name

    csv_href = _csv_to_data_uri(csv_path) if csv_path.exists() else None
    audio_href = _file_to_data_uri(wav_path, "audio/wav") if wav_path and wav_path.exists() else None

    if not (wav_path and wav_path.exists()):
        audio_name = None

    return csv_href, csv_name, audio_href, audio_name

def _prepare_textgrid_download(
    store_data: bool,
    rid: str,
    task: str,
    textgrid_path: Path | None,
) -> tuple[str | None, str | None, str]:
    if not textgrid_path or not textgrid_path.exists():
        return None, None, ""

    textgrid_text = textgrid_path.read_text(encoding="utf-8", errors="replace")

    if store_data:
        tg_copy = RESULTS_DIR / f"{rid}_{task}.TextGrid"
        shutil.copy2(textgrid_path, tg_copy)
        return f"/results/{tg_copy.name}", tg_copy.name, textgrid_text

    tg_href = _file_to_data_uri(textgrid_path, "text/plain")
    tg_name = f"acousa_{task}_{rid}.TextGrid"
    return tg_href, tg_name, textgrid_text

def _prepare_txt_download(
    store_data: bool,
    rid: str,
    task: str,
    src_path: Path | None,
    suffix: str,
) -> tuple[str | None, str | None, str]:
    if not src_path or not src_path.exists():
        return None, None, ""

    txt = src_path.read_text(encoding="utf-8", errors="replace")

    if store_data:
        copy_path = RESULTS_DIR / f"{rid}_{task}_{suffix}.txt"
        shutil.copy2(src_path, copy_path)
        return f"/results/{copy_path.name}", copy_path.name, txt

    href = _file_to_data_uri(src_path, "text/plain")
    name = f"acousa_{task}_{rid}_{suffix}.txt"
    return href, name, txt


def _save_meta(rid: str, payload: dict[str, Any]) -> None:
    path = RESULTS_META_DIR / f"{rid}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _load_meta(rid: str) -> dict[str, Any] | None:
    path = RESULTS_META_DIR / f"{rid}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _build_index_context(request: Request, lang: str, task: str | None = None, error_message: str | None = None) -> dict[str, Any]:
    ui, lang = get_texts(lang)
    tasks = [{"id": task_id, "label": cfg["label"][lang]} for task_id, cfg in TASKS.items()]
    default_task = task or (tasks[0]["id"] if tasks else "")
    return {
        "request": request,
        "ui": ui,
        "lang": lang,
        "tasks": tasks,
        "default_task": default_task,
        "task_instructions_json": json.dumps({task_id: cfg["instructions"][lang] for task_id, cfg in TASKS.items()}, ensure_ascii=False),
        "task_reference_texts_json": json.dumps({task_id: cfg.get("reference_texts", {}).get(lang, "") for task_id, cfg in TASKS.items()}, ensure_ascii=False),
        "error_message": error_message,
    }


@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def index(request: Request, lang: str = DEFAULT_LANG):
    return templates.TemplateResponse("index.html", _build_index_context(request, lang))


@router.get("/results/{rid}", response_class=HTMLResponse)
async def show_results(request: Request, rid: str, lang: str = DEFAULT_LANG):
    ui, lang = get_texts(lang)
    payload = _load_meta(rid)
    if not payload:
        return templates.TemplateResponse(
            "index.html",
            _build_index_context(
                request,
                lang,
                error_message=ui.get("results_unavailable", "Los resultados ya no están disponibles."),
            ),
        )

    payload = _localize_habla_libre_payload(payload, ui)
    payload["request"] = request
    payload["ui"] = ui
    payload["lang"] = lang
    payload["lang_switch_url"] = f"/clinica/results/{rid}"
    return templates.TemplateResponse("results.html", payload)


@router.post("/analyze", response_class=HTMLResponse)
async def analyze(
    request: Request,
    audio: UploadFile = File(...),
    lang: str = Form(DEFAULT_LANG),
    task: str = Form("pataka"),
    age: int = Form(...),
    gender: str | None = Form(None),
    gender_specify: str | None = Form(None),
    browser_metadata_json: str | None = Form(None),
    consent_science: str = Form(...),
):
    ui, lang = get_texts(lang)
    store_data = consent_science.strip().lower() == "yes"

    if task not in TASKS:
        return HTMLResponse(f"<h1>Tarea desconocida: {task}</h1>", status_code=400)

    task_cfg = TASKS[task]
    pipeline = _infer_pipeline(task, task_cfg)

    original_path = wav_path = csv_path = textgrid_path = lemmas_json_path = None
    stem = None

    reference_text = ""

    try:
        suffix = Path(audio.filename).suffix.lower() if audio.filename else ".wav"
        if not suffix:
            suffix = ".wav"

        date_tag = datetime.now().strftime("%Y%m%d")
        final_gender = _final_gender_value(gender, gender_specify)
        mic_token = _browser_metadata_token(browser_metadata_json)

        stem = (
            f"{uuid.uuid4().hex}"
            f"_d{date_tag}"
            f"_task{_safe_filename_token(task)}"
            f"_age{age}"
            f"_gender{_safe_filename_token(final_gender)}"
            f"_{mic_token}"
        )

        # Guardamos el archivo original con sufijo _input para evitar que choque con el WAV limpio.
        original_path = UPLOAD_DIR / f"{stem}_input{suffix}"

        with original_path.open("wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)

        # Este nombre debe ser EXACTAMENTE stem.wav porque algunos scripts generan
        # archivos intermedios usando wav_path.stem.
        wav_path = UPLOAD_DIR / f"{stem}.wav"

        subprocess.run(
            [
                FFMPEG_CMD,
                "-y",
                "-i", str(original_path),
                "-vn",
                "-ac", "1",
                "-ar", "44100",
                "-acodec", "pcm_s16le",
                "-f", "wav",
                str(wav_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        if not wav_path.exists() or wav_path.stat().st_size == 0:
            return HTMLResponse("<h1>No se pudo generar un WAV válido</h1>", status_code=500)

        duration_sec, range_db = audio_duration_and_intensity_range_db(wav_path)
        if (duration_sec < MIN_DURATION_SEC) or (range_db < MIN_INTENSITY_RANGE_DB):
            safe_unlink(original_path)
            if wav_path != original_path:
                safe_unlink(wav_path)
            return templates.TemplateResponse(
                "index.html",
                _build_index_context(request, lang, task=task, error_message=ui.get("msg_audio_quality_fail", "La grabación no cumple los requisitos mínimos de calidad.")),
            )

        # El archivo _input original ya no es necesario una vez generado el WAV.
        safe_unlink(original_path)

        prune_uploads()

        csv_path = RESULTS_DIR / f"{stem}_analysis.csv"
        textgrid_path = RESULTS_DIR / f"{stem}.TextGrid"
        lemmas_json_path = RESULTS_DIR / f"{stem}_lemmas.txt"

        if pipeline == "python_r":
            py_script = _task_python_script(task_cfg, "asos_pipeline.py")
            r_script = _task_r_script(task_cfg, "analyze_asos_all.R")
            if py_script is None or r_script is None:
                return HTMLResponse("<h1>Faltan scripts para la tarea ASOS</h1>", status_code=500)

            base_prefix = RESULTS_DIR / stem

            subprocess.run(
                [PYTHON_CMD, str(py_script), "--wav", str(wav_path), "--out-dir", str(RESULTS_DIR)],
                check=True,
                capture_output=True,
                text=True,
            )

            subprocess.run(
                [RSCRIPT_CMD, str(r_script), str(base_prefix), str(csv_path)],
                check=True,
                capture_output=True,
                text=True,
            )

            # Borrar intermedios del script R que no son necesarios para la web.
            safe_unlink(RESULTS_DIR / f"{stem}_summary_long.csv")
            safe_unlink(RESULTS_DIR / f"{stem}_praatR.xlsx")

        elif pipeline == "acoustic_lectura":
            task_lang = _resolve_task_language(lang)
            reference_text = (
                task_cfg.get("reference_texts", {}).get(task_lang)
                or task_cfg.get("reference_texts", {}).get(DEFAULT_LANG, "")
            )

            prosody_script = SCRIPTS_DIR / str(task_cfg.get("prosody_script", "analyze_lectura.py"))

            if not prosody_script.exists():
                return HTMLResponse("<h1>Falta el script acústico de lectura</h1>", status_code=500)

            subprocess.run(
                [
                    PYTHON_CMD,
                    str(prosody_script),
                    "--audio", str(wav_path),
                    "--out-csv", str(csv_path),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
        
        elif pipeline == "habla_libre":
            habla_script = SCRIPTS_DIR / str(task_cfg.get("python_script", "analyze_habla_libre.py"))

            if not habla_script.exists():
                return HTMLResponse("<h1>Falta el script de habla libre</h1>", status_code=500)

            subprocess.run(
                [
                    PYTHON_CMD,
                    str(habla_script),
                    "--audio", str(wav_path),
                    "--out-csv", str(csv_path),
                    "--out-textgrid", str(textgrid_path),
                    "--out-lemmas-json", str(lemmas_json_path),
                    "--mfa-cmd", str(MFA_CMD),
                    "--language", "es",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

        else:
            praat_script = SCRIPTS_DIR / task_cfg["praat_script"]
            r_script = _task_r_script(task_cfg, "analyze_textgrid.R")

            subprocess.run(
                [PRAAT_CMD, "--run", str(praat_script), str(UPLOAD_DIR).replace("\\", "/"), wav_path.name, str(RESULTS_DIR).replace("\\", "/"), textgrid_path.name],
                check=True,
                capture_output=True,
                text=True,
            )

            subprocess.run(
                [RSCRIPT_CMD, str(r_script), str(textgrid_path), str(csv_path), task],
                check=True,
                capture_output=True,
                text=True,
            )

        if not csv_path.exists():
            return HTMLResponse("<h1>No se generó el CSV</h1>", status_code=500)

        rid = uuid.uuid4().hex
        raw_rows = _read_csv_rows_for_template(csv_path)
        row_groups: list[dict[str, Any]] = []
        hl_norms_table_name = ""

        if task == "pataka":
            robust_xlsx = SCRIPTS_DIR / "centres_sd_robustos_controls.xlsx"
            rows, interpretation_global, interpretation_comment = _build_pataka_rows(csv_path, robust_xlsx)
            f0_summary_text = ""
        elif task == "asos":
            final_gender = _final_gender_value(gender, gender_specify)
            rows, interpretation_global, interpretation_comment, f0_summary_text = _build_asos_rows(csv_path, final_gender, ui)
        elif task == "lectura":
            rows, interpretation_global, interpretation_comment = _build_lectura_rows(csv_path, ui=ui)
            f0_summary_text = ""
        elif task == "habla_libre":
            rows, interpretation_global, interpretation_comment, hl_norms_table_name = _build_habla_libre_rows(
                csv_path,
                age=age,
                gender_value=final_gender,
                ui=ui,
            )
            row_groups = _build_row_groups(rows, HABLA_LIBRE_RESULT_GROUPS, ui)
            f0_summary_text = ""
        else:
            rows, interpretation_global, interpretation_comment = _build_generic_rows(csv_path)
            f0_summary_text = ""

        csv_href, csv_name, audio_href, audio_name = _prepare_downloads(store_data, stem, task, csv_path, wav_path)
        textgrid_href = None
        textgrid_name = None
        textgrid_text = ""
        transcription_text = ""
        lemmas_href = None
        lemmas_name = None
        lemmas_json_text = ""
        lexical_complexity_label = ""

        first_raw = raw_rows[0] if raw_rows else {}

        if task == "habla_libre":
            transcription_text = first_raw.get("transcription", "")

            lexical_complexity_raw = (
                first_raw.get("lexical_complexity_label")
                or first_raw.get("lexical_mean_category")
                or first_raw.get("lexical_category")
                or ""
            )

            lexical_richness_score_raw = first_raw.get("lexical_richness_score_1_5", "")
            rare_percent_raw = first_raw.get("lexical_complexity_rare_percent", "")
            mean_freq_raw = first_raw.get("mean_datamuse_frequency_per_million", "")

        if task in {"pataka", "asos", "habla_libre"}:
            textgrid_href, textgrid_name, textgrid_text = _prepare_textgrid_download(
                store_data,
                stem,
                task,
                textgrid_path,
            )

        def _fmt_no_decimals(x: str | float | int | None) -> str:
            try:
                if x is None or x == "":
                    return ""
                return str(int(round(float(str(x).replace(",", ".")))))
            except Exception:
                return str(x)


        def _fmt_score_1_5(x: str | float | int | None) -> str:
            try:
                if x is None or x == "":
                    return ""
                v = float(str(x).replace(",", "."))
                return f"{v:.2f}".rstrip("0").rstrip(".")
            except Exception:
                return str(x)

        def _rle_color(score_raw: str | float | int | None) -> str:
            try:
                if score_raw is None or score_raw == "":
                    return "#333333"
                v = float(str(score_raw).replace(",", "."))
            except Exception:
                return "#333333"

            # 1 = rosa pálido, 5 = lila fuerte
            v = max(1.0, min(5.0, v))
            t = (v - 1.0) / 4.0

            start = (255, 214, 226)  # rosa pálido
            end = (145, 112, 235)    # lila fuerte

            r = round(start[0] + (end[0] - start[0]) * t)
            g = round(start[1] + (end[1] - start[1]) * t)
            b = round(start[2] + (end[2] - start[2]) * t)

            return f"rgb({r}, {g}, {b})"


        def _rle_bg_color(score_raw: str | float | int | None) -> str:
            try:
                if score_raw is None or score_raw == "":
                    return "rgba(255, 214, 226, 0.22)"
                v = float(str(score_raw).replace(",", "."))
            except Exception:
                return "rgba(255, 214, 226, 0.22)"

            v = max(1.0, min(5.0, v))
            t = (v - 1.0) / 4.0

            start = (255, 214, 226)
            end = (145, 112, 235)

            r = round(start[0] + (end[0] - start[0]) * t)
            g = round(start[1] + (end[1] - start[1]) * t)
            b = round(start[2] + (end[2] - start[2]) * t)

            return f"rgba({r}, {g}, {b}, 0.18)"


        lexical_complexity_label = ""
        lexical_richness_score_display = ""
        lexical_complexity_comment = ""
        lexical_complexity_method = ""
        lexical_richness_color = "#333333"
        lexical_richness_bg_color = "rgba(255, 214, 226, 0.22)"

        lemmas_href = None
        lemmas_name = None
        lemmas_json_text = ""

        if task == "habla_libre":
            lexical_complexity_label = lexical_complexity_raw or _ui_text(
                ui,
                "lexical_complexity_not_calculable",
                "no calculable",
            )

            lexical_richness_score_display = _fmt_score_1_5(lexical_richness_score_raw)
            lexical_richness_color = _rle_color(lexical_richness_score_raw)
            lexical_richness_bg_color = _rle_bg_color(lexical_richness_score_raw)

            rare_percent = _fmt_no_decimals(rare_percent_raw)
            mean_freq = _fmt_no_decimals(mean_freq_raw)

            lexical_comment_parts = []

            if rare_percent:
                lexical_comment_parts.append(
                    _ui_text(
                        ui,
                        "lexical_complexity_rare_comment",
                        "Lemes poc freqüents o molt poc freqüents: {rare_percent} %.",
                    ).format(rare_percent=rare_percent)
                )

            if mean_freq:
                lexical_comment_parts.append(
                    _ui_text(
                        ui,
                        "lexical_complexity_mean_freq_comment",
                        "Freqüència mitjana Datamuse: {mean_freq} ocurrències per milió.",
                    ).format(mean_freq=mean_freq)
                )

            lexical_complexity_comment = " ".join(lexical_comment_parts)

            lexical_complexity_method = _ui_text(
                ui,
                "lexical_complexity_method",
                (
                    "RLE significa Riquesa Lèxica Estimada. És una mesura experimental en escala 1–5: "
                    "1 indica vocabulari molt freqüent i 5 indica vocabulari menys freqüent, més marcat "
                    "o més singular. Primer s’extreuen els lemes lèxics amb Stanza. "
                    "Un valor més alt indica una singularitat lèxica estimada més gran."
                ),
            )

            lemmas_href, lemmas_name, lemmas_json_text = _prepare_txt_download(
                store_data,
                stem,
                task,
                lemmas_json_path,
                "lemas",
            )

        payload = {
            "filename": Path(audio.filename).name if audio.filename else wav_path.name,
            "task": task,
            "task_label": task_cfg["label"][lang],
            "age": age,
            "gender_value": final_gender,
            "hl_norms_table_name": hl_norms_table_name,
            "rows": rows,
            "row_groups": row_groups,
            "results": [{"measure": k, "value": v} for k, v in (raw_rows[0].items() if raw_rows else [])],
            "interpretation_global": interpretation_global,
            "interpretation_comment": interpretation_comment,
            "f0_summary_text": f0_summary_text,
            "csv_data_uri": csv_href,
            "csv_download_name": csv_name,
            "audio_download_url": audio_href,
            "audio_download_name": audio_name,
            "textgrid_download_url": textgrid_href,
            "textgrid_download_name": textgrid_name,
            "transcription_text": transcription_text,
            "textgrid_text": textgrid_text,
            "reference_text": reference_text if task == "lectura" else "",
            "lang_switch_url": f"/clinica/results/{rid}",
            "lexical_complexity_label": lexical_complexity_label,
            "lexical_complexity_comment": lexical_complexity_comment,
            "lexical_richness_color": lexical_richness_color,
            "lexical_richness_bg_color": lexical_richness_bg_color,
            "lemmas_download_url": lemmas_href,
            "lemmas_download_name": lemmas_name,
            "lemmas_json_text": lemmas_json_text,
            "lexical_richness_score_display": lexical_richness_score_display,
            "lexical_complexity_method": lexical_complexity_method,
        }

        _save_meta(rid, payload)
        if store_data:
            prune_results()

        return RedirectResponse(url=f"/clinica/results/{rid}?lang={lang}", status_code=303)

    except subprocess.CalledProcessError as e:
        error_html = "<h1>Error durante el análisis</h1>"
        error_html += "<h2>stdout</h2><pre>" + (e.stdout or "") + "</pre>"
        error_html += "<h2>stderr</h2><pre>" + (e.stderr or "") + "</pre>"
        return HTMLResponse(error_html, status_code=500)

    finally:
        if not store_data and stem:
            for p in UPLOAD_DIR.glob(f"{stem}*"):
                safe_unlink(p)
            for p in RESULTS_DIR.glob(f"{stem}*"):
                safe_unlink(p)
