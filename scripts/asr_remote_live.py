#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

import numpy as np
from faster_whisper import WhisperModel


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def normalize_language(lang: str | None) -> Optional[str]:
    if lang is None:
        return None
    lang = lang.strip().lower()
    if lang in {"auto", ""}:
        return None
    if lang in {"es", "spanish", "castilian"}:
        return "es"
    if lang in {"ca", "catalan", "català"}:
        return "ca"
    raise ValueError(f"Unsupported language value: {lang}")



class BasicASR:
    def __init__(
        self,
        model_size: str = "small",
        device="cuda",
        compute_type="int8",
        beam_size: int = 3,
        vad_filter: bool = True,
        word_timestamps: bool = False,
    ):
        eprint(
            f"Loading model={model_size} device={device} compute_type={compute_type}"
        )
        self.model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type,
        )
        self.beam_size = beam_size
        self.vad_filter = vad_filter
        self.word_timestamps = word_timestamps

    def transcribe_array(self, audio_float32: np.ndarray, sample_rate: int, language: Optional[str]) -> str:
        audio_float32 = np.asarray(audio_float32, dtype=np.float32)

        segments, info = self.model.transcribe(
            audio_float32,
            language=language,
            beam_size=self.beam_size,
            vad_filter=self.vad_filter,
            vad_parameters=dict(
                min_silence_duration_ms=1000,
                speech_pad_ms=200,
            ),
            word_timestamps=self.word_timestamps,
            condition_on_previous_text=False,
            task="transcribe",
        )

        text = " ".join(seg.text.strip() for seg in segments if seg.text.strip()).strip()
        return text


def main():
    parser = argparse.ArgumentParser(description="Remote live ASR from stdin PCM")
    parser.add_argument("--model", default="small")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--compute-type", default="int8")
    parser.add_argument("--beam-size", type=int, default=5)
    parser.add_argument("--language", default="auto")
    parser.add_argument("--sample-rate", type=int, default=16000)
    parser.add_argument("--chunk-sec", type=float, default=3.5, help="How often to decode")
    args = parser.parse_args()

    language = normalize_language(args.language)

    asr = BasicASR(
        model_size=args.model,
        device=args.device,
        compute_type=args.compute_type,
        beam_size=args.beam_size,
        vad_filter=True,
        word_timestamps=False,
    )

    bytes_per_sample = 2  # int16 mono
    samples_per_chunk = int(args.chunk_sec * args.sample_rate)

    raw_buffer = bytearray()
    chunk_buffer = np.zeros(0, dtype=np.float32)

    eprint("Waiting for audio from stdin... Press Ctrl+C to stop.")

    try:
        while True:
            data = sys.stdin.buffer.read(4096)
            if not data:
                break

            raw_buffer.extend(data)

            usable = (len(raw_buffer) // bytes_per_sample) * bytes_per_sample
            if usable == 0:
                continue

            chunk = np.frombuffer(raw_buffer[:usable], dtype=np.int16).astype(np.float32) / 32768.0
            del raw_buffer[:usable]

            chunk_buffer = np.concatenate([chunk_buffer, chunk])

            while len(chunk_buffer) >= samples_per_chunk:
                current = chunk_buffer[:samples_per_chunk]
                chunk_buffer = chunk_buffer[samples_per_chunk:]

                text = asr.transcribe_array(current, args.sample_rate, language)
                text = text.strip()

                if text:
                    print(f"[chunk] {text}", flush=True)

    except KeyboardInterrupt:
        eprint("\nStopped.")


if __name__ == "__main__":
    main()