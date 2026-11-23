"""DSI adaptat: fórmula i valor de referència provisional (font única de veritat).

El DSI adaptat NO és el DSI validat (Wuyts et al., 2000). És un indicador propi i provisional
del laboratori per a una sola vocal /a/ sostinguda a to còmode. L'escala original (+5 / −5,
>5 bo, <5 pobre) NO s'hi aplica: només s'interpreta davant la referència dels controls de sota.

Fórmula (equivalent a 0,13·MPT + 0,0053·F0_alta − 1,18·Jitter − 2,16):
    DSI_adaptat = 0,13·MPT + 0,0053·F0_alta − 1,18·Jitter% + 12,4 − 0,26·I_BAIXA_FIXA
- MPT = durada (s) del tram vocàlic detectat (columna `mpt` del CSV web).
- F0_alta = F0 mitjana de la vocal · 2**(6/12) (columna `f0_high_6st_hz`).
- Jitter% = jitter PPQ5 en % (columna `jitter_pct`).
- I_baixa: no es pot mesurar (cal una tasca de fonació suau); el terme se substitueix per una
  constant, la mitjana de l'estudi de referència (Hakkesteegt et al., 2006, taula 2, total:
  56 dB SPL). Així no influeix en les diferències entre persones.
"""
from __future__ import annotations

import math

# Coeficients de la fórmula original del DSI (Wuyts et al., 2000).
DSI_COEF_MPT = 0.13
DSI_COEF_F0_HIGH = 0.0053
DSI_COEF_I_LOW = -0.26
DSI_COEF_JITTER = -1.18
DSI_INTERCEPT = 12.4

# I_baixa fixada (dB SPL): mitjana de l'estudi de referència (Hakkesteegt et al., 2006).
DSI_ADAPTED_I_LOW_FIXED_DB = 56.0
# Semitons afegits a la F0 mitjana per estimar F0_alta.
DSI_ADAPTED_F0_SEMITONES = 6

DSI_ADAPTED_METHOD = "adapted_v1"

# Referència PROVISIONAL derivada dels controls sans propis (vegeu
# scripts/compute_dsi_adapted_reference.py, que l'ha generada a partir de
# ASOS/controls/asos_dsi_controls60.csv).
# - 8 enregistraments de controls sans de 60 anys, sexe desconegut (els noms dels fitxers
#   suggereixen uns 5 parlants, no verificat: no s'ha d'afirmar cap nombre de parlants).
# - mean/sd: mitjana i desviació estàndard MOSTRAL (ddof=1) del DSI adaptat dels 8 enregistraments.
# - min/max: mitjana ± 2·SD (coherent amb `_severity_from_z`, que tracta el rang com ±2 SD).
# - No s'usa edat ni sexe: una única referència per a tots els usuaris.
# CAL ACTUALITZAR-LA quan hi hagi més controls (més parlants, edats i ambdós sexes).
DSI_ADAPTED_REFERENCE = {
    "mean": 1.0250,
    "sd": 0.7202,
    "min": -0.4155,
    "max": 2.4654,
    "n_recordings": 8,
    "age": 60,
}


def compute_dsi_adapted(mpt, f0_high, jitter_pct) -> float | None:
    """Calcula el DSI adaptat (sense arrodonir) o None si falta alguna entrada o no és finita."""
    vals = []
    for v in (mpt, f0_high, jitter_pct):
        try:
            f = float(v)
        except (TypeError, ValueError):
            return None
        if not math.isfinite(f):
            return None
        vals.append(f)
    m, f0h, jit = vals
    return (
        DSI_COEF_MPT * m
        + DSI_COEF_F0_HIGH * f0h
        + DSI_COEF_JITTER * jit
        + DSI_INTERCEPT
        + DSI_COEF_I_LOW * DSI_ADAPTED_I_LOW_FIXED_DB
    )
