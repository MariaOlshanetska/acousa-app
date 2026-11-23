#!/usr/bin/env python3
"""Calcula la referència provisional del DSI adaptat a partir dels controls.

Ús (des de l'arrel del repo):
    .venv/bin/python scripts/compute_dsi_adapted_reference.py [ruta_csv]

Llegeix ASOS/controls/asos_dsi_controls60.csv (columnes mpt_s, jitter_pct, f0_high_6st_hz),
calcula el DSI adaptat de cada enregistrament amb la fórmula de core/dsi_adapted.py i imprimeix
la mitjana, la SD mostral (ddof=1) i el rang mitjana ± 2·SD, llestos per enganxar a
`DSI_ADAPTED_REFERENCE`.
"""
from __future__ import annotations

import csv
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.dsi_adapted import compute_dsi_adapted  # noqa: E402

DEFAULT_CSV = ROOT / "ASOS" / "controls" / "asos_dsi_controls60.csv"


def compute_reference(csv_path: Path = DEFAULT_CSV) -> dict:
    """Retorna {mean, sd, min, max, n_recordings, values} sense arrodonir."""
    values = []
    with open(csv_path, newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            v = compute_dsi_adapted(row["mpt_s"], row["f0_high_6st_hz"], row["jitter_pct"])
            if v is not None:
                values.append(v)
    mean = statistics.fmean(values)
    sd = statistics.stdev(values)  # SD mostral (ddof=1)
    return {
        "mean": mean,
        "sd": sd,
        "min": mean - 2 * sd,
        "max": mean + 2 * sd,
        "n_recordings": len(values),
        "values": values,
    }


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_CSV
    ref = compute_reference(path)
    print("DSI adaptat per enregistrament:", [round(v, 3) for v in ref["values"]])
    print("DSI_ADAPTED_REFERENCE = {")
    for k in ("mean", "sd", "min", "max"):
        print(f'    "{k}": {ref[k]:.4f},')
    print(f'    "n_recordings": {ref["n_recordings"]},')
    print('    "age": 60,')
    print("}")


if __name__ == "__main__":
    main()
