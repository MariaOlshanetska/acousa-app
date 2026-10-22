#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
integrated_voice_quality_pipeline.py

Single pipeline:
1) Reads a WAV, converts it to mono and detects a continuous voice segment.
   Creates a TextGrid with a single tier and a single labeled interval (segment of interest).
2) Extracts that segment from the sound and generates/saves Praat objects:
     <basename>.Pitch, <basename>.PointProcess, <basename>.Intensity, <basename>.Harmonicity
3) Extracts voice quality measures from the segment (one row) and saves them to TSV.
4) (NEW) Integrates the export_H1_A1_inputs.praat flow:
   - Midpoint F0, F1-F4 and B1-B4 (over the whole sound, more stable)
   - Robust means F1-F4 and B1-B4 within the interval
   - Target frequencies: H1 (=F0), A1..A4 (=harmonic closest to F1..F4)
   - Saves:
       <basename>.Spectrum (short-window FFT at the midpoint, text)
       <basename>.PowerCepstrum (text)
       <basename>.LPCSpectrum (slice of an LPC over a longer window, text)

Dependencies:
  pip install praat-parselmouth numpy
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Dict, Tuple, List

import numpy as np
import parselmouth
from parselmouth.praat import call
from parselmouth import PraatError


# ------------------------- generic helpers -------------------------
def safe_float(x) -> float:
    try:
        v = float(x)
        return v if math.isfinite(v) else float("nan")
    except Exception:
        return float("nan")


def fmt(x: float) -> str:
    return f"{x:.6f}" if isinstance(x, (int, float)) and math.isfinite(float(x)) else "nan"


def save_text_praat_object(obj, out_path: Path) -> None:
    out_path = Path(out_path)
    for cmd in ("Save as text file", "Save as text file...", "Write to text file", "Write to text file..."):
        try:
            call(obj, cmd, str(out_path))
            return
        except Exception:
            pass
    raise RuntimeError(f"Could not save the object to {out_path}")


# ------------------------- robust Praat wrappers (version-proof) -------------------------
def to_pitch_ac(sound: parselmouth.Sound, time_step: float, floor: float, ceiling: float):
    try:
        return call(sound, "To Pitch (ac)", time_step, floor, ceiling)
    except Exception:
        pass
    try:
        return call(
            sound,
            "To Pitch (raw autocorrelation)",
            time_step,
            floor,
            ceiling,
            15,
            "no",
            0.03,
            0.45,
            0.01,
            0.35,
            0.14,
        )
    except Exception:
        pass
    return call(sound, "To Pitch", time_step, floor, ceiling)


def _normalize_pitch_approach(approach: str) -> str:
    a = (approach or "").strip().lower()
    a = a.replace("_", " ")
    a = " ".join(a.split())
    if a in {"raw ac", "raw autocorrelation", "raw autocorrelation (ac)", "raw"}:
        return "raw ac"
    if a in {"raw cc", "raw cross correlation", "raw cross-correlation"}:
        return "raw cc"
    if a in {"ac"}:
        return "ac"
    if a in {"cc"}:
        return "cc"
    return a


def to_pitch_by_choice(sound: parselmouth.Sound, approach: str, floor: float, ceiling: float):
    approach = _normalize_pitch_approach(approach)
    raw_args = (0.0, floor, ceiling, 15, "no", 0.03, 0.45, 0.01, 0.35, 0.14)

    def _try(cmds, args):
        for cmd in cmds:
            try:
                return call(sound, cmd, *args)
            except Exception:
                pass
        return None

    if approach == "raw ac":
        pitch = _try(
            [
                "To Pitch (raw autocorrelation)...",
                "To Pitch (raw autocorrelation)",
                "To Pitch (raw ac)...",
                "To Pitch (raw ac)",
            ],
            raw_args,
        )
        if pitch is not None:
            return pitch
        try:
            return call(sound, "To Pitch (ac)", 0.0, floor, ceiling)
        except Exception:
            return call(sound, "To Pitch", 0.0, floor, ceiling)

    if approach == "ac":
        return call(sound, "To Pitch (ac)", 0.0, floor, ceiling)

    if approach == "cc":
        return call(sound, "To Pitch (cc)", 0.0, floor, ceiling)

    pitch = _try(
        [
            "To Pitch (raw cross-correlation)...",
            "To Pitch (raw cross-correlation)",
            "To Pitch (raw cc)...",
            "To Pitch (raw cc)",
        ],
        raw_args,
    )
    if pitch is not None:
        return pitch

    try:
        return call(sound, "To Pitch (cc)", 0.0, floor, ceiling)
    except Exception:
        return call(sound, "To Pitch", 0.0, floor, ceiling)



def to_intensity_robust(sound: parselmouth.Sound, time_step: float, minimum_pitch: float, subtract_mean: str = "yes"):
    min_pitch = max(float(minimum_pitch), 50.0)
    ts = float(time_step)
    candidates = [
        ("To Intensity", (ts, min_pitch, subtract_mean)),
        ("To Intensity", (min_pitch, ts, subtract_mean)),
        ("To Intensity", (0.0, min_pitch, subtract_mean)),
        ("To Intensity", (min_pitch, 0.0, subtract_mean)),
        ("To Intensity...", (ts, min_pitch, subtract_mean)),
        ("To Intensity...", (min_pitch, ts, subtract_mean)),
        ("To Intensity...", (0.0, min_pitch, subtract_mean)),
        ("To Intensity...", (min_pitch, 0.0, subtract_mean)),
    ]
    last_err = None
    for cmd, args in candidates:
        try:
            return call(sound, cmd, *args)
        except Exception as e:
            last_err = e
    raise last_err


def extract_part(sound: parselmouth.Sound, start: float, end: float) -> parselmouth.Sound:
    try:
        return sound.extract_part(from_time=start, to_time=end, preserve_times=False)
    except Exception:
        return call(sound, "Extract part", start, end, "rectangular", 1.0, False)


# ------------------------- step 1: detect + create TextGrid -------------------------
def detect_voiced_region(
    sound: parselmouth.Sound,
    time_step: float = 0.01,
    f0_floor: float = 50.0,
    f0_ceiling: float = 500.0,
    intensity_drop_db: float = 30.0,
    min_duration: float = 0.20,          # technical minimum to consider a candidate
    preferred_duration: float = 3.0,     # actual target
    onset_pad: float = 0.02,
    offset_pad: float = 0.00,
    min_run_frames: int = 4,
    silence_drop_db: float = 38.0,
    end_silence_frames: int = 12,
):
    duration = float(call(sound, "Get total duration"))

    intensity = to_intensity_robust(
        sound,
        time_step=float(time_step),
        minimum_pitch=float(f0_floor),
        subtract_mean="yes",
    )
    inten = np.asarray(intensity.values[0], dtype=float)
    t = np.asarray(intensity.xs(), dtype=float)

    try:
        call(intensity, "Remove")
    except Exception:
        pass

    if len(inten) == 0 or not np.isfinite(inten).any():
        return 0.0, duration

    win = 5
    kernel = np.ones(win) / win
    inten_s = np.convolve(np.nan_to_num(inten, nan=np.nanmin(inten)), kernel, mode="same")

    peak_db = float(np.nanmax(inten_s))
    thr_on = peak_db - float(intensity_drop_db)
    thr_off = peak_db - float(silence_drop_db)

    pitch = to_pitch_by_choice(sound, "raw ac", f0_floor, f0_ceiling)
    f0 = np.asarray(pitch.selected_array["frequency"], dtype=float)
    tp = np.asarray(pitch.xs(), dtype=float)

    voiced_pitch = np.isfinite(f0) & (f0 > 0)

    if len(tp) > 1:
        voiced = np.interp(t, tp, voiced_pitch.astype(float), left=0.0, right=0.0) > 0.5
    else:
        voiced = np.zeros_like(t, dtype=bool)

    try:
        call(pitch, "Remove")
    except Exception:
        pass

    active_on = np.isfinite(inten_s) & (inten_s >= thr_on) & voiced
    silent_off = (~voiced) | (np.isfinite(inten_s) & (inten_s < thr_off))

    if not active_on.any():
        return 0.0, duration

    idx = np.where(active_on)[0]
    cuts = np.where(np.diff(idx) > 1)[0]
    starts = np.r_[idx[0], idx[cuts + 1]]
    ends = np.r_[idx[cuts], idx[-1]]

    candidates = []

    for s, e in zip(starts, ends):
        s = int(s)
        e = int(e)

        if (e - s + 1) < min_run_frames:
            continue

        silence_count = 0
        candidate_end = len(t) - 1

        for i in range(s, len(t)):
            if silent_off[i]:
                silence_count += 1
                if silence_count >= end_silence_frames:
                    candidate_end = i - end_silence_frames
                    break
            else:
                silence_count = 0

        start_t = max(0.0, float(t[s] - time_step / 2.0 - onset_pad))
        end_t = min(duration, float(t[candidate_end] + time_step / 2.0 + offset_pad))
        dur = end_t - start_t

        if dur >= float(min_duration):
            candidates.append((start_t, end_t, dur))

    if not candidates:
        return 0.0, duration

    # 1) prefer candidates >= 3 s
    preferred = [c for c in candidates if c[2] >= preferred_duration]
    if preferred:
        best = max(preferred, key=lambda x: x[2])
        return best[0], best[1]

    # 2) if none reach 3 s, return the longest one
    best = max(candidates, key=lambda x: x[2])
    return best[0], best[1]



def create_textgrid_single_tier(duration: float, start_t: float, end_t: float, tier_name: str, label: str):
    duration = float(duration)
    start_t = float(start_t)
    end_t = float(end_t)

    tg = None
    last_err = None

    for cmd in ("Create TextGrid", "Create TextGrid..."):
        try:
            tg = call(cmd, 0.0, duration, str(tier_name), "")
            break
        except Exception as e:
            last_err = e

    if tg is None:
        for cmd in ("Create TextGrid", "Create TextGrid..."):
            try:
                tg = call(cmd, "auto", 0.0, duration, str(tier_name), "")
                break
            except Exception as e:
                last_err = e

    if tg is None:
        raise last_err

    tier = 1

    def insert_boundary(t: float):
        for cmd in ("Insert boundary", "Insert boundary..."):
            try:
                call(tg, cmd, tier, float(t))
                return
            except Exception:
                pass
        call(tg, "Insert boundary", tier, float(t))

    if start_t > 0.0:
        insert_boundary(start_t)
    if end_t < duration:
        insert_boundary(end_t)

    if start_t <= 0.0 and end_t < duration:
        mid_idx = 1
    elif start_t > 0.0 and end_t >= duration:
        mid_idx = 2
    elif start_t > 0.0 and end_t < duration:
        mid_idx = 2
    else:
        mid_idx = 1

    for cmd in ("Set interval text", "Set interval text..."):
        try:
            call(tg, cmd, tier, int(mid_idx), str(label))
            break
        except Exception:
            pass
    else:
        call(tg, "Set interval text", tier, int(mid_idx), str(label))

    return tg


def write_textgrid(tg, out_path: Path):
    out_path = Path(out_path)
    try:
        call(tg, "Write to text file", str(out_path))
    except Exception:
        call(tg, "Write to text file...", str(out_path))


# ------------------------- spectrum helper -------------------------
def spectrum_max_in_band_db(spectrum, f_center: float, tol_hz: float) -> float:
    f_lo = max(0.0, float(f_center) - float(tol_hz))
    f_hi = float(f_center) + float(tol_hz)

    b_lo = int(round(float(call(spectrum, "Get bin number from frequency", f_lo))))
    b_hi = int(round(float(call(spectrum, "Get bin number from frequency", f_hi))))
    n_bins = int(call(spectrum, "Get number of bins"))

    b_lo = max(1, b_lo)
    b_hi = min(n_bins, b_hi)

    max_db = float("nan")
    for b in range(b_lo, b_hi + 1):
        re = float(call(spectrum, "Get real value in bin", b))
        im = float(call(spectrum, "Get imaginary value in bin", b))
        amp = math.sqrt(re * re + im * im)
        if amp > 0.0:
            db = 20.0 * math.log10(amp)
            if (not math.isfinite(max_db)) or (db > max_db):
                max_db = db
    return max_db


# ------------------------- Praat-like summary features (from export_H1_A1_inputs.praat) -------------------------
def _get_spectrum_from_sound(sound_piece):
    # Praat: "To Spectrum" (sometimes with arg "yes" / "no")
    try:
        return call(sound_piece, "To Spectrum")
    except Exception:
        return call(sound_piece, "To Spectrum", "yes")


def compute_praatstyle_mid_and_means(
    sound_whole: parselmouth.Sound,
    seg_start: float,
    seg_end: float,
    pitch_approach: str,
    pitch_floor: float,
    pitch_ceiling: float,
    num_formants: int,
    formant_ceiling: float,
    formant_window: float,
    formant_preemph: float,
    mean_step_seconds: float,
    mean_min_frames: int,
    intensity_floor_hz: float,
) -> Dict[str, float]:
    """
    Replicates (for 1 interval) the part that computes:
      - Pitch and Formant over the whole sound
      - values at the midpoint (F0, F1..F4 and B1..B4)
      - robust means within the interval (F1..F4 and B1..B4)
      - intensity: mid and mean
      - target freq: H1, A1..A4
    """
    out: Dict[str, float] = {}

    tmid = (float(seg_start) + float(seg_end)) / 2.0
    out["t_start"] = float(seg_start)
    out["t_end"] = float(seg_end)
    out["t_mid"] = float(tmid)

    # Pitch & Formant over the whole sound (as in the Praat script)
    pitch = to_pitch_by_choice(sound_whole, pitch_approach, pitch_floor, pitch_ceiling)
    formant = call(
        sound_whole, "To Formant (burg)",
        0.0, int(num_formants), float(formant_ceiling), float(formant_window), float(formant_preemph)
    )

    # Intensity over the whole sound
    intensity = to_intensity_robust(sound_whole, time_step=0.0, minimum_pitch=float(intensity_floor_hz), subtract_mean="yes")

    # Midpoint F0
    f0_mid = safe_float(call(pitch, "Get value at time", tmid, "Hertz", "Linear"))
    out["f0_mid_hz"] = f0_mid

    # Midpoint formants + bandwidths
    f_mid = {}
    b_mid = {}
    for i, key in [(1, "f1_mid_hz"), (2, "f2_mid_hz"), (3, "f3_mid_hz"), (4, "f4_mid_hz")]:
        f_mid[key] = safe_float(call(formant, "Get value at time", i, tmid, "Hertz", "Linear"))
        out[key] = f_mid[key]

    for i, key in [(1, "b1_mid_hz"), (2, "b2_mid_hz"), (3, "b3_mid_hz"), (4, "b4_mid_hz")]:
        b_mid[key] = safe_float(call(formant, "Get bandwidth at time", i, tmid, "Hertz", "Linear"))
        out[key] = b_mid[key]

    # Robust means (F1-F4, B1-B4) within the interval
    dt = float(mean_step_seconds)
    sumF = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0}
    sumB = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0}
    n_frames = 0

    t = float(seg_start)
    while t <= float(seg_end) + 1e-12:
        f1t = safe_float(call(formant, "Get value at time", 1, t, "Hertz", "Linear"))
        f2t = safe_float(call(formant, "Get value at time", 2, t, "Hertz", "Linear"))
        f3t = safe_float(call(formant, "Get value at time", 3, t, "Hertz", "Linear"))
        f4t = safe_float(call(formant, "Get value at time", 4, t, "Hertz", "Linear"))

        if all(math.isfinite(x) for x in (f1t, f2t, f3t, f4t)):
            n_frames += 1
            sumF[1] += f1t
            sumF[2] += f2t
            sumF[3] += f3t
            sumF[4] += f4t

            # bandwidths can be undefined; only add if defined
            for j in (1, 2, 3, 4):
                bt = safe_float(call(formant, "Get bandwidth at time", j, t, "Hertz", "Linear"))
                if math.isfinite(bt):
                    sumB[j] += bt

        t += dt

    if n_frames >= int(mean_min_frames):
        out["f1_mean_hz_praatstyle"] = sumF[1] / n_frames
        out["f2_mean_hz_praatstyle"] = sumF[2] / n_frames
        out["f3_mean_hz_praatstyle"] = sumF[3] / n_frames
        out["f4_mean_hz_praatstyle"] = sumF[4] / n_frames
        # as in the Praat script: also divide by n_frames
        out["b1_mean_hz_praatstyle"] = sumB[1] / n_frames
        out["b2_mean_hz_praatstyle"] = sumB[2] / n_frames
        out["b3_mean_hz_praatstyle"] = sumB[3] / n_frames
        out["b4_mean_hz_praatstyle"] = sumB[4] / n_frames
    else:
        for k in [
            "f1_mean_hz_praatstyle", "f2_mean_hz_praatstyle", "f3_mean_hz_praatstyle", "f4_mean_hz_praatstyle",
            "b1_mean_hz_praatstyle", "b2_mean_hz_praatstyle", "b3_mean_hz_praatstyle", "b4_mean_hz_praatstyle",
        ]:
            out[k] = float("nan")

    # Intensity: mid + mean (energy)
    out["int_mid_db_praatstyle"] = safe_float(call(intensity, "Get value at time", tmid, "cubic"))
    out["int_mean_db_praatstyle"] = safe_float(call(intensity, "Get mean", float(seg_start), float(seg_end), "energy"))

    # Harmonic target frequencies: H1 (=F0) and A1..A4 (harmonic closest to the formants)
    out["h1_freq_hz_target"] = f0_mid
    if math.isfinite(f0_mid) and f0_mid > 0:
        for fk, outk in [
            (out["f1_mid_hz"], "a1_freq_hz_target"),
            (out["f2_mid_hz"], "a2_freq_hz_target"),
            (out["f3_mid_hz"], "a3_freq_hz_target"),
            (out["f4_mid_hz"], "a4_freq_hz_target"),
        ]:
            if math.isfinite(fk) and fk > 0:
                out[outk] = round(fk / f0_mid) * f0_mid
            else:
                out[outk] = float("nan")
    else:
        out["a1_freq_hz_target"] = float("nan")
        out["a2_freq_hz_target"] = float("nan")
        out["a3_freq_hz_target"] = float("nan")
        out["a4_freq_hz_target"] = float("nan")

    # cleanup
    for obj in (intensity, formant, pitch):
        try:
            call(obj, "Remove")
        except Exception:
            pass

    return out


def save_midpoint_fft_and_related(
    sound_whole: parselmouth.Sound,
    t_mid: float,
    out_dir: Path,
    basename: str,
    fft_window_seconds: float,
    lpc_extract_seconds: float,
    lpc_order: int,
    lpc_window: float,
    lpc_timestep: float,
    lpc_preemph: float,
    lpc_slice_bandwidth: float,
    lpc_slice_from_hz: float,
    lpc_slice_to_hz: float,
) -> Dict[str, str]:
    """
    Saves:
      - <basename>.Spectrum (FFT around t_mid, short window)
      - <basename>.PowerCepstrum
      - <basename>.LPCSpectrum (slice of an LPC over a longer window)
    """
    meta: Dict[str, str] = {}

    duration = float(call(sound_whole, "Get total duration"))
    tmin = 0.0
    tmax = duration

    # FFT window
    w = float(fft_window_seconds)
    half = w / 2.0
    s1 = t_mid - half
    s2 = t_mid + half
    if s1 < tmin:
        s1 = tmin
        s2 = min(tmax, s1 + w)
    if s2 > tmax:
        s2 = tmax
        s1 = max(tmin, s2 - w)

    piece = extract_part(sound_whole, s1, s2)
    spec = _get_spectrum_from_sound(piece)

    # Save Spectrum: analyze_asos_all.R requires it.
    spectrum_path = out_dir / f"{basename}.Spectrum"
    save_text_praat_object(spec, spectrum_path)
    meta["spectrum_text"] = str(spectrum_path)

    # Save PowerCepstrum.
    try:
        cep = call(spec, "To PowerCepstrum")

        powercepstrum_path = out_dir / f"{basename}.PowerCepstrum"
        save_text_praat_object(cep, powercepstrum_path)
        meta["powercepstrum_text"] = str(powercepstrum_path)

        try:
            call(cep, "Remove")
        except Exception:
            pass
    except Exception:
        meta["powercepstrum_text"] = ""

    # LPC longer window + Spectrum slice
    wL = float(lpc_extract_seconds)
    halfL = wL / 2.0
    s1L = t_mid - halfL
    s2L = t_mid + halfL
    if s1L < tmin:
        s1L = tmin
        s2L = min(tmax, s1L + wL)
    if s2L > tmax:
        s2L = tmax
        s1L = max(tmin, s2L - wL)

    piece_lpc = extract_part(sound_whole, s1L, s2L)

    lpc = call(piece_lpc, "To LPC (autocorrelation)", int(lpc_order), float(lpc_window), float(lpc_timestep), float(lpc_preemph))

    # t_mid within the local window
    lpc_mid = wL / 2.0

    lpc_spec = None
    # Praat signatures can vary; try options compatible with your script (20 0 50)
    candidates = [
        ("To Spectrum (slice)", (lpc_mid, float(lpc_slice_bandwidth), float(lpc_slice_from_hz), float(lpc_slice_to_hz))),
        ("To Spectrum (slice)...", (lpc_mid, float(lpc_slice_bandwidth), float(lpc_slice_from_hz), float(lpc_slice_to_hz))),
        ("To Spectrum (slice)", (lpc_mid, float(lpc_slice_from_hz), float(lpc_slice_to_hz), float(lpc_slice_bandwidth))),
        ("To Spectrum (slice)...", (lpc_mid, float(lpc_slice_from_hz), float(lpc_slice_to_hz), float(lpc_slice_bandwidth))),
    ]
    last_err = None
    for cmd, args in candidates:
        try:
            lpc_spec = call(lpc, cmd, *args)
            break
        except Exception as e:
            last_err = e

    if lpc_spec is not None:
        lpc_spectrum_path = out_dir / f"{basename}.LPCSpectrum"
        save_text_praat_object(lpc_spec, lpc_spectrum_path)
        meta["lpc_spectrum_text"] = str(lpc_spectrum_path)

        try:
            call(lpc_spec, "Remove")
        except Exception:
            pass
    else:
        meta["lpc_spectrum_text"] = ""
        print(
            f"[ASOS] Warning: could not generate LPCSpectrum: {last_err}",
            flush=True,
        )

    # cleanup
    for obj in (lpc, piece_lpc, spec, piece):
        try:
            call(obj, "Remove")
        except Exception:
            pass

    return meta


# ------------------------- step 3: voice quality measures -------------------------
def measure_segment_vq(
    seg: parselmouth.Sound,
    pitch_floor: float = 75.0,
    pitch_ceiling: float = 600.0,
    pointprocess_ceiling: float = 500.0,
    formant_max: float = 5500.0,
    formant_n: int = 5,
    formant_window: float = 0.025,
    formant_preemph: float = 50.0,
) -> Dict[str, float]:
    out: Dict[str, float] = {}

    # Pitch summary + fraction of locally unvoiced frames
    try:
        pitch = call(seg, "To Pitch", 0.0, pitch_floor, pitch_ceiling)
        out["f0_min_hz"] = safe_float(call(pitch, "Get minimum", 0, 0, "Hertz", "Parabolic"))
        out["f0_max_hz"] = safe_float(call(pitch, "Get maximum", 0, 0, "Hertz", "Parabolic"))
        out["f0_mean_hz"] = safe_float(call(pitch, "Get mean", 0, 0, "Hertz"))
        out["f0_sd_hz"] = safe_float(call(pitch, "Get standard deviation", 0, 0, "Hertz"))
    except PraatError:
        out.update({k: float("nan") for k in ["f0_min_hz", "f0_max_hz", "f0_mean_hz", "f0_sd_hz"]})
    try:
        raw_pitch = to_pitch_by_choice(seg, "raw ac", pitch_floor, pitch_ceiling)
        raw_f0 = np.asarray(raw_pitch.selected_array["frequency"], dtype=float)
        if raw_f0.size > 0:
            locally_unvoiced = (~np.isfinite(raw_f0)) | (raw_f0 <= 0)
            out["locally_unvoiced_percent"] = float(locally_unvoiced.mean() * 100.0)
        else:
            out["locally_unvoiced_percent"] = float("nan")
        try:
            call(raw_pitch, "Remove")
        except Exception:
            pass
    except Exception:
        out["locally_unvoiced_percent"] = float("nan")

    # HNR
    try:
        harmonicity = call(seg, "To Harmonicity (cc)", 0.01, pitch_floor, 0.1, 1.0)
        out["hnr_mean_db"] = safe_float(call(harmonicity, "Get mean", 0, 0))
    except PraatError:
        out["hnr_mean_db"] = float("nan")

        # Jitter + Shimmer + voice breaks
    try:
        pp = call(seg, "To PointProcess (periodic, cc)", pitch_floor, pointprocess_ceiling)

        out["jitter_local"] = safe_float(call(pp, "Get jitter (local)", 0, 0, 0.0001, 0.02, 1.3))
        out["jitter_local_abs"] = safe_float(call(pp, "Get jitter (local, absolute)", 0, 0, 0.0001, 0.02, 1.3))
        out["jitter_rap"] = safe_float(call(pp, "Get jitter (rap)", 0, 0, 0.0001, 0.02, 1.3))
        out["jitter_ppq5"] = safe_float(call(pp, "Get jitter (ppq5)", 0, 0, 0.0001, 0.02, 1.3))
        out["jitter_ddp"] = safe_float(call(pp, "Get jitter (ddp)", 0, 0, 0.0001, 0.02, 1.3))

        out["shimmer_local"] = safe_float(call([seg, pp], "Get shimmer (local)", 0, 0, 0.0001, 0.02, 1.3, 1.6))
        out["shimmer_local_db"] = safe_float(call([seg, pp], "Get shimmer (local_dB)", 0, 0, 0.0001, 0.02, 1.3, 1.6))
        out["shimmer_apq3"] = safe_float(call([seg, pp], "Get shimmer (apq3)", 0, 0, 0.0001, 0.02, 1.3, 1.6))
        out["shimmer_apq5"] = safe_float(call([seg, pp], "Get shimmer (apq5)", 0, 0, 0.0001, 0.02, 1.3, 1.6))
        out["shimmer_apq11"] = safe_float(call([seg, pp], "Get shimmer (apq11)", 0, 0, 0.0001, 0.02, 1.3, 1.6))
        out["shimmer_dda"] = safe_float(call([seg, pp], "Get shimmer (dda)", 0, 0, 0.0001, 0.02, 1.3, 1.6))
        
        try:
            n_points = int(call(pp, "Get number of points"))
            pulse_times = np.asarray([safe_float(call(pp, "Get time from index", i)) for i in range(1, n_points + 1)], dtype=float)
            pulse_times = pulse_times[np.isfinite(pulse_times)]
            if pulse_times.size >= 2 and seg.get_total_duration() > 0:
                intervals = np.diff(pulse_times)
                break_threshold = 1.25 / float(pitch_floor)
                breaks = intervals[intervals > break_threshold]
                out["voice_breaks_count"] = float(breaks.size)
                out["voice_breaks_percent"] = float(breaks.sum() / seg.get_total_duration() * 100.0)
            else:
                out["voice_breaks_count"] = 0.0
                out["voice_breaks_percent"] = 0.0
        except Exception:
            out["voice_breaks_count"] = float("nan")
            out["voice_breaks_percent"] = float("nan")

    except PraatError:
        for k in [
            "jitter_local", "jitter_local_abs", "jitter_rap", "jitter_ppq5", "jitter_ddp",
            "shimmer_local", "shimmer_local_db", "shimmer_apq3", "shimmer_apq5", "shimmer_apq11", "shimmer_dda",
            "voice_breaks_count", "voice_breaks_percent",

        ]:
            out[k] = float("nan")

    # Formants (Burg) over the segment (apart from the "praatstyle" over the whole sound)
    try:
        formant = call(seg, "To Formant (burg)", 0.0, formant_n, formant_max, formant_window, formant_preemph)

        out["f1_mean_hz"] = safe_float(call(formant, "Get mean", 1, 0, 0, "Hertz"))
        out["f2_mean_hz"] = safe_float(call(formant, "Get mean", 2, 0, 0, "Hertz"))
        out["f3_mean_hz"] = safe_float(call(formant, "Get mean", 3, 0, 0, "Hertz"))
        out["f4_mean_hz"] = safe_float(call(formant, "Get mean", 4, 0, 0, "Hertz"))

        mid_t = seg.get_total_duration() / 2.0
        out["f1_mid_hz"] = safe_float(call(formant, "Get value at time", 1, mid_t, "Hertz", "Linear"))
        out["f2_mid_hz"] = safe_float(call(formant, "Get value at time", 2, mid_t, "Hertz", "Linear"))
        out["f3_mid_hz"] = safe_float(call(formant, "Get value at time", 3, mid_t, "Hertz", "Linear"))
        out["f4_mid_hz"] = safe_float(call(formant, "Get value at time", 4, mid_t, "Hertz", "Linear"))
    except PraatError:
        for k in [
            "f1_mean_hz", "f2_mean_hz", "f3_mean_hz", "f4_mean_hz",
            "f1_mid_hz", "f2_mid_hz", "f3_mid_hz", "f4_mid_hz"
        ]:
            out[k] = float("nan")

    return out


# ------------------------- main -------------------------
def main() -> None:
    ap = argparse.ArgumentParser()

    ap.add_argument("--wav", required=True, help="Path to .wav")
    ap.add_argument("--out-dir", default=None, help="Output folder (default: same as the wav)")
    ap.add_argument("--tier-name", default="segments", help="Name of the single TextGrid tier")
    ap.add_argument("--label", default="v", help="Label of the segment of interest within the tier")

    # Detection (step 1)
    ap.add_argument("--step", type=float, default=0.01)
    ap.add_argument("--detect-f0-floor", type=float, default=50.0)
    ap.add_argument("--detect-f0-ceiling", type=float, default=500.0)
    ap.add_argument("--intensity-drop-db", type=float, default=30.0)
    ap.add_argument("--min-duration", type=float, default=0.20)

    # Pitch/Harmonicity objects (step 2)
    ap.add_argument("--pitch-approach", choices=["raw ac", "ac", "cc", "raw cc", "raw_ac", "raw_cc"], default="raw ac")
    ap.add_argument("--harmonicity-approach", choices=["cc", "ac"], default="cc")
    ap.add_argument("--pitch-floor", type=float, default=75.0)
    ap.add_argument("--pitch-ceiling", type=float, default=600.0)

    # Voice quality (step 3)
    ap.add_argument("--pp-ceiling", type=float, default=500.0)
    ap.add_argument("--formant-max", type=float, default=5500.0)
    ap.add_argument("--formant-n", type=int, default=5)
    ap.add_argument("--formant-window", type=float, default=0.025)
    ap.add_argument("--formant-preemph", type=float, default=50.0)

    # Simple spectrum (H1/H2/H4 + 2k/5k) as before
    ap.add_argument("--hband-tol-prop-f0", type=float, default=0.06)
    ap.add_argument("--fixedband-tol-hz", type=float, default=20.0)

    # ---- NEW: "Praat export_H1_A1_inputs" parameters
    ap.add_argument("--fft-window-seconds", type=float, default=0.030)
    ap.add_argument("--mean-step-seconds", type=float, default=0.01)
    ap.add_argument("--mean-min-frames", type=int, default=3)
    ap.add_argument("--intensity-floor-hz", type=float, default=75.0)

    ap.add_argument("--lpc-order", type=int, default=16)
    ap.add_argument("--lpc-window", type=float, default=0.030)
    ap.add_argument("--lpc-timestep", type=float, default=0.030)
    ap.add_argument("--lpc-preemph", type=float, default=50.0)
    ap.add_argument("--lpc-extract-seconds", type=float, default=0.080)
    ap.add_argument("--lpc-slice-bandwidth", type=float, default=20.0)
    ap.add_argument("--lpc-slice-from-hz", type=float, default=0.0)
    ap.add_argument("--lpc-slice-to-hz", type=float, default=50.0)

    args = ap.parse_args()

    wav_path = Path(args.wav).expanduser().resolve()
    if not wav_path.exists():
        raise FileNotFoundError(wav_path)

    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else wav_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    basename = wav_path.stem
    tg_path = out_dir / f"{basename}.TextGrid"
    out_tsv = out_dir / f"{basename}.voice_quality.tsv"

    # 1) Load + mono + detect + TG
    sound = parselmouth.Sound(str(wav_path))
    sound = call(sound, "Convert to mono")
    duration = float(call(sound, "Get total duration"))

    seg_start, seg_end = detect_voiced_region(
        sound,
        time_step=0.01,
        f0_floor=75.0,
        f0_ceiling=500.0,
        intensity_drop_db=24.0,
        min_duration=0.20,
        onset_pad=0.01,
        offset_pad=0.00,
        min_run_frames=5,
        silence_drop_db=24.0,
        end_silence_frames=6,
    )

    tg = create_textgrid_single_tier(duration, seg_start, seg_end, tier_name=args.tier_name, label=args.label)
    write_textgrid(tg, tg_path)

    # Segment sound (0..dur local)
    seg = extract_part(sound, seg_start, seg_end)
    seg_dur = seg.get_total_duration()

    # 2) Praat objects for that segment
    pitch_obj = to_pitch_by_choice(seg, args.pitch_approach, args.pitch_floor, args.pitch_ceiling)
    point_process = call(pitch_obj, "To PointProcess")
    intensity_obj = to_intensity_robust(seg, time_step=0.0, minimum_pitch=100.0, subtract_mean="yes")

    if args.harmonicity_approach == "cc":
        harmonicity_obj = call(seg, "To Harmonicity (cc)", 0.01, args.pitch_floor, 0.1, 1.0)
    else:
        harmonicity_obj = call(seg, "To Harmonicity (ac)", 0.01, args.pitch_floor, 0.1, 1.0)

    # Spectral measures (H1/H2/H4 + 2k + 5k) computed on the segment
    f0_mean_for_bands = safe_float(call(pitch_obj, "Get mean", 0.0, 0.0, "Hertz"))
    spectrum_seg = call(seg, "To Spectrum", "yes")

    h1 = h2 = h4 = float("nan")
    if math.isfinite(f0_mean_for_bands) and f0_mean_for_bands > 0:
        tol_hz = float(args.hband_tol_prop_f0) * float(f0_mean_for_bands)
        h1 = spectrum_max_in_band_db(spectrum_seg, 1.0 * f0_mean_for_bands, tol_hz)
        h2 = spectrum_max_in_band_db(spectrum_seg, 2.0 * f0_mean_for_bands, tol_hz)
        h4 = spectrum_max_in_band_db(spectrum_seg, 4.0 * f0_mean_for_bands, tol_hz)

    a2k = spectrum_max_in_band_db(spectrum_seg, 2000.0, float(args.fixedband_tol_hz))
    a5k = spectrum_max_in_band_db(spectrum_seg, 5000.0, float(args.fixedband_tol_hz))

    # 3) Voice quality measures (pitch/hnr/jitter/shimmer/formants)
    vq = measure_segment_vq(
        seg,
        pitch_floor=args.pitch_floor,
        pitch_ceiling=args.pitch_ceiling,
        pointprocess_ceiling=args.pp_ceiling,
        formant_max=args.formant_max,
        formant_n=args.formant_n,
        formant_window=args.formant_window,
        formant_preemph=args.formant_preemph,
    )

    # 4) Praat-export-like values on whole sound + save FFT/LPC/Cepstrum files
    praatstyle = compute_praatstyle_mid_and_means(
        sound_whole=sound,
        seg_start=seg_start,
        seg_end=seg_end,
        pitch_approach=args.pitch_approach,
        pitch_floor=args.pitch_floor,
        pitch_ceiling=args.pitch_ceiling,
        num_formants=args.formant_n,
        formant_ceiling=args.formant_max,
        formant_window=args.formant_window,
        formant_preemph=args.formant_preemph,
        mean_step_seconds=args.mean_step_seconds,
        mean_min_frames=args.mean_min_frames,
        intensity_floor_hz=args.intensity_floor_hz,
    )

    saved_extra = save_midpoint_fft_and_related(
        sound_whole=sound,
        t_mid=praatstyle["t_mid"],
        out_dir=out_dir,
        basename=basename,
        fft_window_seconds=args.fft_window_seconds,
        lpc_extract_seconds=args.lpc_extract_seconds,
        lpc_order=args.lpc_order,
        lpc_window=args.lpc_window,
        lpc_timestep=args.lpc_timestep,
        lpc_preemph=args.lpc_preemph,
        lpc_slice_bandwidth=args.lpc_slice_bandwidth,
        lpc_slice_from_hz=args.lpc_slice_from_hz,
        lpc_slice_to_hz=args.lpc_slice_to_hz,
    )

    # Merge + add metadata
    row: Dict[str, float | str] = {
        "wav": str(wav_path),
        "textgrid": str(tg_path),
        "tier_name": str(args.tier_name),
        "label": str(args.label),

        "xmin_abs": float(seg_start),
        "xmax_abs": float(seg_end),
        "dur_abs": float(seg_end - seg_start),
        "dur_local": float(seg_dur),

        "h1_db": float(h1),
        "h2_db": float(h2),
        "h4_db": float(h4),
        "a2k_db": float(a2k),
        "a5k_db": float(a5k),

        # Extra "praat export" files
        "spectrum_text": saved_extra.get("spectrum_text", ""),
        "powercepstrum_text": saved_extra.get("powercepstrum_text", ""),
        "lpc_spectrum_text": saved_extra.get("lpc_spectrum_text", ""),
    }

    for k, v in vq.items():
        row[k] = float(v)

    for k, v in praatstyle.items():
        row[k] = float(v)

    # TSV fields
    fieldnames: List[str] = [
        # meta
        "wav", "textgrid", "tier_name", "label",
        "xmin_abs", "xmax_abs", "dur_abs", "dur_local",
        "spectrum_text", "powercepstrum_text", "lpc_spectrum_text",

        # Voice quality
        "f0_min_hz", "f0_max_hz", "f0_mean_hz", "f0_sd_hz", "hnr_mean_db",
        "locally_unvoiced_percent", "voice_breaks_count", "voice_breaks_percent",
        "jitter_local", "jitter_local_abs", "jitter_rap", "jitter_ppq5", "jitter_ddp",
        "shimmer_local", "shimmer_local_db", "shimmer_apq3", "shimmer_apq5", "shimmer_apq11", "shimmer_dda",
        "f1_mean_hz", "f2_mean_hz", "f3_mean_hz", "f4_mean_hz",
        "f1_mid_hz", "f2_mid_hz", "f3_mid_hz", "f4_mid_hz",
        "h1_db", "h2_db", "h4_db", "a2k_db", "a5k_db",

        # Praat-export-like summary
        "t_start", "t_end", "t_mid",
        "f0_mid_hz",
        "f1_mid_hz", "f2_mid_hz", "f3_mid_hz", "f4_mid_hz",
        "b1_mid_hz", "b2_mid_hz", "b3_mid_hz", "b4_mid_hz",
        "f1_mean_hz_praatstyle", "f2_mean_hz_praatstyle", "f3_mean_hz_praatstyle", "f4_mean_hz_praatstyle",
        "b1_mean_hz_praatstyle", "b2_mean_hz_praatstyle", "b3_mean_hz_praatstyle", "b4_mean_hz_praatstyle",
        "h1_freq_hz_target", "a1_freq_hz_target", "a2_freq_hz_target", "a3_freq_hz_target", "a4_freq_hz_target",
        "int_mid_db_praatstyle", "int_mean_db_praatstyle",
    ]

    for fn in fieldnames:
        if fn not in row:
            row[fn] = "" if fn.endswith("_text") or fn in {"wav", "textgrid", "tier_name", "label"} else float("nan")

    with open(out_tsv, "w", encoding="utf-8", newline="") as f:
        f.write("\t".join(fieldnames) + "\n")
        vals: List[str] = []
        for fn in fieldnames:
            v = row[fn]
            if isinstance(v, str):
                vals.append(v)
            else:
                vals.append(fmt(float(v)))
        f.write("\t".join(vals) + "\n")

    # Cleanup
    for obj in (spectrum_seg, harmonicity_obj, intensity_obj, point_process, pitch_obj, seg, tg, sound):
        try:
            call(obj, "Remove")
        except Exception:
            pass

    print("OK")
    print(f"  TextGrid: {tg_path}")
    print(f"  Segment abs: start={seg_start:.6f}s end={seg_end:.6f}s dur={(seg_end-seg_start):.6f}s label='{args.label}'")
    print(f"  Objects: {out_dir / f'{basename}.Pitch'} etc.")
    print(f"  TSV: {out_tsv}")
    if saved_extra.get("spectrum_text"):
        print(f"  Spectrum: {saved_extra['spectrum_text']}")
    if saved_extra.get("powercepstrum_text"):
        print(f"  PowerCepstrum: {saved_extra['powercepstrum_text']}")
    if saved_extra.get("lpc_spectrum_text"):
        print(f"  LPCSpectrum: {saved_extra['lpc_spectrum_text']}")


if __name__ == "__main__":
    main()
