#!/usr/bin/env python3
import sys, time, argparse
import numpy as np
import parselmouth
from scipy.signal import find_peaks

def robust_median(x):
    x = x[np.isfinite(x)]
    return float(np.median(x)) if x.size else np.nan

def robust_mean(x):
    x = x[np.isfinite(x)]
    return float(np.mean(x)) if x.size else np.nan

def compute_f0_intensity(sound, time_step=0.01, pitch_floor=75, pitch_ceiling=500):
    pitch = sound.to_pitch(time_step=time_step, pitch_floor=pitch_floor, pitch_ceiling=pitch_ceiling)
    f0 = pitch.selected_array["frequency"]
    f0 = f0[f0 > 0]
    f0_med = robust_median(f0)

    intensity = sound.to_intensity(time_step=time_step, minimum_pitch=pitch_floor)
    inten_vals = intensity.values[0]
    inten_mean = robust_mean(inten_vals)
    return f0_med, inten_mean, inten_vals

def estimate_rate(intensity_vals, time_step, min_peak_distance_s=0.09, prominence_db=2.5):
    x = intensity_vals.astype(np.float32)
    x = x[np.isfinite(x)]
    if x.size < 5:
        return np.nan
    win_s = 0.05
    win = max(3, int(win_s / time_step))
    xs = np.convolve(x, np.ones(win, dtype=np.float32)/win, mode="same")
    med = np.median(xs)
    thr = med + 1.5
    min_dist = max(1, int(min_peak_distance_s / time_step))
    peaks, _ = find_peaks(xs, height=thr, distance=min_dist, prominence=prominence_db)
    dur_s = len(xs) * time_step
    return float(len(peaks) / dur_s) if dur_s > 0 else np.nan

def arrow(delta_pct, deadband=3.0):
    if not np.isfinite(delta_pct): return "—"
    if abs(delta_pct) < deadband: return "≈"
    return "↑" if delta_pct > 0 else "↓"

def fmt(x, unit="", digits=1):
    return "—" if not np.isfinite(x) else f"{x:.{digits}f}{unit}"

class Ring:
    def __init__(self, maxlen):
        self.buf = np.zeros(maxlen, dtype=np.float32)
        self.maxlen = maxlen
        self.w = 0
        self.filled = 0
    def push(self, x):
        x = np.asarray(x, dtype=np.float32)
        n = x.size
        if n >= self.maxlen:
            self.buf[:] = x[-self.maxlen:]
            self.w = 0
            self.filled = self.maxlen
            return
        end = self.w + n
        if end <= self.maxlen:
            self.buf[self.w:end] = x
        else:
            k = self.maxlen - self.w
            self.buf[self.w:] = x[:k]
            self.buf[:end % self.maxlen] = x[k:]
        self.w = (self.w + n) % self.maxlen
        self.filled = min(self.maxlen, self.filled + n)
    def last(self, n):
        n = int(n)
        if self.filled < n:
            return None
        start = (self.w - n) % self.maxlen
        if start < self.w:
            return self.buf[start:self.w].copy()
        return np.concatenate([self.buf[start:], self.buf[:self.w]]).copy()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sr", type=int, default=16000)
    ap.add_argument("--window", type=float, default=2.0)
    ap.add_argument("--update", type=float, default=0.5)
    ap.add_argument("--calib", type=float, default=4.0)
    ap.add_argument("--time_step", type=float, default=0.01)
    args = ap.parse_args()

    sr = args.sr
    window_n = int(args.window * sr)
    update_n = int(args.update * sr)
    calib_n  = int(args.calib  * sr)

    ring = Ring(maxlen=int((args.window + 2.0) * sr))
    stdin = sys.stdin.buffer

    print(f"Recibiendo audio por stdin: {sr} Hz, mono, s16le.", flush=True)
    print(f"Baseline: primeros {args.calib:.1f}s (habla normal). Luego continuo.\n", flush=True)

    bytes_per_sample = 2  # s16le
    chunk_n = int(0.1 * sr)
    chunk_bytes = chunk_n * bytes_per_sample

    got = 0
    while got < calib_n:
        b = stdin.read(chunk_bytes)
        if not b:
            print("No llega audio (stdin vacío).", flush=True)
            return
        x = np.frombuffer(b, dtype=np.int16).astype(np.float32) / 32768.0
        ring.push(x)
        got += x.size

    calib = ring.last(calib_n)
    sound = parselmouth.Sound(calib, sr)

    pitch_floor, pitch_ceiling = 75, 500
    f0_c, inten_c, inten_vals_c = compute_f0_intensity(sound, time_step=args.time_step,
                                                       pitch_floor=pitch_floor, pitch_ceiling=pitch_ceiling)
    if np.isfinite(f0_c) and f0_c > 0:
        pitch_floor = max(50, f0_c * 0.55)
        pitch_ceiling = min(800, f0_c * 2.2)
        f0_c, inten_c, inten_vals_c = compute_f0_intensity(sound, time_step=args.time_step,
                                                           pitch_floor=pitch_floor, pitch_ceiling=pitch_ceiling)
    rate_c = estimate_rate(inten_vals_c, time_step=args.time_step)

    print("=== Baseline ===", flush=True)
    print(f"F0 baseline:        {fmt(f0_c,' Hz',1)}", flush=True)
    print(f"Intensidad baseline:{fmt(inten_c,' dB',1)}", flush=True)
    print(f"Ritmo baseline:     {fmt(rate_c,' p/s',2)}", flush=True)
    print(f"Pitch floor/ceiling:{pitch_floor:.0f}/{pitch_ceiling:.0f} Hz\n", flush=True)

    t0 = time.time()
    since = 0

    def delta_pct(cur, base):
        if not (np.isfinite(cur) and np.isfinite(base) and base != 0):
            return np.nan
        return 100.0 * (cur - base) / base

    while True:
        b = stdin.read(chunk_bytes)
        if not b:
            break
        x = np.frombuffer(b, dtype=np.int16).astype(np.float32) / 32768.0
        ring.push(x)
        since += x.size

        if since >= update_n:
            since = 0
            w = ring.last(window_n)
            if w is None:
                continue
            s = parselmouth.Sound(w, sr)
            f0, inten, inten_vals = compute_f0_intensity(s, time_step=args.time_step,
                                                         pitch_floor=pitch_floor, pitch_ceiling=pitch_ceiling)
            rate = estimate_rate(inten_vals, time_step=args.time_step)

            df0 = delta_pct(f0, f0_c)
            dint = delta_pct(inten, inten_c)
            drate = delta_pct(rate, rate_c)

            ts = time.time() - t0
            print(
                f"[{ts:6.1f}s] "
                f"F0 {fmt(f0,' Hz',1):>10} {arrow(df0)} ({fmt(df0,'%',0)}) | "
                f"Int {fmt(inten,' dB',1):>10} {arrow(dint)} ({fmt(dint,'%',0)}) | "
                f"Rit {fmt(rate,' p/s',2):>10} {arrow(drate)} ({fmt(drate,'%',0)})",
                flush=True
            )

if __name__ == "__main__":
    main()
