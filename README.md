# AcousA

Web application for the acoustic analysis of speech recordings, developed at the Laboratori de Fonètica (Universitat de Barcelona). Users record or upload a short speech task and get acoustic measures placed against reference values, with explanations in Catalan, Spanish and English.

This project is funded by MCIN/AEI, reference PID2022-139004OA-I00.

## Tasks

| Task | What it measures |
|---|---|
| `asos` | Voice quality from a sustained /a/ (MPT, F0, jitter, shimmer, HNR, CPPS, H1–H2, H1–A1, voice breaks) and a provisional adapted DSI |
| `pataka` | Articulation rate (diadochokinesis) |
| `lectura` | Reading |
| `habla_libre` | Free speech (automatic transcription, speech measures and lexical richness) |

### Adapted DSI (ASOS)

The Dysphonia Severity Index (Wuyts et al., 2000) cannot be computed from a single sustained /a/, so the ASOS task reports a **provisional, adapted index**. It is not the validated DSI and its values are not comparable with published DSI scales or norms.

`adapted DSI = 0.13·MPT + 0.0053·F0_high − 1.18·Jitter − 2.16`

- `F0_high` is estimated as the mean F0 of the vowel plus 6 semitones.
- The lowest-intensity term is replaced by a constant (56 dB).
- Jitter is PPQ5, in percent.
- The reference range (mean ± 2 SD) comes from the lab's own healthy controls aged 60 (8 recordings from 5 people). It is provisional and will be updated as more controls are recorded.

The constants live in `core/dsi_adapted.py` and can be recomputed with `scripts/compute_dsi_adapted_reference.py`.

## Requirements

- Python 3.11 or later and the packages in `requirements.txt`.
- [Praat](https://www.fon.hum.uva.nl/praat/) available as a command (`PRAAT_CMD`).
- R with `tidyverse`, `openxlsx`, `janitor` and `readtextgrid` (`RSCRIPT_CMD`).
- For free speech: Montreal Forced Aligner (`MFA_CMD`) and Stanza resources (`STANZA_RESOURCES_DIR`).

## Running

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Recordings and analysis results are stored under `uploads/` and `results/`, which are not part of the repository.

## License

GNU General Public License v3.0. See [LICENSE](LICENSE).
