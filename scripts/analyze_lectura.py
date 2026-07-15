#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import parselmouth


TIME_STEP = 0.01

MIN_SPEECH_INTERVAL = 0.12
MIN_PAUSE_INTERVAL = 0.10
LONG_PAUSE_THRESHOLD = 1.0
DROP_TINY_SPEECH = 0.05

PITCH_FLOOR = 75
PITCH_CEILING = 500

MIN_SYLLABLE_DISTANCE = 0.10
MIN_SYLLABLE_DIP_DB = 2.0
SYLLABLE_INTENSITY_MARGIN_DB = 2.0


@dataclass
class Interval:
    start: float
    end: float

    @property
    def dur(self) -> float:
        return self.end - self.start


def merge_intervals(intervals: list[Interval], max_gap: float = 0.0) -> list[Interval]:
    if not intervals:
        return []

    intervals = sorted(intervals, key=lambda x: x.start)
    out = [Interval(intervals[0].start, intervals[0].end)]

    for it in intervals[1:]:
        last = out[-1]
        if it.start <= last.end + max_gap:
            out[-1] = Interval(last.start, max(last.end, it.end))
        else:
            out.append(Interval(it.start, it.end))
    return out


def invert_intervals(intervals: list[Interval], start: float, end: float) -> list[Interval]:
    if not intervals:
        return [Interval(start, end)] if end > start else []

    out: list[Interval] = []
    cur = start
    for it in intervals:
        if it.start > cur:
            out.append(Interval(cur, it.start))
        cur = max(cur, it.end)
    if cur < end:
        out.append(Interval(cur, end))
    return out


def trim_by_duration(intervals: list[Interval], min_dur: float) -> list[Interval]:
    return [it for it in intervals if it.dur >= min_dur]


def extract_values_in_interval(times: np.ndarray, values: np.ndarray, start: float, end: float) -> np.ndarray:
    mask = (times >= start) & (times <= end)
    return values[mask]


def robust_speech_threshold_db(intensity_values: np.ndarray) -> float:
    finite = intensity_values[np.isfinite(intensity_values)]
    if len(finite) == 0:
        return 0.0
    p95 = np.percentile(finite, 95)
    p20 = np.percentile(finite, 20)
    return max(p20 + 0.25 * (p95 - p20), p95 - 25.0)


def speech_intervals_from_audio(sound: parselmouth.Sound):
    total_duration = sound.get_total_duration()

    intensity = sound.to_intensity(time_step=TIME_STEP)
    intensity_values = intensity.values[0]
    intensity_times = intensity.xs()

    pitch = sound.to_pitch(time_step=TIME_STEP, pitch_floor=PITCH_FLOOR, pitch_ceiling=PITCH_CEILING)
    f0 = pitch.selected_array["frequency"]
    pitch_times = pitch.xs()

    n = min(len(intensity_values), len(f0), len(intensity_times), len(pitch_times))
    intensity_values = intensity_values[:n]
    intensity_times = intensity_times[:n]
    f0 = f0[:n]

    thr_db = robust_speech_threshold_db(intensity_values)
    speech_mask = (intensity_values >= thr_db) & ((f0 > 0) | (intensity_values >= thr_db + 3))

    intervals: list[Interval] = []
    in_run = False
    start_t = None

    for i, flag in enumerate(speech_mask):
        t = intensity_times[i]
        if flag and not in_run:
            in_run = True
            start_t = t - TIME_STEP / 2
        elif not flag and in_run:
            end_t = t + TIME_STEP / 2
            intervals.append(Interval(max(0.0, start_t), min(total_duration, end_t)))
            in_run = False
            start_t = None

    if in_run and start_t is not None:
        intervals.append(Interval(max(0.0, start_t), total_duration))

    intervals = trim_by_duration(intervals, DROP_TINY_SPEECH)
    intervals = merge_intervals(intervals, max_gap=0.04)
    intervals = trim_by_duration(intervals, MIN_SPEECH_INTERVAL)

    return intervals, intensity, pitch


def get_voice_span(speech_intervals: list[Interval]) -> Interval | None:
    if not speech_intervals:
        return None
    return Interval(speech_intervals[0].start, speech_intervals[-1].end)


def get_internal_pauses(speech_intervals: list[Interval], voice_span: Interval) -> list[Interval]:
    pauses = invert_intervals(speech_intervals, voice_span.start, voice_span.end)
    return trim_by_duration(pauses, MIN_PAUSE_INTERVAL)


def estimate_syllable_nuclei(
    intensity: parselmouth.Intensity,
    pitch: parselmouth.Pitch,
    voice_span: Interval,
) -> list[float]:
    intensity_values = intensity.values[0]
    intensity_times = intensity.xs()
    f0 = pitch.selected_array["frequency"]

    n = min(len(intensity_values), len(f0), len(intensity_times))
    intensity_values = intensity_values[:n]
    intensity_times = intensity_times[:n]
    f0 = f0[:n]

    mask = (intensity_times >= voice_span.start) & (intensity_times <= voice_span.end)
    times = intensity_times[mask]
    vals = intensity_values[mask]
    voiced = f0[mask] > 0

    if len(times) < 3:
        return []

    thr_db = robust_speech_threshold_db(vals) + SYLLABLE_INTENSITY_MARGIN_DB
    peaks = []
    last_peak_time = -999.0

    for i in range(1, len(vals) - 1):
        if not voiced[i]:
            continue
        if vals[i] < thr_db:
            continue
        if not (vals[i] > vals[i - 1] and vals[i] >= vals[i + 1]):
            continue

        left_min = np.min(vals[max(0, i - 3):i + 1])
        right_min = np.min(vals[i:min(len(vals), i + 4)])
        dip = vals[i] - max(left_min, right_min)

        if dip < MIN_SYLLABLE_DIP_DB:
            continue

        t = times[i]
        if t - last_peak_time < MIN_SYLLABLE_DISTANCE:
            if peaks and vals[i] > peaks[-1][1]:
                peaks[-1] = (t, vals[i])
                last_peak_time = t
            continue

        peaks.append((t, vals[i]))
        last_peak_time = t

    return [t for t, _ in peaks]


def interval_f0_stats(pitch: parselmouth.Pitch, interval: Interval):
    f0 = pitch.selected_array["frequency"]
    times = pitch.xs()
    vals = extract_values_in_interval(times, f0, interval.start, interval.end)
    voiced = vals[vals > 0]
    if len(voiced) == 0:
        return None, None, None
    return float(np.mean(voiced)), float(np.std(voiced)), float(np.max(voiced) - np.min(voiced))


def write_summary_csv(path: Path, row: dict):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        writer.writeheader()
        writer.writerow(row)


def analyze_audio(audio_path: Path):
    sound = parselmouth.Sound(str(audio_path))
    speech_intervals, intensity, pitch = speech_intervals_from_audio(sound)

    if not speech_intervals:
        raise RuntimeError("No se detectó habla suficiente en el audio.")

    voice_span = get_voice_span(speech_intervals)
    assert voice_span is not None

    pauses = get_internal_pauses(speech_intervals, voice_span)
    pause_time = sum(p.dur for p in pauses)

    total_duration = voice_span.dur
    articulation_time = max(total_duration - pause_time, 1e-9)

    syllable_nuclei = estimate_syllable_nuclei(intensity, pitch, voice_span)
    syllable_count = len(syllable_nuclei)

    speech_rate = syllable_count / total_duration if total_duration > 0 else 0.0
    articulation_rate = syllable_count / articulation_time if articulation_time > 0 else 0.0

    pause_count = len(pauses)
    mean_pause_duration = pause_time / pause_count if pause_count > 0 else 0.0
    pause_percentage = (pause_time / total_duration) * 100 if total_duration > 0 else 0.0
    long_pauses = sum(p.dur > LONG_PAUSE_THRESHOLD for p in pauses)

    f0_mean, f0_sd, f0_range = interval_f0_stats(pitch, voice_span)
    f0_mean = 0.0 if f0_mean is None else f0_mean
    f0_sd = 0.0 if f0_sd is None else f0_sd
    f0_range = 0.0 if f0_range is None else f0_range

    summary = {
        "total_duration": round(total_duration, 4),
        "speech_rate": round(speech_rate, 4),
        "articulation_rate": round(articulation_rate, 4),
        "pause_count": int(pause_count),
        "mean_pause_duration": round(mean_pause_duration, 4),
        "pause_percentage": round(pause_percentage, 4),
        "long_pauses": int(long_pauses),
        "f0_mean": round(f0_mean, 4),
        "f0_sd": round(f0_sd, 4),
        "f0_range": round(f0_range, 4),
        "syllable_nuclei_estimated": int(syllable_count),
        "speech_intervals": int(len(speech_intervals)),
        "voice_start": round(voice_span.start, 4),
        "voice_end": round(voice_span.end, 4),
    }

    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio", required=True, help="Ruta al wav")
    parser.add_argument("--out-csv", required=True, help="CSV resumen")
    args = parser.parse_args()

    audio_path = Path(args.audio)
    out_csv = Path(args.out_csv)

    summary = analyze_audio(audio_path)
    write_summary_csv(out_csv, summary)

    print(f"Resumen guardado en: {out_csv}")


if __name__ == "__main__":
    main()